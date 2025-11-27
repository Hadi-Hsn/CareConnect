"""Mock scheduling client for development."""
import secrets
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_maker
from app.core.logging import get_logger
from app.models import Appointment, AppointmentChannel, AppointmentStatus, Provider
from app.schemas.provider import TimeSlot
from app.services.scheduling_client import SchedulingClient

logger = get_logger(__name__)

# Lebanon timezone
LEBANON_TZ = ZoneInfo("Asia/Beirut")


class MockSchedulingClient(SchedulingClient):
    """Mock scheduling client for development and testing."""

    def __init__(self) -> None:
        """Initialize mock scheduling client."""
        # Define working hours (9 AM to 5 PM)
        self.start_hour = 9
        self.end_hour = 17
        self.slot_duration_minutes = 30

    async def _get_session(self) -> AsyncSession:
        """Get database session."""
        return async_session_maker()

    def _generate_slots_for_date(
        self,
        provider_id: int,
        target_date: date,
        filter_past: bool = True,
    ) -> list[TimeSlot]:
        """Generate timeslots for a given date.
        
        Args:
            provider_id: Provider the slots belong to (embedded in slot_id for validation)
            target_date: The date to generate slots for
            filter_past: If True, filter out past time slots for today
        """
        slots: list[TimeSlot] = []
        current_time = datetime.combine(target_date, time(hour=self.start_hour), tzinfo=LEBANON_TZ)
        end_time = datetime.combine(target_date, time(hour=self.end_hour), tzinfo=LEBANON_TZ)
        
        # Get current time in Lebanon timezone for filtering
        now_lebanon = datetime.now(LEBANON_TZ)
        is_today = target_date == now_lebanon.date()

        slot_id = 1
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=self.slot_duration_minutes)
            
            # Skip past slots if this is today and filter_past is True
            if filter_past and is_today and slot_end <= now_lebanon:
                current_time = slot_end
                slot_id += 1
                continue
            
            slots.append(
                TimeSlot(
                    slot_id=f"slot_{provider_id}_{target_date.isoformat()}_{slot_id}",
                    start=current_time,
                    end=slot_end,
                    available=True,  # All slots available in mock
                )
            )
            current_time = slot_end
            slot_id += 1

        return slots

    async def search_providers(
        self, department: str | None = None, provider_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Search for providers."""
        async with await self._get_session() as session:
            query = select(Provider)

            if department:
                query = query.where(Provider.department.ilike(f"%{department}%"))
            if provider_type:
                query = query.where(Provider.type == provider_type)

            result = await session.execute(query)
            providers = result.scalars().all()

            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "department": p.department,
                    "type": p.type,
                    "specialty": p.specialty,
                }
                for p in providers
            ]

    async def get_timeslots(self, provider_id: int, target_date: date) -> list[TimeSlot]:
        """Get available timeslots for a provider."""
        # Check if provider exists
        async with await self._get_session() as session:
            result = await session.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()

            if not provider:
                logger.warning("provider_not_found", provider_id=provider_id)
                return []

            # Generate all possible slots (with past filtering for today)
            all_slots = self._generate_slots_for_date(provider_id, target_date, filter_past=True)

            # Get existing appointments for this provider on this date
            start_of_day = datetime.combine(target_date, time.min, tzinfo=LEBANON_TZ)
            end_of_day = datetime.combine(target_date, time.max, tzinfo=LEBANON_TZ)

            result = await session.execute(
                select(Appointment).where(
                    Appointment.provider_id == provider_id,
                    Appointment.time_start >= start_of_day,
                    Appointment.time_start <= end_of_day,
                    Appointment.status == AppointmentStatus.CONFIRMED,
                )
            )
            booked_appointments = result.scalars().all()

            # Mark booked slots as unavailable
            booked_times = {(appt.time_start, appt.time_end) for appt in booked_appointments}

            for slot in all_slots:
                if (slot.start, slot.end) in booked_times:
                    slot.available = False

            logger.info(
                "generated_timeslots",
                provider_id=provider_id,
                date=target_date.isoformat(),
                total_slots=len(all_slots),
                available_slots=sum(1 for s in all_slots if s.available),
            )

            return all_slots

    async def book_appointment(
        self, user_id: int, provider_id: int, slot_id: str, reason: str | None = None
    ) -> dict[str, Any]:
        """Book an appointment."""
        # Parse slot_id to get start time
        # Format: slot_YYYY-MM-DD_N
        try:
            parts = slot_id.split("_")
            if len(parts) != 4:
                raise ValueError("Invalid slot_id format")

            _, slot_provider_id_str, date_str, slot_number_str = parts
            slot_provider_id = int(slot_provider_id_str)

            if slot_provider_id != provider_id:
                raise ValueError(
                    f"Slot {slot_id} does not belong to provider {provider_id}"
                )

            slot_number = int(slot_number_str)

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slots = self._generate_slots_for_date(
                provider_id, target_date, filter_past=False
            )  # Don't filter when booking

            if slot_number - 1 >= len(slots):
                raise ValueError("Invalid slot number")

            selected_slot = slots[slot_number - 1]

            # Create appointment
            async with await self._get_session() as session:
                # Check if this slot is already booked
                start_of_day = datetime.combine(target_date, time.min, tzinfo=LEBANON_TZ)
                end_of_day = datetime.combine(target_date, time.max, tzinfo=LEBANON_TZ)
                
                result = await session.execute(
                    select(Appointment).where(
                        Appointment.provider_id == provider_id,
                        Appointment.time_start == selected_slot.start,
                        Appointment.time_end == selected_slot.end,
                        Appointment.status == AppointmentStatus.CONFIRMED,
                    )
                )
                existing_appointment = result.scalar_one_or_none()
                
                if existing_appointment:
                    logger.warning(
                        "slot_already_booked",
                        provider_id=provider_id,
                        slot_id=slot_id,
                        existing_appointment_id=existing_appointment.id,
                    )
                    return {
                        "error": f"This time slot is no longer available. Please choose another time.",
                        "slot_id": slot_id,
                        "time_start": selected_slot.start.isoformat(),
                    }

                confirmation_code = secrets.token_hex(8).upper()

                appointment = Appointment(
                    user_id=user_id,
                    provider_id=provider_id,
                    time_start=selected_slot.start,
                    time_end=selected_slot.end,
                    status=AppointmentStatus.CONFIRMED,
                    channel=AppointmentChannel.AGENT,
                    reason=reason,
                    confirmation_code=confirmation_code,
                )

                session.add(appointment)
                await session.commit()
                await session.refresh(appointment)

                logger.info(
                    "appointment_booked",
                    appointment_id=appointment.id,
                    user_id=user_id,
                    provider_id=provider_id,
                    confirmation_code=confirmation_code,
                )

                return {
                    "appointment_id": appointment.id,
                    "confirmation_code": confirmation_code,
                    "time_start": appointment.time_start.isoformat(),
                    "time_end": appointment.time_end.isoformat(),
                    "status": str(appointment.status) if hasattr(appointment.status, 'value') else appointment.status,
                }

        except Exception as e:
            logger.error("booking_failed", error=str(e), slot_id=slot_id)
            raise ValueError(f"Failed to book appointment: {e}")

    async def modify_appointment(self, appointment_id: int, new_slot_id: str) -> dict[str, Any]:
        """Modify an existing appointment."""
        try:
            # Parse new slot
            parts = new_slot_id.split("_")
            if len(parts) != 4:
                raise ValueError("Invalid slot_id format")

            _, slot_provider_id_str, date_str, slot_number_str = parts
            slot_provider_id = int(slot_provider_id_str)
            slot_number = int(slot_number_str)

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slots = self._generate_slots_for_date(
                slot_provider_id, target_date, filter_past=False
            )  # Don't filter when modifying

            if slot_number - 1 >= len(slots):
                raise ValueError("Invalid slot number")

            selected_slot = slots[slot_number - 1]

            # Update appointment
            async with await self._get_session() as session:
                result = await session.execute(
                    select(Appointment).where(Appointment.id == appointment_id)
                )
                appointment = result.scalar_one_or_none()

                if not appointment:
                    raise ValueError("Appointment not found")

                if slot_provider_id != appointment.provider_id:
                    raise ValueError(
                        "New time slot belongs to a different provider than the appointment"
                    )

                appointment.time_start = selected_slot.start
                appointment.time_end = selected_slot.end
                appointment.updated_at = datetime.now(LEBANON_TZ)

                await session.commit()
                await session.refresh(appointment)

                logger.info("appointment_modified", appointment_id=appointment_id)

                return {
                    "appointment_id": appointment.id,
                    "time_start": appointment.time_start.isoformat(),
                    "time_end": appointment.time_end.isoformat(),
                    "status": str(appointment.status) if hasattr(appointment.status, 'value') else appointment.status,
                }

        except Exception as e:
            logger.error("modification_failed", error=str(e), appointment_id=appointment_id)
            raise ValueError(f"Failed to modify appointment: {e}")

    async def cancel_appointment(self, appointment_id: int) -> dict[str, Any]:
        """Cancel an appointment."""
        try:
            async with await self._get_session() as session:
                # Get appointment with provider details
                result = await session.execute(
                    select(Appointment, Provider)
                    .join(Provider, Appointment.provider_id == Provider.id)
                    .where(Appointment.id == appointment_id)
                )
                row = result.first()

                if not row:
                    raise ValueError("Appointment not found")

                appointment, provider = row

                # Store details before cancellation for response
                cancelled_reason = appointment.reason or f"{provider.department} appointment"
                cancelled_time = appointment.time_start
                cancelled_confirmation = appointment.confirmation_code

                appointment.status = AppointmentStatus.CANCELLED
                appointment.updated_at = datetime.now(LEBANON_TZ)

                await session.commit()

                logger.info("appointment_cancelled", appointment_id=appointment_id)

                return {
                    "appointment_id": appointment.id,
                    "status": str(appointment.status) if hasattr(appointment.status, 'value') else appointment.status,
                    "cancelled_appointment": {
                        "reason": cancelled_reason,
                        "provider_name": provider.name,
                        "department": provider.department,
                        "date_time": cancelled_time.strftime("%B %d, %Y at %I:%M %p"),
                        "confirmation_code": cancelled_confirmation,
                    },
                    "message": f"Successfully cancelled: {cancelled_reason} on {cancelled_time.strftime('%B %d, %Y at %I:%M %p')}",
                }

        except Exception as e:
            logger.error("cancellation_failed", error=str(e), appointment_id=appointment_id)
            raise ValueError(f"Failed to cancel appointment: {e}")
