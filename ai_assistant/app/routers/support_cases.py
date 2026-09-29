"""
Support Cases API endpoints for recording and managing customer issues.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query
from typing import Optional
from sqlalchemy import text
from datetime import datetime, timezone
import asyncio
import httpx
import logging
import uuid
import json

from ..config import settings
from ..database import get_db_session
from ..schemas_support_cases import (
    CreateSupportCaseRequest,
    UpdateSupportCaseRequest,
    ResolveSupportCaseRequest,
    AddCommentRequest,
    SupportCaseResponse,
    SupportCaseCommentResponse,
    SupportCaseListResponse,
    SupportCaseStatsResponse,
    SupportCaseStatusEnum,
    SupportCasePriorityEnum,
)
from ..services.support_case_notifications import get_user_context, notify_case_event

logger = logging.getLogger(__name__)


def _generate_case_number() -> str:
    """Generate a unique case number like SC-20260630-XXXX."""
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:4].upper()
    return f"SC-{date_part}-{random_part}"


def _parse_jsonb_list(value) -> list:
    """Safely parse a JSONB value that should be a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return []  # empty JSONB object stored instead of array
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


async def _current_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Resolve the ABParts user behind the request's bearer token, or None."""
    if not authorization:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ABPARTS_API_URL}/users/me/",
                                    headers={"Authorization": authorization})
        if resp.status_code == 200:
            return str(resp.json().get("id"))
        logger.warning(f"Could not identify support case user: /users/me/ returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Could not identify support case user: {e}")
    return None


async def require_support_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Support cases are the Oraseas/BossServ support log: only their active
    admins may read or change them.
    """
    user_id = await _current_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_user_context(user_id)
    if (not user or not user["is_active"] or not user["side"]
            or user["role"] not in ("admin", "super_admin")):
        raise HTTPException(status_code=403, detail="Support cases are limited to Oraseas and BossServ admins")
    return user


router = APIRouter(dependencies=[Depends(require_support_user)])


def _to_utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    """Store datetimes as naive UTC, matching the TIMESTAMP columns."""
    if value is not None and value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _utc(value: Optional[datetime]) -> Optional[datetime]:
    """Mark naive UTC timestamps from the database as UTC so browsers show local time."""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


# Case columns plus the display names of the users who recorded / resolved it
_CASE_WITH_NAMES_SQL = """
    SELECT sc.*,
           COALESCE(cu.name, cu.username) AS created_by_name,
           COALESCE(ru.name, ru.username) AS resolved_by_name
    FROM support_cases sc
    LEFT JOIN users cu ON cu.id::text = sc.created_by
    LEFT JOIN users ru ON ru.id::text = sc.resolved_by
    WHERE sc.id = :id
