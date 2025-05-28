# import json
# import logging
# from enum import Enum
# from typing import Any, Dict, List, Optional

# from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
# from fastapi.responses import StreamingResponse

# from src.app.models.llm_model import (
#     FeedbackRequest,
#     InteractiveOptions,
#     QueryRequest,
#     QueryResponse,
#     SourceResponse,
# )
# from src.app.schemas.llm_schema import QueryType
# from src.app.services.database_service import DatabaseService
# from src.app.services.feedback_service import FeedbackService
# from src.app.services.llm_service import LLMService

# logger = logging.getLogger(__name__)


# # Define a custom JSON encoder to handle Enums properly and prevent recursion
# class EnumJsonEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Enum):
#             return obj.value
#         return super().default(obj)


# class LLMController:
#     """Controller for conversation chat-related operations"""

#     @staticmethod
#     def get_conversations(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
#         """Get all conversation titles, optionally filtered by user_id"""
#         conversations = DatabaseService.get_all_conversations(user_id)
#         return [
#             {
#                 "id": conv.id,
#                 "title": conv.title,
#                 "user_id": conv.user_id,
#                 "created_at": conv.created_at.isoformat(),
#             }
#             for conv in conversations
#         ]

#     @staticmethod
#     def get_conversation_details(conversation_id: int) -> List[Dict[str, Any]]:
#         """Get full conversation (messages) by conversation ID"""
#         messages = DatabaseService.get_conversation_details(conversation_id)
#         return [
#             {
#                 "id": msg.id,
#                 "role": msg.role,
#                 "message": msg.message,
#                 "created_at": msg.created_at.isoformat(),
#                 "metadata": (
#                     msg.meta_data if hasattr(msg, "meta_data") else None
#                 ),  # Changed from metadata to meta_data
#             }
#             for msg in messages
#         ]

#     @classmethod
#     def delete_all_conversations(cls, user_id: Optional[str] = None):
#         """Delete all conversations, optionally filtered by user_id"""
#         try:
#             deleted_count = DatabaseService.delete_all_conversations(user_id)
#             return {
#                 "status": "success",
#                 "message": f"Successfully deleted {deleted_count} conversations",
#                 "deleted_count": deleted_count,
#             }
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to delete conversations: {str(e)}",
#             )

#     @classmethod
#     def delete_conversation(cls, conversation_id: int):
#         """Delete a specific conversation by ID"""
#         # Verify conversation exists
#         if not DatabaseService.conversation_exists(conversation_id):
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Conversation with ID {conversation_id} not found",
#             )

#         success = DatabaseService.delete_conversation(conversation_id)

#         if success:
#             return {
#                 "status": "success",
#                 "message": f"Conversation with ID {conversation_id} deleted successfully",
#             }
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to delete conversation with ID {conversation_id}",
#             )

#     @classmethod
#     async def process_query(cls, query_request: QueryRequest, stream_callback=None):
#         """Process a user query with interactive mode support"""
#         if query_request.conversation_id == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Invalid conversation ID: 0",
#             )

#         logger.info(f"Processing query: {query_request.query}")

#         # Process query with interactive mode
#         response_data = LLMService.process_interactive_query(
#             query=query_request.query,
#             context_limit=query_request.context_limit,
#             selected_doc_id=query_request.document_id,
#             llm_provider=query_request.provider,
#             stream_callback=stream_callback,
#             debug_mode=query_request.debug_mode,
#             conversation_id=query_request.conversation_id,
#             query_type=query_request.query_type,
#             connector_id=query_request.connector_id,
#             interactive=query_request.interactive,
#             interaction_response=query_request.interaction_response,
#             user_id=query_request.user_id,
#         )

#         # Convert sources
#         sources = [
#             SourceResponse(**source) for source in response_data.get("sources", [])
#         ]

#         # Create response object
#         response = QueryResponse(
#             id=response_data["id"],
#             query=response_data["query"],
#             response=response_data["response"],
#             sources=sources,
#             title=response_data["title"],
#             timestamp=response_data["timestamp"],
#             query_type=response_data.get("query_type", QueryType.RAG),
#         )

#         # Add interactive options if present
#         if "interactive_options" in response_data:
#             interactive_opts = response_data["interactive_options"]
#             # Create a proper InteractiveOptions object, ensuring type is properly handled
#             response.interactive_options = InteractiveOptions(
#                 type=interactive_opts["type"],
#                 message=interactive_opts["message"],
#                 options=interactive_opts["options"],
#             )

#         return response

#     @classmethod
#     async def handle_websocket_connection(cls, websocket: WebSocket):
#         """Handle WebSocket connection and streaming for chat queries"""
#         try:
#             while True:
#                 # Receive query from client
#                 data = await websocket.receive_text()
#                 query_data = json.loads(data)

