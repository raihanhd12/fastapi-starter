# import json
# import logging
# from typing import Any, Dict, List, Optional

# from src.database.factories.conversation_chat_detail import ConversationChatDetail
# from src.database.factories.conversation_chat_factory import ConversationChat
# from src.database.session import get_db

# # Configure logger
# logger = logging.getLogger(__name__)


# class DatabaseService:
#     """Database service for conversation chat operations"""

#     @classmethod
#     def create_conversation(cls, title: str, user_id: Optional[str] = None) -> int:
#         """Create a new conversation"""
#         with get_db() as db:
#             conversation = ConversationChat(title=title, user_id=user_id)
#             db.add(conversation)
#             db.commit()
#             db.refresh(conversation)
#             return conversation.id

#     @classmethod
#     def add_message_to_conversation(
#         cls,
#         conversation_id: int,
#         role: str,
#         message: str,
#         metadata: Optional[Dict[str, Any]] = None,
#     ):
#         # Handle case where conversation_id might be a tuple
#         if isinstance(conversation_id, tuple):
#             conversation_id = conversation_id[0] if conversation_id else None

#         if conversation_id is None:
#             raise ValueError("conversation_id cannot be None")

#         with get_db() as db:
#             # Convert metadata to JSON string if provided
#             metadata_str = json.dumps(metadata) if metadata else None

#             chat_detail = ConversationChatDetail(
#                 conversation_id=conversation_id,
#                 role=role,
#                 message=message,
#                 metadata=metadata_str,
#             )
#             db.add(chat_detail)
#             db.commit()
#             db.refresh(chat_detail)
#             return chat_detail

#     @classmethod
#     def get_all_conversations(
#         cls, user_id: Optional[str] = None
#     ) -> List[ConversationChat]:
#         """Get all conversations, optionally filtered by user_id"""
#         with get_db() as db:
#             query = db.query(ConversationChat)

#             # Filter by user_id if provided
#             if user_id:
#                 query = query.filter(ConversationChat.user_id == user_id)

#             return query.order_by(ConversationChat.created_at.desc()).all()

#     @classmethod
#     def get_conversation_details(
#         cls, conversation_id: int
#     ) -> List[ConversationChatDetail]:
#         with get_db() as db:
#             details = (
#                 db.query(ConversationChatDetail)
#                 .filter(ConversationChatDetail.conversation_id == conversation_id)
#                 .order_by(ConversationChatDetail.created_at.asc())
#                 .all()
#             )
#             return details

#     @classmethod
#     def get_conversation_history(cls, conversation_id: int) -> list[dict]:
#         with get_db() as db:
#             messages = (
#                 db.query(ConversationChatDetail)
#                 .filter(ConversationChatDetail.conversation_id == conversation_id)
#                 .order_by(ConversationChatDetail.created_at.asc())
#                 .all()
#             )
#         if not messages:
#             return []

#         return [{"role": m.role, "message": m.message} for m in messages]

#     @classmethod
#     def update_conversation_title(cls, conversation_id: int, new_title: str):
#         """Update the title of an existing conversation"""
#         with get_db() as db:
#             conversation = (
#                 db.query(ConversationChat)
#                 .filter(ConversationChat.id == conversation_id)
#                 .first()
#             )
#             if conversation:
#                 conversation.title = new_title
#                 db.commit()

#     @classmethod
#     def get_last_assistant_message(
#         cls, conversation_id: int
#     ) -> Optional[ConversationChatDetail]:
#         """Get the last assistant message in a conversation"""
#         with get_db() as db:
#             last_message = (
#                 db.query(ConversationChatDetail)
#                 .filter(
#                     ConversationChatDetail.conversation_id == conversation_id,
#                     ConversationChatDetail.role == "assistant",
#                 )
#                 .order_by(ConversationChatDetail.created_at.desc())
#                 .first()
#             )
#             return last_message

#     @classmethod
#     def update_message_metadata(cls, message_id: int, metadata: Dict[str, Any]) -> bool:
#         """Update the metadata of a specific message"""
#         with get_db() as db:
#             message = db.query(ConversationChatDetail).get(message_id)
#             if message:
#                 # Fix: Gunakan meta_data bukan metadata (sesuai definisi di model)
#                 existing_metadata = {}
#                 if (
#                     message.meta_data
#                 ):  # Changed from message.metadata to message.meta_data
#                     try:
#                         if isinstance(message.meta_data, str):
#                             existing_metadata = json.loads(message.meta_data)
#                         elif isinstance(message.meta_data, dict):
#                             existing_metadata = message.meta_data
#                     except json.JSONDecodeError:
#                         # If metadata is invalid JSON, just replace it
#                         pass

#                 # Merge and update
#                 existing_metadata.update(metadata)
#                 message.meta_data = json.dumps(
#                     existing_metadata
#                 )  # Changed from message.metadata to message.meta_data
#                 db.commit()
#                 return True
#             return False

#     @classmethod
#     def conversation_exists(cls, conversation_id: int) -> bool:
#         """Check if a conversation with the given ID exists"""
#         with get_db() as db:
#             conversation = (
#                 db.query(ConversationChat)
#                 .filter(ConversationChat.id == conversation_id)
#                 .first()
#             )
#             return conversation is not None

#     @classmethod
#     def delete_conversation(cls, conversation_id: int) -> bool:
#         """Delete a specific conversation by ID"""
#         with get_db() as db:
#             try:
#                 # First delete all conversation details
#                 db.query(ConversationChatDetail).filter(
#                     ConversationChatDetail.conversation_id == conversation_id
#                 ).delete()

#                 # Then delete the conversation
#                 conversation = (
#                     db.query(ConversationChat)
#                     .filter(ConversationChat.id == conversation_id)
#                     .first()
#                 )
#                 if conversation:
#                     db.delete(conversation)
#                     db.commit()
#                     return True
#                 return False
#             except Exception as e:
#                 db.rollback()
#                 logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
#                 return False

#     @classmethod
#     def delete_all_conversations(cls, user_id: Optional[str] = None) -> int:
#         """Delete all conversations, optionally filtered by user_id"""
#         with get_db() as db:
#             try:
#                 # Build the filter
#                 conversations_filter = []
#                 if user_id:
#                     conversations_filter.append(ConversationChat.user_id == user_id)

#                 # Get conversation IDs to delete
#                 conversation_ids = [
#                     c.id
#                     for c in db.query(ConversationChat.id)
#                     .filter(*conversations_filter)
#                     .all()
#                 ]

#                 if not conversation_ids:
#                     return 0

#                 # Delete all conversation details first
#                 db.query(ConversationChatDetail).filter(
#                     ConversationChatDetail.conversation_id.in_(conversation_ids)
#                 ).delete(synchronize_session=False)

#                 # Then delete conversations
#                 deleted_count = (
#                     db.query(ConversationChat)
#                     .filter(ConversationChat.id.in_(conversation_ids))
#                     .delete(synchronize_session=False)
#                 )

#                 db.commit()
#                 return deleted_count
#             except Exception as e:
#                 db.rollback()
#                 logger.error(f"Error deleting conversations: {str(e)}")
#                 raise
