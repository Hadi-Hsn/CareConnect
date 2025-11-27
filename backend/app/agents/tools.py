"""
Production-Ready Tool Definitions for OpenAI GPT-4+ Function Calling
Follows strict JSON Schema validation and OpenAI best practices
"""
from typing import Any

# Tool schemas following OpenAI function calling format
# Each tool has:
# 1. Clear, unambiguous description
# 2. Strict parameter typing
# 3. Required field enforcement
# 4. Examples in descriptions
# 5. No business logic (schemas only)

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_timeslots",
            "description": (
                "Search for available appointment time slots on a specific date. "
                "Returns list of providers with their available time slots. "
                "Each slot includes: slot_id, start time, end time. "
                "Use when user mentions a date or asks about availability. "
                "REQUIRED: date in YYYY-MM-DD format (calculate from relative dates). "
                "OPTIONAL: Specify EITHER provider_id OR department, NOT both."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                        "description": (
                            "Date to search for availability in YYYY-MM-DD format. "
                            "You MUST convert relative dates: 'tomorrow', 'next Monday', 'Thursday' -> YYYY-MM-DD. "
                            "Example: If today is 2025-11-20 and user says 'tomorrow', use '2025-11-21'."
                        ),
                    },
                    "provider_id": {
                        "type": "integer",
                        "description": (
                            "Specific provider ID to search. "
                            "Use when user requests a specific doctor by name. "
                            "Get provider_id from previous search results or get_user_appointments. "
                            "MUTUALLY EXCLUSIVE with 'department' parameter."
                        ),
                    },
                    "department": {
                        "type": "string",
                        "description": (
                            "Department name to search: 'Cardiology', 'Radiology', 'Orthopedics', etc. "
                            "Use when user mentions a specialty or department. "
                            "Returns all providers in that department with availability. "
                            "MUTUALLY EXCLUSIVE with 'provider_id' parameter."
                        ),
                    },
                },
                "required": ["date"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book a new medical appointment for the authenticated user. "
                "Reserves a specific time slot with a specific provider. "
                "Returns: appointment_id, confirmation_code, datetime, status. "
                "CRITICAL: Only call AFTER user confirms they want to book. "
                "NEVER call if user is asking about modifying/canceling existing appointment. "
                "User authentication is automatic - DO NOT ask for user_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "integer",
                        "description": (
                            "ID of the provider (doctor/specialist) for this appointment. "
                            "MUST match a provider_id from search_timeslots results. "
                            "NEVER guess or use arbitrary values."
                        ),
                    },
                    "slot_id": {
                        "type": "string",
                        "pattern": "^slot_\\d+_\\d{4}-\\d{2}-\\d{2}_\\d+$",
                        "description": (
                            "ID of the time slot to book. "
                            "Format: 'slot_PROVIDERID_YYYY-MM-DD_N' (e.g., 'slot_12_2025-11-21_3'). "
                            "Provider ID embedded in the slot ensures bookings cannot mismatch doctors. "
                            "MUST be returned by search_timeslots for the same provider. "
                            "NEVER construct manually."
                        ),
                    },
                    "reason": {
                        "type": "string",
                        "maxLength": 500,
                        "description": (
                            "Optional reason for the appointment. "
                            "Examples: 'Annual checkup', 'Follow-up visit', 'New patient consultation'. "
                            "Include if user provides it."
                        ),
                    },
                },
                "required": ["provider_id", "slot_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "modify_appointment",
            "description": (
                "Change an existing appointment to a new time slot. "
                "CRITICAL: You MUST call get_user_appointments FIRST to get the real appointment_id. "
                "NEVER guess or make up appointment_id - it must come from get_user_appointments results. "
                "Typical appointment_id values are small integers like 1, 2, 3, etc. "
                "Workflow: 1) get_user_appointments → 2) search_timeslots for new time → 3) modify_appointment"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": (
                            "Numeric ID of the appointment to modify (small integer like 1, 2, 3). "
                            "MUST come from get_user_appointments results - NEVER guess this value. "
                            "This is NOT the confirmation code (which is alphanumeric like 'ABC123XYZ'). "
                            "Field name in get_user_appointments results: 'appointment_id'."
                        ),
                    },
                    "new_slot_id": {
                        "type": "string",
                        "pattern": "^slot_\\d+_\\d{4}-\\d{2}-\\d{2}_\\d+$",
                        "description": (
                            "ID of the new time slot. "
                            "Format: 'slot_PROVIDERID_YYYY-MM-DD_N'. "
                            "The PROVIDERID must match the original appointment's provider. "
                            "MUST come from search_timeslots results for the same provider."
                        ),
                    },
                },
                "required": ["appointment_id", "new_slot_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": (
                "Cancel an existing appointment permanently. "
                "CRITICAL: You MUST call get_user_appointments FIRST to get the real appointment_id. "
                "NEVER guess or make up appointment_id - it must come from get_user_appointments results. "
                "Always confirm cancellation details with user before calling."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": (
                            "Numeric ID of the appointment to cancel (small integer like 1, 2, 3). "
                            "MUST come from get_user_appointments results - NEVER guess this value. "
                            "Field name in get_user_appointments results: 'appointment_id'."
                        ),
                    },
                },
                "required": ["appointment_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email_confirmation",
            "description": (
                "Send email confirmation for an appointment to the user. "
                "Automatically sends after successful booking, so ONLY call manually "
                "if user explicitly requests a resend. "
                "REQUIRED: appointment_id (get from booking result or get_user_appointments)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": (
                            "Numeric ID of the appointment to send confirmation for. "
                            "Get from book_appointment result or get_user_appointments."
                        ),
                    },
                },
                "required": ["appointment_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rag_lookup",
            "description": (
                "Look up facility information using retrieval-augmented generation (RAG). "
                "Returns relevant information from facility documents including: "
                "directions, parking, department hours, lab test preparations, FAQs, policies. "
                "Use when user asks about: 'where to park', 'how to get there', "
                "'lab test instructions', 'department hours', 'facility information'. "
                "DO NOT use for medical advice or diagnosis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 500,
                        "description": (
                            "The question or topic to search for. "
                            "Be specific and include key terms. "
                            "Examples: 'parking for visitors', 'radiology department hours', "
                            "'preparation for cholesterol test', 'how to get to main entrance'."
                        ),
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_appointments",
            "description": (
                "Retrieve the authenticated user's medical appointments. "
                "Returns a list with appointment details including: appointment_id, confirmation_code, "
                "provider name, department, date, time, status, and reason. "
                "Use this when user asks about their schedule, upcoming visits, or past appointments. "
                "CRITICAL: Always call this FIRST when user wants to cancel/modify by confirmation code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["upcoming", "past", "all"],
                        "description": (
                            "Filter appointments by status. "
                            "'upcoming' = future scheduled/confirmed appointments (default). "
                            "'past' = completed or cancelled appointments. "
                            "'all' = both upcoming and past."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "description": (
                            "Maximum number of appointments to return. "
                            "Defaults to 10. Useful for 'show me all my appointments'."
                        ),
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_providers",
            "description": (
                "List doctors/providers in a specific department. "
                "Returns provider names, specialties, and IDs for booking. "
                "Use when user asks: 'who are the doctors in X department', "
                "'list doctors in cardiology', 'show me rheumatology specialists'. "
                "This queries the actual database - use this instead of guessing doctor names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": (
                            "Department name to search, e.g., 'Cardiology', 'Rheumatology', 'Radiology'. "
                            "Case-insensitive partial match supported."
                        ),
                    },
                },
                "required": ["department"],
                "additionalProperties": False,
            },
        },
    },
]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """
    Get tool definition by name.
    
    Args:
        name: Tool function name
        
    Returns:
        Tool definition dict or None if not found
    """
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None


def validate_tool_arguments(tool_name: str, arguments: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Validate tool arguments against schema.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments dict to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    tool = get_tool_by_name(tool_name)
    if not tool:
        return False, f"Unknown tool: {tool_name}"
    
    schema = tool["function"]["parameters"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # Check required fields
    for field in required:
        if field not in arguments:
            return False, f"Missing required field: {field}"
    
    # Check for unexpected fields
    if schema.get("additionalProperties") is False:
        for field in arguments:
            if field not in properties:
                return False, f"Unexpected field: {field}"
    
    # Type checking (basic)
    for field, value in arguments.items():
        if field not in properties:
            continue
            
        expected_type = properties[field].get("type")
        if expected_type == "string" and not isinstance(value, str):
            return False, f"Field '{field}' must be string, got {type(value).__name__}"
        elif expected_type == "integer" and not isinstance(value, int):
            return False, f"Field '{field}' must be integer, got {type(value).__name__}"
        
        # Pattern validation for strings
        if expected_type == "string" and "pattern" in properties[field]:
            import re
            pattern = properties[field]["pattern"]
            if not re.match(pattern, value):
                return False, f"Field '{field}' does not match required pattern: {pattern}"
    
    return True, None
