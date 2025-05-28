# from typing import Optional

# from fastapi import APIRouter, Depends, Query, Request

# from src.app.controllers.llm_controller import LLMController
# from src.app.models.llm_model import FeedbackRequest, QueryRequest, QueryResponse
# from src.config.security import validate_api_key

# # Define router for all endpoints
# router = APIRouter(prefix="/api/v1", dependencies=[Depends(validate_api_key)])


# @router.post("/chat/query", response_model=QueryResponse, tags=["chat"])
# async def process_query(query_request: QueryRequest, request: Request):
#     """Process a query and generate a response"""
#     stream = getattr(query_request, "stream", False)

#     if stream:
#         return await LLMController.process_streaming_query(query_request)
#     else:
#         # Process the query and get the response
#         response = await LLMController.process_query(query_request)
#         # Return the response object directly - FastAPI will handle serialization
#         return response


# @router.get("/conversations", tags=["chat"])
# async def get_conversations(user_id: Optional[str] = Query(None)):
#     """Get all conversations"""
#     return LLMController.get_conversations(user_id)


# @router.get("/conversations/{conversation_id}", tags=["chat"])
# async def get_conversation_details(conversation_id: int):
#     """Get conversation details (messages) by conversation ID"""
#     return LLMController.get_conversation_details(conversation_id)


# @router.delete("/conversations", tags=["chat"])
# async def delete_all_conversations(user_id: Optional[str] = Query(None)):
#     """Delete all conversations, optionally filtered by user_id"""
#     return LLMController.delete_all_conversations(user_id)


# @router.delete("/conversations/{conversation_id}", tags=["chat"])
# async def delete_conversation(conversation_id: int):
#     """Delete a specific conversation by ID"""
#     return LLMController.delete_conversation(conversation_id)


# @router.post("/feedback", tags=["feedback"])
# def submit_feedback(feedback_request: FeedbackRequest):
#     """Submit feedback"""
#     return LLMController.submit_feedback(feedback_request)


# @router.get("/feedbacks", tags=["feedback"])
# def get_feedbacks(filter: Optional[str] = Query(None)):
#     """Retrieve all feedbacks, optionally filtered by thumbs_up or thumbs_down"""
#     return LLMController.get_feedbacks(filter)
