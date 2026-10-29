"""Email notifications for the Airflow_Lab3 DAG.

Emails go through the Airflow SMTP connection (default id: smtp_default), so no
credentials live in the code. If no recipient or connection is configured, the
email is skipped and logged instead of failing the pipeline.
"""
import logging
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

log = logging.getLogger(__name__)

SMTP_CONN_ID = os.environ.get("LAB3_SMTP_CONN_ID", "smtp_default")
TEMPLATES = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates"),
    autoescape=select_autoescape(["html"]),
)


def render(template_name: str, **values) -> str:
    return TEMPLATES.get_template(template_name).render(**values)


def send_email(to: str, subject: str, html: str) -> bool:
    """Send an HTML email; returns False (and logs) instead of raising."""
    recipients = [r.strip() for r in (to or "").split(",") if r.strip()]
    if not recipients:
        log.info("No notify_email set, skipping email: %s", subject)
        return False

    try:
        from airflow.providers.smtp.hooks.smtp import SmtpHook
        from airflow.sdk import BaseHook

        sender = BaseHook.get_connection(SMTP_CONN_ID).login
        with SmtpHook(smtp_conn_id=SMTP_CONN_ID) as hook:
            hook.send_email_smtp(to=recipients, subject=subject, html_content=html,
                                 from_email=sender)
        log.info("Email sent to %s: %s", recipients, subject)
        return True
    except Exception:
        # A broken mail setup should not fail the ML pipeline itself
        log.exception("Could not send email via connection '%s'", SMTP_CONN_ID)
        return False


def task_failure_alert(context) -> None:
    """on_failure_callback: email the owner when any task fails after its retries."""
    ti = context["ti"]
    html = render(
        "email_failure.html",
        dag_id=ti.dag_id,
        task_id=ti.task_id,
        run_id=context["run_id"],
        try_number=ti.try_number,
        exception=str(context.get("exception")),
    )
    send_email(context["params"].get("notify_email", ""),
               f"[Airflow] FAILED: {ti.dag_id}.{ti.task_id}", html)
