# from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func

# from src.database.factories.conversation_chat_factory import ConversationChat
# from src.database.session import Base


# class ConversationChatDetail(Base):
#     __tablename__ = "conversation_chat_detail"

#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey(ConversationChat.id), nullable=False)
#     role = Column(String, nullable=False)  # "user" or "assistant"
#     message = Column(Text, nullable=False)
#     # Rename the attribute to meta_data but keep the column name as "metadata"
#     meta_data = Column("metadata", Text, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     # Keep only one relationship definition
#     conversation = relationship("ConversationChat", backref="details")
