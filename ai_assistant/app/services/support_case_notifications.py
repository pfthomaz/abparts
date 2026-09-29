"""
Email notifications between Oraseas and BossServ for support cases.

When someone at Oraseas records or resolves a support case, BossServ is emailed,
and vice versa. Cases recorded by anyone else (customers, AI chat capture) send
nothing.

Recipients are the active admin users of the other side's organization, unless
overridden with a comma-separated list in SUPPORT_CASE_NOTIFY_ORASEAS /
SUPPORT_CASE_NOTIFY_BOSSSERV.
"""

import os
import logging
from datetime import datetime
from html import escape
from typing import Optional, List, Dict, Any

from sqlalchemy import text

from ..database import get_db_session
from .email_service import email_service

logger = logging.getLogger(__name__)

ORASEAS = "oraseas"
BOSSSERV = "bossserv"

SIDE_LABELS = {ORASEAS: "Oraseas", BOSSSERV: "BossServ"}

CHANNEL_LABELS = {
    "phone": "Phone",
    "email": "Email",
    "whatsapp": "WhatsApp",
    "on_site": "On site",
    "other": "Other",
}

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000").rstrip("/")


def _side_of(org_type: Optional[str], org_name: Optional[str]) -> Optional[str]:
    if org_type == "oraseas_ee":
        return ORASEAS
    if org_name and org_name.lower().startswith("bossserv"):
        return BOSSSERV
    return None


def get_user_context(user_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Look up an ABParts user with their organization and which side they are on."""
    if not user_id:
        return None
    with get_db_session() as db:
        row = db.execute(text("""
            SELECT u.id::text AS id, u.name, u.username, u.email, u.role::text AS role,
                   u.is_active, u.user_status::text AS user_status,
                   o.name AS org_name, o.organization_type::text AS org_type
            FROM users u JOIN organizations o ON o.id = u.organization_id
            WHERE u.id::text = :id
        """), {"id": user_id}).fetchone()
    if not row:
        return None
    return {
        "id": row.id,
        "name": row.name or row.username,
        "email": row.email,
        "role": row.role,
        "is_active": bool(row.is_active) and row.user_status == "active",
        "org_name": row.org_name,
        "side": _side_of(row.org_type, row.org_name),
    }


def _recipients_for(side: str) -> List[str]:
    override = os.getenv(f"SUPPORT_CASE_NOTIFY_{side.upper()}", "")
    emails = [e.strip() for e in override.split(",") if e.strip()]
    if emails:
        return emails

    org_filter = ("o.organization_type::text = 'oraseas_ee'" if side == ORASEAS
                  else "o.name ILIKE 'BossServ%'")
    with get_db_session() as db:
        rows = db.execute(text(f"""
            SELECT DISTINCT u.email
            FROM users u JOIN organizations o ON o.id = u.organization_id
            WHERE {org_filter}
              AND u.is_active
              AND u.user_status::text = 'active'
              AND u.role::text IN ('admin', 'super_admin')
              AND u.email IS NOT NULL AND u.email <> ''
        """)).fetchall()
    return [r.email for r in rows]


def _fmt_time(value: Optional[datetime]) -> str:
    return value.strftime("%d %b %Y %H:%M UTC") if value else "-"


def _case_fields(case, actor: Dict[str, Any], resolver: Optional[Dict[str, Any]]):
    """Ordered (label, value) pairs for the email body."""
    recorder = get_user_context(case.created_by)
    fields = [
        ("Case", case.case_number),
        ("Customer", case.organization_id or "-"),
        ("Machine", f"{case.machine_name} (S/N {case.machine_serial})" if case.machine_name else "-"),
        ("Machine model", f"AutoBoss {case.machine_model}" if case.machine_model else "-"),
        ("Priority", (case.priority or "").capitalize()),
        ("Customer contacted", _fmt_time(getattr(case, "contacted_at", None))),
        ("Contact channel", CHANNEL_LABELS.get(getattr(case, "contact_channel", None) or "", "-")),
        ("Recorded by", f"{recorder['name']} ({recorder['org_name']})" if recorder else "-"),
        ("Recorded at", _fmt_time(case.created_at)),
        ("Title", case.title),
        ("Description", case.description),
    ]
    if case.symptoms:
        fields.append(("Symptoms", case.symptoms))
    if case.root_cause:
        fields.append(("Root cause", case.root_cause))
    if case.resolution:
        fields.append(("Resolution", case.resolution))
        who = resolver or actor
        fields.append(("Resolved by", f"{who['name']} ({who['org_name']})"))
        fields.append(("Resolved at", _fmt_time(case.resolved_at)))
    return fields


def _build_email(case, event: str, actor: Dict[str, Any], resolver: Optional[Dict[str, Any]]):
    side_label = SIDE_LABELS[actor["side"]]
    if event == "resolved":
        subject = f"Support case resolved by {side_label}: {case.case_number} - {case.title}"
        intro = f"{actor['name']} ({side_label}) resolved a support case."
    else:
        subject = f"New support case from {side_label}: {case.case_number} - {case.title}"
        intro = f"{actor['name']} ({side_label}) recorded a new customer support case."
        if case.status == "resolved":
            intro += " It was already resolved when recorded."

    fields = _case_fields(case, actor, resolver)
    link = f"{BASE_URL}/support-cases"

    text_body = "\n".join(
        [intro, ""] + [f"{label}: {value}" for label, value in fields] + ["", f"View in ABParts: {link}"]
    )

    rows = "".join(
        f'<tr><td style="padding:6px 12px 6px 0;color:#6b7280;vertical-align:top;white-space:nowrap">'
        f'{escape(label)}</td><td style="padding:6px 0;white-space:pre-wrap">{escape(str(value))}</td></tr>'
        for label, value in fields
    )
    html_body = f"""<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#111827">
<p>{escape(intro)}</p>
<table style="border-collapse:collapse">{rows}</table>
<p><a href="{escape(link)}">View in ABParts</a></p>
</body></html>"""

    return subject, html_body, text_body


def notify_case_event(case_id: str, event: str, actor_user_id: Optional[str]) -> None:
    """
    Email the other side (Oraseas <-> BossServ) that a case was created or resolved.
    Runs as a background task; never raises.
    """
    try:
        actor = get_user_context(actor_user_id)
        if not actor or not actor["side"]:
            logger.info(f"No support case notification for case {case_id}: "
                        f"user {actor_user_id} is not Oraseas or BossServ")
            return

        other_side = BOSSSERV if actor["side"] == ORASEAS else ORASEAS
        recipients = _recipients_for(other_side)
        if not recipients:
            logger.warning(f"No {SIDE_LABELS[other_side]} recipients for support case {case_id}")
            return

        with get_db_session() as db:
            case = db.execute(text("""
                SELECT sc.*, m.name AS machine_name, m.serial_number AS machine_serial
                FROM support_cases sc LEFT JOIN machines m ON m.id::text = sc.machine_id
                WHERE sc.id = :id
            """), {"id": case_id}).fetchone()
        if not case:
            return

        resolver = get_user_context(getattr(case, "resolved_by", None))
        subject, html_body, text_body = _build_email(case, event, actor, resolver)
        sent = email_service._send_email(
            to_email=", ".join(recipients),
            subject=subject,
            html_content=html_body,
            text_content=text_body,
        )
        if sent:
            logger.info(f"Support case {case.case_number} ({event}) emailed to {', '.join(recipients)}")
    except Exception as e:
        logger.error(f"Failed to send support case notification for {case_id}: {e}")
