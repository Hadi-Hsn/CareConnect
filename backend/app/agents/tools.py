"""Tool definitions for OpenAI function calling."""
from typing import Any

# Tool schemas following OpenAI function calling format
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_timeslots",
            "description": "Find available appointment timeslots for a specific provider or department on a given date",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "integer",
                        "description": "The ID of the specific provider (doctor, specialist, etc.)",
                    },
                    "department": {
                        "type": "string",
                        "description": "The department name (e.g., 'Cardiology', 'Radiology', 'Primary Care')",
                    },
                    "date": {
                        "type": "string",
                        "description": "The date to check availability for, in YYYY-MM-DD format. You must calculate this from relative dates like 'Thursday', 'tomorrow', 'next week', etc. based on the current date.",
                    },
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the authenticated user with a specific provider at a specific timeslot. Only call this after the user has confirmed they want to book. DO NOT include user_id - it is automatically provided from authentication.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "integer",
                        "description": "The ID of the provider for the appointment",
                    },
                    "slot_id": {
                        "type": "string",
                        "description": "The ID of the timeslot to book (from search_timeslots results)",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for the appointment",
                    },
                },
                "required": ["provider_id", "slot_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "modify_appointment",
            "description": "Modify an existing appointment to a new timeslot",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the appointment to modify",
                    },
                    "new_slot_id": {
                        "type": "string",
                        "description": "The ID of the new timeslot",
                    },
                },
                "required": ["appointment_id", "new_slot_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment. If the user provides a confirmation code instead of an appointment ID, you must first call get_user_appointments to find the appointment with that confirmation code, then use its appointment_id to cancel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the appointment to cancel. This is NOT the confirmation code - it's the numeric appointment ID from get_user_appointments.",
                    },
                },
                "required": ["appointment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email_confirmation",
            "description": "Send an email confirmation for an appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the appointment to send confirmation for",
                    },
                },
                "required": ["appointment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rag_lookup",
            "description": "Look up facility information including directions, parking, department hours, lab test preparations, and FAQs. Use this for any question about the facility.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to look up information about",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_appointments",
            "description": "Retrieve the authenticated user's appointments. Returns upcoming and recent past appointments with details including provider, time, location, and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["upcoming", "past", "all"],
                        "description": "Filter appointments by status: 'upcoming' for future appointments, 'past' for completed/cancelled appointments, 'all' for both. Defaults to 'upcoming'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of appointments to return. Defaults to 10.",
                    },
                },
                "required": [],
            },
        },
    },
]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """Get tool definition by name."""
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None
