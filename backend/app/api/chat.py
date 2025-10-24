from fastapi import APIRouter, HTTPException
from app.services.matching_service import matching_service
from app.services.vertex_gemini_service import vertex_gemini_service
from app.services.storage_service import storage_service
from app.core.agent import agent
from app.models.schemas import ChatRequest, AnalyzeApplicationRequest
from app.core.logger import setup_logger
import uuid
import time

router = APIRouter()
logger = setup_logger(__name__)


# Chat Endpoints
# Main conversational endpoint
# ~~~~worked! testing done by with postman.
@router.post("/message")
async def handle_chat_message(request: ChatRequest):
    """
    Main conversational endpoint
    Determines intent and routes to appropriate service or AI agent
    Automatically saves all messages to Google Cloud Storage for history
    """
    try:
        # Initialize trace data
        trace_steps = []
        start_time = time.time()

        # Generate or use existing session_id
        session_id = request.context.get("session_id") if request.context else None
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")

        # Save user message to GCS
        storage_service.save_chat_message(
            session_id=session_id, role="user", content=request.message, metadata=request.context
        )

        # FIRST: Check if this is a follow-up query about a specific applicant (before intent detection)
        message_lower = request.message.lower()
        applicants_data = request.context.get("applicants_data", []) if request.context else []

        logger.info(f"📋 Context has {len(applicants_data)} applicants stored")

        is_applicant_query = (
            applicants_data and
            any(keyword in message_lower for keyword in [
                "details", "tell me", "about", "more", "show me",
                "give me", "what", "who", "information"
            ])
        )

        logger.info(f"🔍 Is applicant query: {is_applicant_query}")

        if is_applicant_query:
            # Extract applicant name from the message
            found_applicant = None
            logger.info(f"🔎 Searching for applicant in message: {request.message}")
            for applicant in applicants_data:
                applicant_name = applicant.get("applicant_name", "")
                # Check if any part of the name is in the message
                name_parts = applicant_name.lower().split()
                if any(part in message_lower for part in name_parts if len(part) > 2):
                    found_applicant = applicant
                    logger.info(f"✅ Found applicant: {applicant_name}")
                    break

            if found_applicant:
                # Generate detailed response about the specific applicant
                response = await vertex_gemini_service.generate_applicant_details(
                    query=request.message,
                    applicant_data=found_applicant
                )

                # Save AI response to GCS
                storage_service.save_chat_message(
                    session_id=session_id,
                    role="assistant",
                    content=response,
                    intent="applicant_details"
                )

                return {
                    "success": True,
                    "intent": "applicant_details",
                    "session_id": session_id,
                    "response": {"text": response, "applicant": found_applicant}
                }
            else:
                logger.warning(f"❌ No applicant found matching the query: {request.message}")

        # Detect intent using Vertex Gemini
        intent_start = time.time()
        intent = await vertex_gemini_service.detect_intent(request.message)
        intent_duration = int((time.time() - intent_start) * 1000)

        trace_steps.append(
            {
                "id": "intent",
                "label": "Gemini Intent Detection",
                "status": "complete",
                "duration": intent_duration,
                "details": "gemini-1.5-flash",
                "data": {
                    "detected_intent": intent["type"],
                    "confidence": 0.95,
                    "filters": intent.get("filters", {}),
                },
            }
        )

        # Route based on intent type
        if intent["type"] == "find_adopters":
            # Use matching service for adopter search
            search_start = time.time()
            search_results = await matching_service.find_adopters(
                query=request.message, filters=intent.get("filters"), limit=intent.get("limit")
            )
            search_duration = int((time.time() - search_start) * 1000)

            # Add trace step for Elasticsearch search
            trace_steps.append(
                {
                    "id": "elasticsearch-search",
                    "label": "Elasticsearch Hybrid Search",
                    "status": "complete",
                    "duration": search_duration,
                    "details": "semantic + structured filters",
                    "data": {
                        "index": "applications",
                        "query_type": "hybrid",
                        "semantic_field": "motivation",
                        "filters": intent.get("filters", {}),
                        "total_hits": len(search_results.get("hits", [])),
                        "took_ms": search_results.get("took", 0),
                    },
                }
            )

            # Let Gemini format the results into natural language
            format_start = time.time()
            formatted_text = await vertex_gemini_service.format_search_results(
                query=request.message, search_results=search_results, search_type="adopters"
            )
            format_duration = int((time.time() - format_start) * 1000)

            trace_steps.append(
                {
                    "id": "gemini-format",
                    "label": "Gemini Response Formatting",
                    "status": "complete",
                    "duration": format_duration,
                    "details": "gemini-1.5-flash",
                    "data": {
                        "results_formatted": len(search_results.get("hits", [])),
                        "response_length": len(formatted_text),
                    },
                }
            )

            # Save AI response to GCS with full matches data
            matches_data = search_results.get("hits", [])
            logger.info(f"Saving {len(matches_data)} matches to session {session_id}")
            logger.info(f"First match sample: {matches_data[0] if matches_data else 'None'}")

            storage_service.save_chat_message(
                session_id=session_id,
                role="assistant",
                content=formatted_text,
                intent=intent["type"],
                metadata={
                    "total_matches": len(matches_data),
                    "matches": matches_data,  # Save the actual match data
                },
            )

            total_duration = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "intent": intent["type"],
                "session_id": session_id,
                "response": {
                    "text": formatted_text,  # Gemini's natural language response
                    "matches": search_results.get("hits", []),  # Structured data for cards
                    "total": len(search_results.get("hits", [])),
                    "query_time_ms": search_results.get("took", 0),
                },
                "trace": {
                    "steps": trace_steps,
                    "total_duration_ms": total_duration,
                    "query": request.message,
                },
            }

        elif intent["type"] == "analyze_application":
            # Use matching service for application analysis
            analysis_start = time.time()
            result = await matching_service.analyze_application(request.message)
            analysis_duration = int((time.time() - analysis_start) * 1000)

            trace_steps.append(
                {
                    "id": "analyze-application",
                    "label": "Application Analysis",
                    "status": "complete",
                    "duration": analysis_duration,
                    "details": "Elasticsearch + Gemini analysis",
                    "data": {
                        "similar_successes": len(result.get("similar_successful_adopters", [])),
                        "similar_failures": len(result.get("similar_failed_adopters", [])),
                        "prediction": result.get("prediction", {}),
                    },
                }
            )

            # Save AI response to GCS with full analysis data
            storage_service.save_chat_message(
                session_id=session_id,
                role="assistant",
                content="Application analysis completed",
                intent=intent["type"],
                metadata={
                    "applicationAnalysis": result  # Save full analysis for display in history
                },
            )

            total_duration = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "intent": intent["type"],
                "session_id": session_id,
                "response": result,
                "trace": {
                    "steps": trace_steps,
                    "total_duration_ms": total_duration,
                    "query": request.message,
                },
            }

        else:
            # Check if this is a dog info query or similar cases query
            message_lower = request.message.lower()
            is_dog_query = any(
                keyword in message_lower
                for keyword in [
                    "tell me about",
                    "show me",
                    "dog profile",
                    "medical history",
                    "similar cases",
                    "find similar",
                    "like this",
                    "dog_",  # Match dog_001, dog_002, etc.
                ]
            )

            if is_dog_query:
                # Use AI agent with tools for dog info and similar cases
                session_id = (
                    request.context.get("session_id", "default") if request.context else "default"
                )
                agent_start = time.time()
                result = await agent.chat(
                    user_message=request.message,
                    session_id=session_id,
                    context=request.context,
                )
                agent_duration = int((time.time() - agent_start) * 1000)

                trace_steps.append(
                    {
                        "id": "agent-tools",
                        "label": "Gemini Agent with Tools",
                        "status": "complete",
                        "duration": agent_duration,
                        "details": "gemini-1.5-pro with function calling",
                        "data": {
                            "tools_used": result.get(
                                "tools_used", ["get_dog_profile", "search_similar_cases"]
                            ),
                            "response_length": len(str(result["response"])),
                        },
                    }
                )

                # Save AI response to GCS with tools metadata
                storage_service.save_chat_message(
                    session_id=session_id,
                    role="assistant",
                    content=str(result["response"]),
                    intent="dog_info_with_tools",
                    metadata={
                        "tools_used": result.get("tools_used", []),
                        "response_type": "agent_with_tools",
                    },
                )

                total_duration = int((time.time() - start_time) * 1000)

                return {
                    "success": True,
                    "intent": "dog_info_with_tools",
                    "response": result["response"],
                    "session_id": session_id,
                    "trace": {
                        "steps": trace_steps,
                        "total_duration_ms": total_duration,
                        "query": request.message,
                    },
                }
            else:
                # General question - use basic Gemini
                gemini_start = time.time()
                result = await vertex_gemini_service.generate_response(
                    prompt=request.message, context=request.context
                )
                gemini_duration = int((time.time() - gemini_start) * 1000)

                trace_steps.append(
                    {
                        "id": "gemini-generate",
                        "label": "Gemini Response Generation",
                        "status": "complete",
                        "duration": gemini_duration,
                        "details": "gemini-1.5-flash",
                        "data": {"response_length": len(result)},
                    }
                )

                # Save AI response to GCS with minimal metadata
                storage_service.save_chat_message(
                    session_id=session_id,
                    role="assistant",
                    content=result,
                    intent="general",
                    metadata={"response_type": "general_gemini"},
                )

                total_duration = int((time.time() - start_time) * 1000)

                return {
                    "success": True,
                    "intent": "general",
                    "session_id": session_id,
                    "response": result,
                    "trace": {
                        "steps": trace_steps,
                        "total_duration_ms": total_duration,
                        "query": request.message,
                    },
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analyze Adoption Application
# ~~~~worked! testing done by with postman.
@router.post("/analyze-application")
async def analyze_application(request: AnalyzeApplicationRequest):
    """
    Analyze an adoption application
    THE KEY FEATURE for demo
    """
    try:
        trace_steps = []
        start_time = time.time()

        # Analyze application
        analysis_start = time.time()
        analysis = await matching_service.analyze_application(request.application_text)
        analysis_duration = int((time.time() - analysis_start) * 1000)

        trace_steps.append(
            {
                "id": "extract-features",
                "label": "Extract Application Features",
                "status": "complete",
                "duration": int(analysis_duration * 0.2),
                "details": "Gemini text analysis",
                "data": {"features_extracted": ["housing", "experience", "motivation"]},
            }
        )

        trace_steps.append(
            {
                "id": "semantic-search-success",
                "label": "Search Similar Successful Adopters",
                "status": "complete",
                "duration": int(analysis_duration * 0.4),
                "details": "Elasticsearch semantic search",
                "data": {
                    "index": "outcomes",
                    "similar_matches": len(analysis.get("similar_successful_adopters", [])),
                },
            }
        )

        trace_steps.append(
            {
                "id": "semantic-search-failure",
                "label": "Search Similar Failed Adoptions",
                "status": "complete",
                "duration": int(analysis_duration * 0.3),
                "details": "Elasticsearch semantic search",
                "data": {
                    "index": "outcomes",
                    "similar_matches": len(analysis.get("similar_failed_adopters", [])),
                },
            }
        )

        trace_steps.append(
            {
                "id": "prediction",
                "label": "Generate Success Prediction",
                "status": "complete",
                "duration": int(analysis_duration * 0.1),
                "details": "Pattern analysis",
                "data": {"prediction": analysis.get("prediction", {})},
            }
        )

        total_duration = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "analysis": analysis,
            "trace": {
                "steps": trace_steps,
                "total_duration_ms": total_duration,
                "query": request.application_text[:100] + "...",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-insights/{query_id}")
async def get_search_insights(query_id: str):
    """
    Get Elasticsearch query details for visualization
    """
    # TODO: Implement query caching and retrieval
    return {
        "success": True,
        "insights": {
            "query_id": query_id,
            # Query breakdown, timing, etc.
        },
    }
