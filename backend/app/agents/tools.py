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
                        "description": "The date to check availability for, in YYYY-MM-DD format",
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
            "description": "Book an appointment for a user with a specific provider at a specific timeslot. Only call this after the user has confirmed they want to book.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The ID of the user booking the appointment",
                    },
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
                "required": ["user_id", "provider_id", "slot_id"],
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
            "description": "Cancel an existing appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the appointment to cancel",
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
]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """Get tool definition by name."""
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None
