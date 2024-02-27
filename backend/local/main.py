from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.http.authentication.login import router as login_router
from app.api.http.authentication.auth_token import router as auth_token_router
from app.api.http.authentication.signup import router as signup_router

from app.api.http.swarm.create_swarm import router as create_swarm_router
from app.api.http.swarm.delete_swarm import router as delete_swarm_router
from app.api.http.swarm.set_current_swarm import router as set_current_swarm_router
from app.api.http.swarm.spawn_swarm import router as spawn_swarm_router
from app.api.http.swarm.update_swarm import router as update_swarm_router

from app.api.http.chat.set_current_chat import router as set_current_chat_router
from app.api.http.chat.handle_user_message import router as handle_user_message_router

from app.api.http.user.update_user import router as update_user_router

from app.api.websocket.websocket_manager import manager

from app.api.swarm_operation_queue import swarm_operation_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(swarm_operation_queue())
    yield
    # Flush the queue before the application stops

app = FastAPI(lifespan=lifespan)

    

app = FastAPI()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages if necessary
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(client_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login_router)
app.include_router(auth_token_router)
app.include_router(signup_router)
app.include_router(create_swarm_router)
app.include_router(delete_swarm_router)
app.include_router(set_current_swarm_router)
app.include_router(spawn_swarm_router)
app.include_router(update_swarm_router)
app.include_router(set_current_chat_router)
app.include_router(handle_user_message_router)
app.include_router(update_user_router)
