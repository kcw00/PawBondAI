from typing import Dict, Any, List, Callable
from app.services.elasticsearch_service import es_service


# Tool 1: Get Dog Profile
async def get_dog_profile(dog_id: str) -> Dict[str, Any]:
    """
    Retrieve complete dog profile including medical history, behavioral notes, and adoption status.
    """
    dog = await es_service.get_dog_profile(dog_id)

    if not dog:
        return {
            "tool": "get_dog_profile",
            "success": False,
            "error": f"Dog with ID '{dog_id}' not found in the system",
            "dog_id": dog_id,
        }

    # Format medical events
    formatted_medical_events = []
    for event in dog.get("medical_events", []):
        formatted_medical_events.append(
            {
                "date": event.get("date"),
                "event_type": event.get("event_type"),
                "condition": event.get("condition"),
                "treatment": event.get("treatment", "N/A"),
                "severity": event.get("severity"),
                "outcome": event.get("outcome"),
            }
        )

    return {
        "tool": "get_dog_profile",
        "success": True,
        "dog_id": dog_id,
        "basic_info": {
            "name": dog.get("name"),
            "breed": dog.get("breed", "Mixed"),
            "age": dog.get("age"),
            "sex": dog.get("sex"),
            "weight_kg": dog.get("weight_kg"),
        },
        "medical_info": {
            "medical_history": dog.get("medical_history"),
            "current_conditions": dog.get("current_conditions", []),
            "past_conditions": dog.get("past_conditions", []),
            "medical_events": formatted_medical_events,
            "adoption_readiness": dog.get("adoption_readiness"),
        },
        "behavioral_info": {
            "personality_traits": dog.get("personality_traits"),
            "behavioral_notes": dog.get("behavioral_notes"),
        },
        "adoption_info": {
            "status": dog.get("status"),
            "rescue_organization": dog.get("rescue_organization"),
            "intake_date": dog.get("intake_date"),
        },
    }


# Tool 2: Search Similar Cases
async def search_similar_cases(symptoms: List[str], species: str = "dog") -> Dict[str, Any]:
    """
    Find similar medical cases or adoption outcomes using vector similarity search.
    Returns historical cases that can help predict adoption success.
    """
    if not symptoms or len(symptoms) == 0:
        return {
            "tool": "search_similar_cases",
            "success": False,
            "error": "No symptoms provided. Please specify conditions, behaviors, or traits to search for.",
        }

    try:
        # Search case studies index for similar medical cases
        cases = await es_service.vector_search_cases(symptoms, size=10)

        # Filter by species
        cases = [c for c in cases if c.get("species", "dog") == species]

        formatted_cases = []
        for case in cases[:5]:  # Limit to top 5 results
            formatted_cases.append(
                {
                    "case_id": case.get("case_id"),
                    "symptoms": case.get("symptoms", []),
                    "diagnosis": case.get("diagnosis"),
                    "treatment": case.get("treatment"),
                    "outcome": case.get("outcome"),
                    "rescue_organization": case.get("rescue_organization"),
                    "origin_country": case.get("origin_country", "Unknown"),
                }
            )

        return {
            "tool": "search_similar_cases",
            "success": True,
            "query_symptoms": symptoms,
            "cases_found": len(formatted_cases),
            "cases": formatted_cases,
            "message": f"Found {len(formatted_cases)} similar cases based on: {', '.join(symptoms)}",
        }
    except Exception as e:
        return {
            "tool": "search_similar_cases",
            "success": False,
            "error": f"Error searching similar cases: {str(e)}",
            "query_symptoms": symptoms,
        }


# Export tool registry for AI agent
TOOL_REGISTRY: Dict[str, Callable] = {
    "get_dog_profile": get_dog_profile,
    "search_similar_cases": search_similar_cases,
}
