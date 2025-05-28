# from typing import List, Optional

# from pydantic import BaseModel, Field

# from src.app.schemas.llm_schema import InteractionType, LLMProvider, QueryType


# class SourceResponse(BaseModel):
#     """Source document information response schema"""

#     id: str
#     score: float
#     metadata: dict = {}
#     text: str


# class InteractiveOptions(BaseModel):
#     """Interactive options for the response"""

#     type: InteractionType
#     message: str
#     options: List[str]

#     model_config = {
#         "json_encoders": {
#             InteractionType: lambda v: v.value if hasattr(v, "value") else str(v)
#         },
#         "arbitrary_types_allowed": True,
#     }

#     def model_dump(self, **kwargs):
#         """Override the default model_dump to handle enum serialization properly"""
#         return {
#             "type": self.type.value if hasattr(self.type, "value") else str(self.type),
#             "message": self.message,
#             "options": self.options,
#         }

#     def dict(self, **kwargs):
#         """Support older Pydantic versions"""
#         return self.model_dump(**kwargs)


# class QueryRequest(BaseModel):
#     """Chat query request schema"""

#     query: str
#     context_limit: int = Field(default=3, ge=1, le=100)
#     document_id: str = "all"  # "all" or specific document ID
#     provider: LLMProvider = LLMProvider.DIGITAL_OCEAN
#     debug_mode: bool = False
#     conversation_id: Optional[int] = None
#     stream: Optional[bool] = False
#     query_type: Optional[QueryType] = None  # Allow explicitly setting query type
#     connector_id: Optional[str] = (
#         None  # For SQL queries, specify the database connector
#     )
#     interactive: bool = True  # Enable interactive mode by default
#     interaction_response: Optional[str] = None  # User's response to interactive prompt
#     user_id: Optional[str] = None  # User ID for tracking purposes


# class QueryResponse(BaseModel):
#     """Chat query response schema"""

#     id: int
#     query: str
#     response: str
#     sources: List[SourceResponse] = []
#     title: str
#     timestamp: str
#     query_type: QueryType = QueryType.RAG  # Include query type in response
#     interactive_options: Optional[InteractiveOptions] = (
#         None  # Interactive response options
#     )


# class FeedbackRequest(BaseModel):
#     """Feedback request schema for API"""

#     question: str
#     answer: str
#     feedback: str  # "thumbs_up" or "thumbs_down"
#     reason: Optional[str] = None
#     reason: Optional[str] = None
#     reason: Optional[str] = None
