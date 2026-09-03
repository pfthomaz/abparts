"""
Support Cases API endpoints for recording and managing customer issues.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from sqlalchemy import text
from datetime import datetime
import asyncio
import logging
import uuid
import json

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

logger = logging.getLogger(__name__)
router = APIRouter()


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
        created_by=row.created_by,
        assigned_to=row.assigned_to,
        tags=_parse_jsonb_list(row.tags),
        related_parts=_parse_jsonb_list(row.related_parts),
        internal_notes=row.internal_notes,
        knowledge_doc_id=row.knowledge_doc_id,
        session_id=row.session_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        resolved_at=row.resolved_at,
        closed_at=row.closed_at,
        comments=comments or [],
    )


@router.post("/support-cases", response_model=SupportCaseResponse)
async def create_support_case(request: CreateSupportCaseRequest):
    """
    Create a new support case.
    """
    case_id = str(uuid.uuid4())
    case_number = _generate_case_number()

    try:
        with get_db_session() as db:
            db.execute(text("""
                INSERT INTO support_cases 
                (id, case_number, title, description, machine_model, machine_id,
                 symptoms, status, priority, organization_id, created_by, assigned_to,
                 tags, related_parts, session_id, created_at, updated_at)
                VALUES (:id, :case_number, :title, :description, :machine_model, :machine_id,
                        :symptoms, :status, :priority, :organization_id, :created_by, :assigned_to,
                        :tags, :related_parts, :session_id, NOW(), NOW())
            """), {
                'id': case_id,
                'case_number': case_number,
                'title': request.title,
                'description': request.description,
                'machine_model': request.machine_model,
                'machine_id': request.machine_id,
                'symptoms': request.symptoms,
                'status': 'open',
                'priority': request.priority.value,
                'organization_id': request.organization_id,
                'created_by': request.assigned_to or 'system',  # Will be overridden by auth
                'assigned_to': request.assigned_to,
                'tags': json.dumps(request.tags if request.tags else []),
                'related_parts': json.dumps(request.related_parts if request.related_parts else []),
                'session_id': request.session_id,
            })

            # Fetch the created case
            result = db.execute(
                text("SELECT * FROM support_cases WHERE id = :id"),
                {'id': case_id}
            ).fetchone()

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
            result = db.execute(
                text("SELECT * FROM support_cases WHERE id = :id"),
                {'id': case_id}
            ).fetchone()

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
                created_at=c.created_at,
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
async def update_support_case(case_id: str, request: UpdateSupportCaseRequest):
    """
    Update a support case.
    """
    try:
        set_clauses = ["updated_at = NOW()"]
        params = {'case_id': case_id}

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
            result = db.execute(
                text(f"UPDATE support_cases SET {', '.join(set_clauses)} WHERE id = :case_id RETURNING *"),
                params
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Support case not found")

        # Keep the knowledge base in sync when a resolved case's content changes
        kb_relevant = ('title', 'description', 'symptoms', 'root_cause',
                       'resolution', 'machine_model', 'related_parts', 'tags', 'status')
        if (result.status == 'resolved' and result.resolution
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
async def resolve_support_case(case_id: str, request: ResolveSupportCaseRequest):
    """
    Resolve a support case and optionally publish to knowledge base.
    """
    try:
        with get_db_session() as db:
            # Update the case
            result = db.execute(
                text("""
                    UPDATE support_cases 
                    SET root_cause = :root_cause,
                        resolution = :resolution,
                        internal_notes = COALESCE(:internal_notes, internal_notes),
                        status = 'resolved',
                        resolved_at = NOW(),
                        updated_at = NOW()
                    WHERE id = :case_id
                    RETURNING *
                """),
                {
                    'case_id': case_id,
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
            result = db.execute(
                text("SELECT * FROM support_cases WHERE id = :id"),
                {'id': case_id}
            ).fetchone()

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
    Publish resolved support cases into the AI knowledge base.

    By default this only touches resolved cases that have a resolution but are
    NOT yet in the knowledge base (no knowledge_doc_id). With refresh_existing=true
    it also re-syncs cases that are already linked, picking up later edits.

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
                WHERE status = 'resolved'
                  AND resolution IS NOT NULL AND btrim(resolution) <> ''
                  {kb_filter}
                ORDER BY resolved_at NULLS LAST
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
            created_at=result.created_at,
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
                created_at=c.created_at,
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
