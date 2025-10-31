"""Handover API endpoints."""
import json
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user, require_admin
from app.models import HandoverIncident, IncidentStatus, User, UserRole
from app.schemas.handover import (
    HandoverRequest,
    HandoverResponse,
    IncidentDetail,
    IncidentListItem,
    IncidentUpdate,
    IncidentStats,
)
from app.services.email_client import EmailService

router = APIRouter()
logger = get_logger(__name__)


def _summarize_conversation(messages: list[dict]) -> str:
    """Generate a summary of the conversation."""
    summary_parts = []
    
    for msg in messages[-10:]:  # Last 10 messages
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "user":
            summary_parts.append(f"Patient: {content[:200]}")
        elif role == "assistant":
            summary_parts.append(f"Assistant: {content[:200]}")
    
    return "\n\n".join(summary_parts)


@router.post("/request", response_model=HandoverResponse)
async def request_handover(
    handover_request: HandoverRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HandoverResponse:
    """
    Request handover to human support.
    
    Patient can click a button to escalate their conversation to a human.
    This creates an incident, sends notifications to admins, and confirms to patient.
    """
    try:
        # Generate confirmation code
        confirmation_code = f"HO-{secrets.token_hex(4).upper()}"
        
        # Generate chat summary
        chat_summary = _summarize_conversation(handover_request.messages)
        full_conversation = json.dumps(handover_request.messages)
        
        # Create incident
        incident = HandoverIncident(
            user_id=current_user.id,
            patient_name=current_user.name,
            patient_email=current_user.email,
            patient_phone=handover_request.patient_phone,
            subject=handover_request.subject,
            chat_summary=chat_summary,
            full_conversation=full_conversation,
            priority=handover_request.priority,
            status=IncidentStatus.PENDING,
        )
        
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        
        logger.info(
            "handover_incident_created",
            incident_id=incident.id,
            user_id=current_user.id,
            priority=handover_request.priority.value,
        )
        
        # Get all admin users for notification
        result = await db.execute(
            select(User).where(User.role == UserRole.ADMIN)
        )
        admins = result.scalars().all()
        admin_emails = [admin.email for admin in admins]
        
        # Send notifications
        email_service = EmailService()
        
        incident_details = {
            "incident_id": incident.id,
            "patient_name": current_user.name,
            "patient_email": current_user.email,
            "patient_phone": handover_request.patient_phone or "Not provided",
            "subject": handover_request.subject,
            "chat_summary": chat_summary,
            "priority": handover_request.priority.value,
            "confirmation_code": confirmation_code,
            "admin_portal_url": "http://localhost:5173",
            "estimated_response_time": "within 24 hours",
        }
        
        # Send to admins
        if admin_emails:
            await email_service.send_handover_notification(admin_emails, incident_details)
            logger.info(
                "handover_notification_sent",
                incident_id=incident.id,
                admin_count=len(admin_emails),
            )
        
        # Send confirmation to patient
        await email_service.send_handover_confirmation_to_patient(
            current_user.email, incident_details
        )
        
        return HandoverResponse(
            incident_id=incident.id,
            status=incident.status,
            message="Your request has been received. Our team will contact you soon.",
            confirmation_code=confirmation_code,
            estimated_response_time="within 24 hours",
        )
        
    except Exception as e:
        logger.error("handover_request_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=500, detail=f"Failed to process handover request: {str(e)}"
        )


@router.get("/incidents", response_model=list[IncidentListItem])
async def list_incidents(
    status: IncidentStatus | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[IncidentListItem]:
    """List all handover incidents (admin only)."""
    query = select(HandoverIncident).options(
        selectinload(HandoverIncident.assigned_admin)
    )
    
    if status:
        query = query.where(HandoverIncident.status == status)
    
    query = query.order_by(HandoverIncident.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [
        IncidentListItem(
            id=incident.id,
            patient_name=incident.patient_name,
            patient_email=incident.patient_email,
            subject=incident.subject,
            priority=incident.priority,
            status=incident.status,
            created_at=incident.created_at,
            assigned_to=incident.assigned_to,
            assigned_admin_name=incident.assigned_admin.name if incident.assigned_admin else None,
        )
        for incident in incidents
    ]


@router.get("/incidents/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> IncidentDetail:
    """Get detailed incident information (admin only)."""
    result = await db.execute(
        select(HandoverIncident)
        .options(selectinload(HandoverIncident.assigned_admin))
        .where(HandoverIncident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentDetail(
        id=incident.id,
        user_id=incident.user_id,
        patient_name=incident.patient_name,
        patient_email=incident.patient_email,
        patient_phone=incident.patient_phone,
        subject=incident.subject,
        chat_summary=incident.chat_summary,
        full_conversation=incident.full_conversation,
        priority=incident.priority,
        status=incident.status,
        assigned_to=incident.assigned_to,
        assigned_admin_name=incident.assigned_admin.name if incident.assigned_admin else None,
        admin_notes=incident.admin_notes,
        resolution=incident.resolution,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


@router.patch("/incidents/{incident_id}", response_model=IncidentDetail)
async def update_incident(
    incident_id: int,
    update: IncidentUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> IncidentDetail:
    """Update incident (admin only)."""
    result = await db.execute(
        select(HandoverIncident)
        .options(selectinload(HandoverIncident.assigned_admin))
        .where(HandoverIncident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields
    if update.status is not None:
        incident.status = update.status
        if update.status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now(timezone.utc)
    
    if update.priority is not None:
        incident.priority = update.priority
    
    if update.assigned_to is not None:
        incident.assigned_to = update.assigned_to
    
    if update.admin_notes is not None:
        incident.admin_notes = update.admin_notes
    
    if update.resolution is not None:
        incident.resolution = update.resolution
    
    await db.commit()
    await db.refresh(incident)
    
    logger.info(
        "incident_updated",
        incident_id=incident_id,
        updated_by=current_user.id,
        status=incident.status.value,
    )
    
    return IncidentDetail(
        id=incident.id,
        user_id=incident.user_id,
        patient_name=incident.patient_name,
        patient_email=incident.patient_email,
        patient_phone=incident.patient_phone,
        subject=incident.subject,
        chat_summary=incident.chat_summary,
        full_conversation=incident.full_conversation,
        priority=incident.priority,
        status=incident.status,
        assigned_to=incident.assigned_to,
        assigned_admin_name=incident.assigned_admin.name if incident.assigned_admin else None,
        admin_notes=incident.admin_notes,
        resolution=incident.resolution,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


@router.get("/incidents/stats/overview", response_model=IncidentStats)
async def get_incident_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> IncidentStats:
    """Get incident statistics (admin only)."""
    # Total count
    total_result = await db.execute(select(func.count(HandoverIncident.id)))
    total_incidents = total_result.scalar() or 0
    
    # Status counts
    pending_result = await db.execute(
        select(func.count(HandoverIncident.id)).where(
            HandoverIncident.status == IncidentStatus.PENDING
        )
    )
    pending_count = pending_result.scalar() or 0
    
    in_progress_result = await db.execute(
        select(func.count(HandoverIncident.id)).where(
            HandoverIncident.status == IncidentStatus.IN_PROGRESS
        )
    )
    in_progress_count = in_progress_result.scalar() or 0
    
    resolved_result = await db.execute(
        select(func.count(HandoverIncident.id)).where(
            HandoverIncident.status == IncidentStatus.RESOLVED
        )
    )
    resolved_count = resolved_result.scalar() or 0
    
    # Priority counts
    high_priority_result = await db.execute(
        select(func.count(HandoverIncident.id)).where(
            and_(
                HandoverIncident.priority == "high",
                HandoverIncident.status != IncidentStatus.CLOSED,
            )
        )
    )
    high_priority_count = high_priority_result.scalar() or 0
    
    urgent_result = await db.execute(
        select(func.count(HandoverIncident.id)).where(
            and_(
                HandoverIncident.priority == "urgent",
                HandoverIncident.status != IncidentStatus.CLOSED,
            )
        )
    )
    urgent_count = urgent_result.scalar() or 0
    
    # Average resolution time
    avg_time_result = await db.execute(
        select(
            func.avg(
                func.extract('epoch', HandoverIncident.resolved_at - HandoverIncident.created_at)
            )
        ).where(HandoverIncident.resolved_at.isnot(None))
    )
    avg_seconds = avg_time_result.scalar()
    avg_resolution_time_hours = (avg_seconds / 3600) if avg_seconds else None
    
    return IncidentStats(
        total_incidents=total_incidents,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        avg_resolution_time_hours=avg_resolution_time_hours,
        high_priority_count=high_priority_count,
        urgent_count=urgent_count,
    )