#                 # Check conversation_id before processing
#                 if query_data.get("conversation_id") == 0:
#                     await websocket.send_json(
#                         {
#                             "status": "error",
#                             "code": 404,
#                             "message": "Invalid conversation ID: 0",
#                         }
#                     )
#                     return

#                 query_request = QueryRequest(**query_data)

#                 # Setup queue for streaming responses
#                 from asyncio import Queue

#                 queue = Queue()

#                 def stream_callback(new_content):
#                     """Callback for streaming content chunks"""
#                     queue.put_nowait(new_content)

#                 # Send start message
#                 await websocket.send_json({"status": "started"})

#                 import asyncio

#                 async def generate_response():
#                     response_data = await asyncio.to_thread(
#                         LLMService.process_interactive_query,
#                         query=query_request.query,
#                         context_limit=query_request.context_limit,
#                         selected_doc_id=query_request.document_id,
#                         llm_provider=query_request.provider,
#                         stream_callback=stream_callback,
#                         debug_mode=query_request.debug_mode,
#                         conversation_id=query_request.conversation_id,
#                         query_type=query_request.query_type,
#                         connector_id=query_request.connector_id,
#                         interactive=query_request.interactive,
#                         interaction_response=query_request.interaction_response,
#                         user_id=query_request.user_id,
#                     )
#                     await queue.put({"__final_data__": response_data})

#                 # Start processing in background
#                 asyncio.create_task(generate_response())

#                 # Stream content to client
#                 while True:
#                     chunk = await queue.get()
#                     if isinstance(chunk, dict) and "__final_data__" in chunk:
#                         response_data = chunk["__final_data__"]
#                         await websocket.send_json(
#                             {"status": "complete", "data": response_data}
#                         )
#                         break
#                     else:
#                         await websocket.send_json(
#                             {"status": "streaming", "content": chunk}
#                         )

#         except WebSocketDisconnect:
#             logger.info("Client disconnected from WebSocket")
#         except Exception as e:
#             logger.error(f"Error in WebSocket: {str(e)}")
#             await websocket.send_json({"status": "error", "message": str(e)})

#     @classmethod
#     async def process_streaming_query(cls, query_request: QueryRequest):
#         """Process a query with streaming response"""
#         if query_request.conversation_id == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Invalid conversation ID: 0",
#             )

#         async def event_generator():
#             from asyncio import Queue

#             queue = Queue()

#             # Initialize conversation
#             conversation_id = query_request.conversation_id

#             def stream_callback(new_content):
#                 queue.put_nowait(new_content)

#             yield 'data: {"status": "started"}\n\n'

#             import asyncio

#             async def generate_response():
#                 response_data = await asyncio.to_thread(
#                     LLMService.process_interactive_query,
#                     query=query_request.query,
#                     context_limit=query_request.context_limit,
#                     selected_doc_id=query_request.document_id,
#                     llm_provider=query_request.provider,
#                     stream_callback=stream_callback,
#                     debug_mode=query_request.debug_mode,
#                     conversation_id=conversation_id,
#                     query_type=query_request.query_type,
#                     connector_id=query_request.connector_id,
#                     interactive=query_request.interactive,
#                     interaction_response=query_request.interaction_response,
#                 )
#                 await queue.put({"__final_data__": response_data})

#             asyncio.create_task(generate_response())

#             while True:
#                 chunk = await queue.get()
#                 if isinstance(chunk, dict) and "__final_data__" in chunk:
#                     response_data = chunk["__final_data__"]

#                     # For new conversations, the title is already set by LLMService
#                     conversation_id = response_data.get("id")

#                     yield f"data: {json.dumps({'status': 'complete', 'data': response_data}, cls=EnumJsonEncoder)}\n\n"
#                     break
#                 else:
#                     yield f"data: {json.dumps({'status': 'streaming', 'content': chunk}, cls=EnumJsonEncoder)}\n\n"

#         return StreamingResponse(event_generator(), media_type="text/event-stream")

#     @staticmethod
#     def submit_feedback(feedback_request: FeedbackRequest):
#         """Process and save feedback"""
#         FeedbackService.save_feedback(
#             question=feedback_request.question,
#             answer=feedback_request.answer,
#             feedback=feedback_request.feedback,
#             reason=feedback_request.reason,
#         )
#         return {"message": "Feedback submitted successfully"}

#     @staticmethod
#     def get_feedbacks(filter_feedback: Optional[str] = None):
#         """Retrieve all feedbacks, optionally filtered"""
#         feedbacks = FeedbackService.get_feedbacks(filter_feedback)
#         return [
#             {
#                 "id": fb.id,
#                 "question": fb.question,
#                 "answer": fb.answer,
#                 "feedback": fb.feedback,
#                 "reason": fb.reason,
#                 "created_at": fb.created_at.isoformat(),
#             }
#             for fb in feedbacks
#         ]