"""


def _row_to_case_response(row, comments=None) -> SupportCaseResponse:
    """Convert a database row to a SupportCaseResponse."""
    return SupportCaseResponse(
        id=row.id,
        case_number=row.case_number,
        title=row.title,
        description=row.description,
        machine_model=row.machine_model,
        machine_id=row.machine_id,
        symptoms=row.symptoms,
        root_cause=row.root_cause,
        resolution=row.resolution,
        status=row.status,
        priority=row.priority,
        organization_id=row.organization_id,
        contacted_at=_utc(getattr(row, 'contacted_at', None)),
        contact_channel=getattr(row, 'contact_channel', None),
        created_by=row.created_by,
        created_by_name=getattr(row, 'created_by_name', None),
        resolved_by=getattr(row, 'resolved_by', None),
        resolved_by_name=getattr(row, 'resolved_by_name', None),
        assigned_to=row.assigned_to,
        tags=_parse_jsonb_list(row.tags),
        related_parts=_parse_jsonb_list(row.related_parts),
        internal_notes=row.internal_notes,
        knowledge_doc_id=row.knowledge_doc_id,
        session_id=row.session_id,
        created_at=_utc(row.created_at),
        updated_at=_utc(row.updated_at),
        resolved_at=_utc(row.resolved_at),
        closed_at=_utc(row.closed_at),
        comments=comments or [],
    )


@router.post("/support-cases", response_model=SupportCaseResponse)
async def create_support_case(
    request: CreateSupportCaseRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_support_user),
):
    """
    Create a new support case. If a resolution is supplied the case is recorded
    as already resolved. The other side (Oraseas <-> BossServ) is emailed.
    """
    case_id = str(uuid.uuid4())
    case_number = _generate_case_number()
    user_id = user["id"]
    resolved = bool(request.resolution and request.resolution.strip())

    try:
        with get_db_session() as db:
            db.execute(text("""
                INSERT INTO support_cases 
                (id, case_number, title, description, machine_model, machine_id,
                 symptoms, root_cause, resolution, status, priority, organization_id,
                 contacted_at, contact_channel, created_by, assigned_to,
                 tags, related_parts, session_id, created_at, updated_at,
                 resolved_at, resolved_by)
                VALUES (:id, :case_number, :title, :description, :machine_model, :machine_id,
                        :symptoms, :root_cause, :resolution, :status, :priority, :organization_id,
                        COALESCE(:contacted_at, NOW()), :contact_channel, :created_by, :assigned_to,
                        :tags, :related_parts, :session_id, NOW(), NOW(),
                        CASE WHEN :resolved THEN NOW() END, :resolved_by)
            """), {
                'id': case_id,
                'case_number': case_number,
                'title': request.title,
                'description': request.description,
                'machine_model': request.machine_model,
                'machine_id': request.machine_id,
                'symptoms': request.symptoms,
                'root_cause': request.root_cause or None,
                'resolution': request.resolution if resolved else None,
                'status': 'resolved' if resolved else 'open',
                'priority': request.priority.value,
                'organization_id': request.organization_id,
                'contacted_at': _to_utc_naive(request.contacted_at),
                'contact_channel': request.contact_channel or None,
                'created_by': user_id,
                'assigned_to': request.assigned_to,
                'tags': json.dumps(request.tags if request.tags else []),
                'related_parts': json.dumps(request.related_parts if request.related_parts else []),
                'session_id': request.session_id,
                'resolved': resolved,
                'resolved_by': user_id if resolved else None,
            })

            # Fetch the created case
            result = db.execute(
                text("SELECT * FROM support_cases WHERE id = :id"),
                {'id': case_id}
            ).fetchone()

        if resolved:
            try:
                doc_id = await _sync_case_to_knowledge_base(result)
                if doc_id:
                    with get_db_session() as db:
                        db.execute(
                            text("UPDATE support_cases SET knowledge_doc_id = :d WHERE id = :id"),
                            {'d': doc_id, 'id': case_id}
                        )
            except Exception as e:
                logger.warning(f"Failed to publish new resolved case {case_id} to knowledge base: {e}")

        with get_db_session() as db:
            result = db.execute(text(_CASE_WITH_NAMES_SQL), {'id': case_id}).fetchone()

        background_tasks.add_task(notify_case_event, case_id, 'created', user_id)

        logger.info(f"Created support case {case_number} (id: {case_id})")
        return _row_to_case_response(result)

    except Exception as e:
        logger.error(f"Failed to create support case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create support case: {str(e)}")


@router.get("/support-cases", response_model=SupportCaseListResponse)
async def list_support_cases(
    status: Optional[SupportCaseStatusEnum] = Query(None),
    priority: Optional[SupportCasePriorityEnum] = Query(None),
    machine_model: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List support cases with filtering and pagination.
    """
    try:
        conditions = []
        params = {'limit': limit, 'offset': offset}

        if status:
            conditions.append("status = :status")
            params['status'] = status.value
        if priority:
            conditions.append("priority = :priority")
            params['priority'] = priority.value
        if machine_model:
            conditions.append("machine_model = :machine_model")
            params['machine_model'] = machine_model
        if organization_id:
            conditions.append("organization_id = :organization_id")
            params['organization_id'] = organization_id
        if assigned_to:
            conditions.append("assigned_to = :assigned_to")
            params['assigned_to'] = assigned_to
        if created_by:
            conditions.append("created_by = :created_by")
            params['created_by'] = created_by
        if search:
            conditions.append(
                "(title ILIKE :search OR description ILIKE :search OR symptoms ILIKE :search)"
            )
            params['search'] = f"%{search}%"

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with get_db_session() as db:
            # Get total count
            count_result = db.execute(
                text(f"SELECT COUNT(*) FROM support_cases WHERE {where_clause}"),
                params
            ).scalar()

            # Get paginated results
            results = db.execute(
                text(f"""
                    SELECT * FROM support_cases 
                    WHERE {where_clause}
                    ORDER BY 
                        CASE priority
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                params
            ).fetchall()

        cases = [_row_to_case_response(row) for row in results]
        return SupportCaseListResponse(
            cases=cases,
            total=count_result,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(f"Failed to list support cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list support cases: {str(e)}")


@router.get("/support-cases/stats", response_model=SupportCaseStatsResponse)
async def get_support_case_stats():
    """
    Get support case statistics.
    """
    try:
        with get_db_session() as db:
            # Status counts
            status_counts = db.execute(text("""
                SELECT status, COUNT(*) as count FROM support_cases GROUP BY status
            """)).fetchall()

            status_map = {row.status: row.count for row in status_counts}

            # Cases by machine model
            model_counts = db.execute(text("""
                SELECT COALESCE(machine_model, 'Unknown') as model, COUNT(*) as count 
                FROM support_cases GROUP BY machine_model
            """)).fetchall()

            # Cases by priority
            priority_counts = db.execute(text("""
                SELECT priority, COUNT(*) as count FROM support_cases GROUP BY priority
            """)).fetchall()

            # Average resolution time
            avg_resolution = db.execute(text("""
                SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600) as avg_hours
                FROM support_cases WHERE resolved_at IS NOT NULL
            """)).scalar()

        total = sum(status_map.values()) if status_map else 0

        return SupportCaseStatsResponse(
            total_cases=total,
            open_cases=status_map.get('open', 0),
            investigating_cases=status_map.get('investigating', 0),
            waiting_cases=status_map.get('waiting_on_customer', 0),
            resolved_cases=status_map.get('resolved', 0),
            closed_cases=status_map.get('closed', 0),
            avg_resolution_time_hours=round(avg_resolution, 1) if avg_resolution else None,
            cases_by_machine_model={row.model: row.count for row in model_counts},
            cases_by_priority={row.priority: row.count for row in priority_counts},
        )

    except Exception as e:
        logger.error(f"Failed to get support case stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/support-cases/{case_id}", response_model=SupportCaseResponse)
async def get_support_case(case_id: str):
    """
    Get a specific support case by ID with comments.
    """
    try:
        with get_db_session() as db:
            result = db.execute(text(_CASE_WITH_NAMES_SQL), {'id': case_id}).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Support case not found")

            # Get comments
            comments_rows = db.execute(
                text("""
                    SELECT * FROM support_case_comments 
                    WHERE case_id = :case_id ORDER BY created_at ASC
                """),
                {'case_id': case_id}
            ).fetchall()

        comments = [
            SupportCaseCommentResponse(
                id=c.id,
                case_id=c.case_id,
                author_id=c.author_id,
                content=c.content,
                is_internal=c.is_internal,
                created_at=_utc(c.created_at),
            )
            for c in comments_rows
        ]

        return _row_to_case_response(result, comments)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get support case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get support case: {str(e)}")


@router.put("/support-cases/{case_id}", response_model=SupportCaseResponse)
async def update_support_case(
    case_id: str,
    request: UpdateSupportCaseRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_support_user),
):
    """
    Update a support case. Moving it to resolved emails the other side.
    """
    try:
        set_clauses = ["updated_at = NOW()"]
        params = {'case_id': case_id}
        user_id = None

        if request.title is not None:
            set_clauses.append("title = :title")
            params['title'] = request.title
        if request.description is not None:
            set_clauses.append("description = :description")
            params['description'] = request.description
        if request.machine_model is not None:
            set_clauses.append("machine_model = :machine_model")
            params['machine_model'] = request.machine_model
        if request.machine_id is not None:
            set_clauses.append("machine_id = :machine_id")
            params['machine_id'] = request.machine_id
        if request.symptoms is not None:
            set_clauses.append("symptoms = :symptoms")
            params['symptoms'] = request.symptoms
        if request.contacted_at is not None:
            set_clauses.append("contacted_at = :contacted_at")
            params['contacted_at'] = _to_utc_naive(request.contacted_at)
        if request.contact_channel is not None:
            set_clauses.append("contact_channel = :contact_channel")
            params['contact_channel'] = request.contact_channel or None
        if request.root_cause is not None:
            set_clauses.append("root_cause = :root_cause")
            params['root_cause'] = request.root_cause
        if request.resolution is not None:
            set_clauses.append("resolution = :resolution")
            params['resolution'] = request.resolution
        if request.status is not None:
            set_clauses.append("status = :status")
            params['status'] = request.status.value
            if request.status == SupportCaseStatusEnum.resolved:
                set_clauses.append("resolved_at = NOW()")
                user_id = user["id"]
                set_clauses.append("resolved_by = :resolved_by")
                params['resolved_by'] = user_id
            elif request.status == SupportCaseStatusEnum.closed:
                set_clauses.append("closed_at = NOW()")
        if request.priority is not None:
            set_clauses.append("priority = :priority")
            params['priority'] = request.priority.value
        if request.assigned_to is not None:
            set_clauses.append("assigned_to = :assigned_to")
            params['assigned_to'] = request.assigned_to
        if request.tags is not None:
            set_clauses.append("tags = :tags")
            params['tags'] = json.dumps(request.tags)
        if request.related_parts is not None:
            set_clauses.append("related_parts = :related_parts")
            params['related_parts'] = json.dumps(request.related_parts)
        if request.internal_notes is not None:
            set_clauses.append("internal_notes = :internal_notes")
            params['internal_notes'] = request.internal_notes

        with get_db_session() as db:
            previous_status = db.execute(
                text("SELECT status FROM support_cases WHERE id = :case_id"), {'case_id': case_id}
            ).scalar()

            result = db.execute(
                text(f"UPDATE support_cases SET {', '.join(set_clauses)} WHERE id = :case_id RETURNING *"),
                params
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Support case not found")

        if result.status == 'resolved' and previous_status != 'resolved':
            background_tasks.add_task(notify_case_event, case_id, 'resolved', user_id)

        # Keep the knowledge base in sync when a resolved/closed case's content changes
        kb_relevant = ('title', 'description', 'symptoms', 'root_cause',
                       'resolution', 'machine_model', 'related_parts', 'tags', 'status')
        if (result.status in ('resolved', 'closed') and result.resolution
                and any(getattr(request, f, None) is not None for f in kb_relevant)):
            try:
                doc_id = await _sync_case_to_knowledge_base(result)
                if doc_id and doc_id != result.knowledge_doc_id:
                    with get_db_session() as db:
                        db.execute(
                            text("UPDATE support_cases SET knowledge_doc_id = :d WHERE id = :id"),
                            {'d': doc_id, 'id': case_id}
                        )
                        result = db.execute(
                            text("SELECT * FROM support_cases WHERE id = :id"), {'id': case_id}
                        ).fetchone()
            except Exception as e:
                logger.warning(f"Failed to re-sync case {case_id} to knowledge base: {e}")

        logger.info(f"Updated support case {case_id}")
        return _row_to_case_response(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update support case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update support case: {str(e)}")


@router.post("/support-cases/{case_id}/resolve", response_model=SupportCaseResponse)
async def resolve_support_case(
    case_id: str,
    request: ResolveSupportCaseRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_support_user),
):
    """
    Resolve a support case, optionally publish to knowledge base, and email the other side.
    """
    user_id = user["id"]
    try:
        with get_db_session() as db:
            previous_status = db.execute(
                text("SELECT status FROM support_cases WHERE id = :case_id"), {'case_id': case_id}
            ).scalar()

            # Update the case
            result = db.execute(
                text("""
                    UPDATE support_cases 
                    SET root_cause = :root_cause,
                        resolution = :resolution,
                        internal_notes = COALESCE(:internal_notes, internal_notes),
                        status = 'resolved',
                        resolved_at = NOW(),
                        resolved_by = :resolved_by,
                        updated_at = NOW()
                    WHERE id = :case_id
                    RETURNING *
                """),
                {
                    'case_id': case_id,
                    'resolved_by': user_id,
                    'root_cause': request.root_cause,
                    'resolution': request.resolution,
                    'internal_notes': request.internal_notes,
                }
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Support case not found")

        # Publish / refresh in the knowledge base if requested
        if request.publish_to_knowledge_base:
            try:
                knowledge_doc_id = await _sync_case_to_knowledge_base(result)
                if knowledge_doc_id and knowledge_doc_id != result.knowledge_doc_id:
                    with get_db_session() as db:
                        db.execute(
                            text("UPDATE support_cases SET knowledge_doc_id = :doc_id WHERE id = :case_id"),
                            {'doc_id': knowledge_doc_id, 'case_id': case_id}
                        )
                    logger.info(f"Published case {case_id} to knowledge base as {knowledge_doc_id}")
            except Exception as e:
                logger.warning(f"Failed to publish case to knowledge base: {e}")
                # Don't fail the resolve operation if KB publish fails

        # Re-fetch with updated knowledge_doc_id
        with get_db_session() as db:
            result = db.execute(text(_CASE_WITH_NAMES_SQL), {'id': case_id}).fetchone()

        if previous_status != 'resolved':
            background_tasks.add_task(notify_case_event, case_id, 'resolved', user_id)

        logger.info(f"Resolved support case {case_id}")
        return _row_to_case_response(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve support case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve support case: {str(e)}")


# Guard against two overlapping backfills writing the vector index at once.
_backfill_lock = asyncio.Lock()


@router.post("/support-cases/backfill-knowledge-base")
async def backfill_knowledge_base(
    dry_run: bool = Query(False, description="List what would be published, change nothing"),
    refresh_existing: bool = Query(False, description="Also refresh cases already linked to a KB doc"),
):
    """
    Publish resolved and closed support cases into the AI knowledge base.

    By default this only touches resolved/closed cases that have a resolution
    but are NOT yet in the knowledge base (no knowledge_doc_id). With
    refresh_existing=true it also re-syncs cases that are already linked,
    picking up later edits.

    Idempotent and safe to re-run. Synchronous admin operation - runtime scales
    with the number of cases processed (a few embedding calls each).
    """
    if _backfill_lock.locked():
        raise HTTPException(status_code=409, detail="A knowledge base backfill is already running")

    async with _backfill_lock:
        kb_filter = "" if refresh_existing else \
            "AND (knowledge_doc_id IS NULL OR btrim(knowledge_doc_id) = '')"

        with get_db_session() as db:
            rows = db.execute(text(f"""
                SELECT * FROM support_cases
                WHERE status IN ('resolved', 'closed')
                  AND resolution IS NOT NULL AND btrim(resolution) <> ''
                  {kb_filter}
                ORDER BY COALESCE(resolved_at, closed_at, updated_at)
            """)).fetchall()

        summary = {
            "eligible": len(rows),
            "published": 0,
            "failed": 0,
            "dry_run": dry_run,
            "refresh_existing": refresh_existing,
            "cases": [],
        }

        if dry_run:
            summary["cases"] = [{"case_number": r.case_number, "title": r.title} for r in rows]
            return summary

        if not rows:
            return summary

        # One shared LLM client + vector index for the whole batch
        from ..llm_client import LLMClient
        from ..services.knowledge_base import KnowledgeBaseService
        from ..services.vector_database import VectorDatabase

        llm_client = LLMClient()
        await llm_client.initialize()
        try:
            kb_service = KnowledgeBaseService(llm_client, VectorDatabase())
            for r in rows:
                try:
                    doc_id = await _sync_case_to_knowledge_base(r, kb_service=kb_service)
                    if not doc_id:
                        summary["failed"] += 1
                        continue
                    if doc_id != r.knowledge_doc_id:
                        with get_db_session() as db:
                            db.execute(text(
                                "UPDATE support_cases SET knowledge_doc_id = :d, updated_at = NOW() "
                                "WHERE id = :id"
                            ), {"d": doc_id, "id": r.id})
                    summary["published"] += 1
                    summary["cases"].append({"case_number": r.case_number, "knowledge_doc_id": doc_id})
                except Exception as e:
                    logger.warning(f"Backfill failed for case {r.case_number}: {e}")
                    summary["failed"] += 1
        finally:
            await llm_client.cleanup()

        logger.info(
            f"Support case KB backfill: {summary['published']} published, "
            f"{summary['failed']} failed (eligible {summary['eligible']})"
        )
        return summary


@router.post("/support-cases/{case_id}/comments", response_model=SupportCaseCommentResponse)
async def add_comment(case_id: str, request: AddCommentRequest):
    """
    Add a comment to a support case.
    """
    comment_id = str(uuid.uuid4())

    try:
        with get_db_session() as db:
            # Verify case exists
            case_exists = db.execute(
                text("SELECT id FROM support_cases WHERE id = :id"),
                {'id': case_id}
            ).fetchone()

            if not case_exists:
                raise HTTPException(status_code=404, detail="Support case not found")

            db.execute(text("""
                INSERT INTO support_case_comments (id, case_id, author_id, content, is_internal, created_at)
                VALUES (:id, :case_id, :author_id, :content, :is_internal, NOW())
            """), {
                'id': comment_id,
                'case_id': case_id,
                'author_id': 'system',  # Will be overridden by auth in production
                'content': request.content,
                'is_internal': request.is_internal,
            })

            # Update case timestamp
            db.execute(
                text("UPDATE support_cases SET updated_at = NOW() WHERE id = :id"),
                {'id': case_id}
            )

            result = db.execute(
                text("SELECT * FROM support_case_comments WHERE id = :id"),
                {'id': comment_id}
            ).fetchone()

        return SupportCaseCommentResponse(
            id=result.id,
            case_id=result.case_id,
            author_id=result.author_id,
            content=result.content,
            is_internal=result.is_internal,
            created_at=_utc(result.created_at),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add comment to case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")


@router.get("/support-cases/{case_id}/comments")
async def list_comments(case_id: str, include_internal: bool = Query(True)):
    """
    List comments for a support case.
    """
    try:
        with get_db_session() as db:
            if include_internal:
                results = db.execute(
                    text("SELECT * FROM support_case_comments WHERE case_id = :case_id ORDER BY created_at ASC"),
                    {'case_id': case_id}
                ).fetchall()
            else:
                results = db.execute(
                    text("SELECT * FROM support_case_comments WHERE case_id = :case_id AND is_internal = false ORDER BY created_at ASC"),
                    {'case_id': case_id}
                ).fetchall()

        return [
            SupportCaseCommentResponse(
                id=c.id,
                case_id=c.case_id,
                author_id=c.author_id,
                content=c.content,
                is_internal=c.is_internal,
                created_at=_utc(c.created_at),
            )
            for c in results
        ]

    except Exception as e:
        logger.error(f"Failed to list comments for case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list comments: {str(e)}")


def _build_case_document_content(case_row) -> str:
    """Render a resolved support case into the text that gets embedded for the AI."""
    parts = [
        f"Issue: {case_row.title}",
        f"\nDescription: {case_row.description}",
    ]
    if case_row.symptoms:
        parts.append(f"\nSymptoms: {case_row.symptoms}")
    parts.append(f"\nRoot Cause: {case_row.root_cause}")
    parts.append(f"\nResolution: {case_row.resolution}")

    related_parts = _parse_jsonb_list(getattr(case_row, "related_parts", None))
    if related_parts:
        parts.append(f"\nRelated Parts: {', '.join(str(p) for p in related_parts)}")

    if case_row.machine_model:
        parts.append(f"\nApplicable Machine Model: AutoBoss {case_row.machine_model}")

    return "\n".join(parts)


async def _sync_case_to_knowledge_base(case_row, kb_service=None) -> Optional[str]:
    """
    Create or update the knowledge base document for a resolved support case so
    the AI assistant can cite it as verified field experience.

    - If the case already has a knowledge_doc_id and that document still exists,
      its content is refreshed in place (no duplicate).
    - Otherwise a new knowledge document is created.
    - Returns the knowledge document id, or None if the case has no resolution yet.

    Pass an existing kb_service to reuse one LLM client / vector index across a
    batch (see the backfill endpoint).
    """
    if not (case_row.resolution and str(case_row.resolution).strip()):
        return None

    title = f"[Resolved Case] {case_row.title}"
    content = _build_case_document_content(case_row)
    machine_models = [case_row.machine_model] if case_row.machine_model else ["ALL"]

    tags = _parse_jsonb_list(case_row.tags) + ["support_case", "resolved_issue", "troubleshooting"]
    tags = list(dict.fromkeys(tags))  # de-dupe, keep order

    metadata = {
        "source": "support_case",
        "case_id": case_row.id,
        "case_number": case_row.case_number,
        "priority": case_row.priority,
        "resolved_at": str(case_row.resolved_at) if case_row.resolved_at else None,
    }

    from ..llm_client import LLMClient
    from ..services.knowledge_base import KnowledgeBaseService
    from ..services.vector_database import VectorDatabase

    own_client = None
    if kb_service is None:
        own_client = LLMClient()
        await own_client.initialize()
        kb_service = KnowledgeBaseService(own_client, VectorDatabase())

    try:
        existing_id = getattr(case_row, "knowledge_doc_id", None)
        if existing_id and await kb_service.get_document(existing_id):
            await kb_service.update_document(
                existing_id,
                title=title,
                content=content,
                machine_models=machine_models,
                tags=tags,
                metadata=metadata,
            )
            logger.info(f"Refreshed KB doc {existing_id} for case {case_row.case_number}")
            return existing_id

        doc_id = await kb_service.create_document(
            title=title,
            content=content,
            document_type="support_case",
            machine_models=machine_models,
            tags=tags,
            language="en",
            version="1.0",
            metadata=metadata,
        )
        logger.info(f"Created KB doc {doc_id} for case {case_row.case_number}")
        return doc_id

    finally:
        if own_client is not None:
            await own_client.cleanup()


async def _llm_extract_json(llm_client, prompt: str) -> dict:
    """Call the LLM and parse a JSON object from the reply. Tries json_object mode,
    then plain mode, on the primary then fallback model."""
    last_err = None
    for model in (settings.OPENAI_MODEL, settings.OPENAI_FALLBACK_MODEL):
        for use_response_format in (True, False):
            try:
                kwargs = dict(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700,
                    temperature=0.2,
                )
                if use_response_format:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = await llm_client.client.chat.completions.create(**kwargs)
                raw = resp.choices[0].message.content or ""
                start, end = raw.find("{"), raw.rfind("}")
                if start != -1 and end != -1:
                    return json.loads(raw[start:end + 1])
            except Exception as e:
                last_err = e
    raise RuntimeError(f"LLM JSON extraction failed: {last_err}")


async def _distill_case_fields(llm_client, transcript: str, language: str = "en") -> dict:
    """Turn a chat transcript into structured support-case fields."""
    prompt = (
        "You extract a structured support case from a conversation between an AutoBoss "
        "net-cleaning-machine operator and an AI assistant.\n"
        "Return ONLY a JSON object with these keys:\n"
        '  "title": short problem summary, max ~80 chars\n'
        '  "description": 1-3 sentences of problem context\n'
        '  "symptoms": what was observed / reported\n'
        '  "root_cause": the underlying cause identified in the conversation, "" if none\n'
        '  "resolution": the concrete fix the operator CONFIRMED worked, "" if not confirmed\n'
        '  "machine_model": e.g. "V4", "V3.1B" if stated, else null\n'
        '  "tags": array of 2-5 short lowercase keywords\n'
        "Base every field strictly on the conversation. If the operator never confirmed a "
        'fix, "resolution" MUST be an empty string.\n\n'
        f"CONVERSATION:\n{transcript}"
    )
    data = await _llm_extract_json(llm_client, prompt)

    def s(v):
        return str(v).strip() if v is not None else ""

    return {
        "title": s(data.get("title")) or "Support case captured from AI chat",
        "description": s(data.get("description")),
        "symptoms": s(data.get("symptoms")),
        "root_cause": s(data.get("root_cause")),
        "resolution": s(data.get("resolution")),
        "machine_model": s(data.get("machine_model")) or None,
        "tags": [s(t).lower() for t in (data.get("tags") or []) if s(t)][:5],
    }


async def _save_conversation_as_case(*, llm_client, transcript: str,
                                     session_id: Optional[str] = None,
                                     machine_id: Optional[str] = None,
                                     machine_model: Optional[str] = None,
                                     user_id: Optional[str] = None,
                                     organization_id: Optional[str] = None,
                                     language: str = "en") -> dict:
    """
    Distil a chat transcript into a resolved support case and publish it to the
    knowledge base. Idempotent per session_id (updates the linked case if any).
    """
    fields = await _distill_case_fields(llm_client, transcript, language)

    if not fields["resolution"]:
        return {
            "saved": False,
            "reason": "no_confirmed_resolution",
            "message": "I couldn't identify a confirmed fix in this conversation, so no case was created.",
        }

    model = machine_model or fields["machine_model"]
    tags = list(dict.fromkeys(fields["tags"] + ["ai_chat", "captured_from_chat"]))
    title = fields["title"][:200]
    description = fields["description"] or title

    # support_cases.session_id is a FK to ai_sessions - only reference a session
    # row that actually exists (it isn't persisted for anonymous chats).
    link_session_id = None
    if session_id:
        with get_db_session() as db:
            if db.execute(text("SELECT 1 FROM ai_sessions WHERE id = :s"),
                          {"s": session_id}).fetchone():
                link_session_id = session_id

    existing = None
    if link_session_id:
        with get_db_session() as db:
            existing = db.execute(text(
                "SELECT id, case_number, knowledge_doc_id FROM support_cases "
                "WHERE session_id = :s ORDER BY created_at DESC LIMIT 1"
            ), {"s": link_session_id}).fetchone()

    if existing:
        case_id = str(existing.id)
        with get_db_session() as db:
            db.execute(text("""
                UPDATE support_cases SET
                    title = :title, description = :description, symptoms = :symptoms,
                    root_cause = :root_cause, resolution = :resolution,
                    machine_model = COALESCE(:machine_model, machine_model),
                    status = 'resolved', resolved_at = COALESCE(resolved_at, NOW()),
                    tags = :tags, updated_at = NOW()
                WHERE id = :id
            """), {
                "title": title, "description": description,
                "symptoms": fields["symptoms"], "root_cause": fields["root_cause"],
                "resolution": fields["resolution"], "machine_model": model,
                "tags": json.dumps(tags), "id": case_id,
            })
            row = db.execute(text("SELECT * FROM support_cases WHERE id = :id"),
                             {"id": case_id}).fetchone()
        created = False
    else:
        case_id = str(uuid.uuid4())
        case_number = _generate_case_number()
        with get_db_session() as db:
            db.execute(text("""
                INSERT INTO support_cases
                (id, case_number, title, description, machine_model, machine_id, symptoms,
                 root_cause, resolution, status, priority, organization_id, created_by,
                 tags, related_parts, session_id, created_at, updated_at, resolved_at)
                VALUES
                (:id, :case_number, :title, :description, :machine_model, :machine_id, :symptoms,
                 :root_cause, :resolution, 'resolved', 'medium', :organization_id, :created_by,
                 :tags, :related_parts, :session_id, NOW(), NOW(), NOW())
            """), {
                "id": case_id, "case_number": case_number, "title": title,
                "description": description, "machine_model": model,
                "machine_id": machine_id, "symptoms": fields["symptoms"],
                "root_cause": fields["root_cause"], "resolution": fields["resolution"],
                "organization_id": organization_id, "created_by": user_id or "ai_chat",
                "tags": json.dumps(tags), "related_parts": json.dumps([]),
                "session_id": link_session_id,
            })
            row = db.execute(text("SELECT * FROM support_cases WHERE id = :id"),
                             {"id": case_id}).fetchone()
        created = True

    knowledge_doc_id = None
    try:
        knowledge_doc_id = await _sync_case_to_knowledge_base(row)
        if knowledge_doc_id and knowledge_doc_id != row.knowledge_doc_id:
            with get_db_session() as db:
                db.execute(text("UPDATE support_cases SET knowledge_doc_id = :d WHERE id = :id"),
                           {"d": knowledge_doc_id, "id": case_id})
    except Exception as e:
        logger.warning(f"Failed to sync chat-captured case {case_id} to knowledge base: {e}")

    return {
        "saved": True,
        "created": created,
        "case_id": case_id,
        "case_number": row.case_number,
        "knowledge_doc_id": knowledge_doc_id,
        "title": fields["title"],
    }
