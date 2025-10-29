"""Abstract scheduling client interface."""
from abc import ABC, abstractmethod
from datetime import date, datetime

from app.schemas.provider import TimeSlot


class SchedulingClient(ABC):
    """Abstract interface for scheduling system integration."""

    @abstractmethod
    async def search_providers(
        self, department: str | None = None, provider_type: str | None = None
    ) -> list[dict]:
        """
        Search for providers.

        Args:
            department: Filter by department
            provider_type: Filter by provider type

        Returns:
            List of provider dictionaries
        """
        pass

    @abstractmethod
    async def get_timeslots(self, provider_id: int, target_date: date) -> list[TimeSlot]:
        """
        Get available timeslots for a provider on a specific date.

        Args:
            provider_id: Provider ID
            target_date: Target date

        Returns:
            List of available timeslots
        """
        pass

    @abstractmethod
    async def book_appointment(
        self, user_id: int, provider_id: int, slot_id: str, reason: str | None = None
    ) -> dict:
        """
        Book an appointment.

        Args:
            user_id: User ID
            provider_id: Provider ID
            slot_id: Timeslot ID
            reason: Appointment reason

        Returns:
            Booking confirmation details
        """
        pass

    @abstractmethod
    async def modify_appointment(self, appointment_id: int, new_slot_id: str) -> dict:
        """
        Modify an existing appointment.

        Args:
            appointment_id: Appointment ID
            new_slot_id: New timeslot ID

        Returns:
            Modified appointment details
        """
        pass

    @abstractmethod
    async def cancel_appointment(self, appointment_id: int) -> dict:
        """
        Cancel an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            Cancellation confirmation
        """
        pass
