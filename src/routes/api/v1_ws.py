# from fastapi import APIRouter, WebSocket
# from starlette.status import WS_1008_POLICY_VIOLATION

# from src.app.controllers.llm_controller import LLMController
# import src.config.env as env

# # Router khusus untuk WebSocket tanpa dependencies global
# ws_router = APIRouter(prefix="/api/v1")


# @ws_router.websocket("/chat/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for streaming query responses"""
#     await websocket.accept()

#     # Custom authentication untuk WebSocket
#     headers = dict(websocket.headers)
#     api_key = headers.get("x-api-key")

#     # Validasi API key
#     if env.API_KEY and env.API_KEY != "" and api_key != env.API_KEY:
#         await websocket.close(code=WS_1008_POLICY_VIOLATION, reason="Invalid API Key")
#         return

#     # Lanjutkan dengan handling WebSocket setelah autentikasi berhasil
#     await LLMController.handle_websocket_connection(websocket)
