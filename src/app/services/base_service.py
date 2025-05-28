# from typing import List, Optional

# from src.database.factories.feedback_factory import FeedbackModel
# from src.database.session import SessionLocal


# class FeedbackService:
#     """Service for feedback operations"""

#     @staticmethod
#     def save_feedback(
#         question: str, answer: str, feedback: str, reason: Optional[str] = None
#     ):
#         db = SessionLocal()
#         try:
#             fb = FeedbackModel(
#                 question=question, answer=answer, feedback=feedback, reason=reason
#             )
#             db.add(fb)
#             db.commit()
#             db.refresh(fb)
#             return fb
#         finally:
#             db.close()

#     @staticmethod
#     def get_feedbacks(filter_feedback: Optional[str] = None) -> List[FeedbackModel]:
#         db = SessionLocal()
#         try:
#             query = db.query(FeedbackModel)
#             if filter_feedback:
#                 query = query.filter(FeedbackModel.feedback == filter_feedback)
#             return query.order_by(FeedbackModel.created_at.desc()).all()
#         finally:
#             db.close()
