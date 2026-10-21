import logging
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.sla_service import check_and_update_sla_breaches

logger = logging.getLogger(__name__)

@celery_app.task
def periodic_check_sla_breaches():
    logger.info("Executing periodic SLA breach detection job...")
    db = SessionLocal()
    try:
        count = check_and_update_sla_breaches(db)
        logger.info(f"SLA breach detection finished. Newly breached complaints: {count}")
        return {"newly_breached_count": count}
    finally:
        db.close()

@celery_app.task
def send_email_notification_task(recipient_email: str, subject: str, body: str):
    logger.info(f"Simulating async email delivery to {recipient_email} - Subject: {subject}")
    # Email delivery implementation or SMTP send
    return {"status": "sent", "recipient": recipient_email}
