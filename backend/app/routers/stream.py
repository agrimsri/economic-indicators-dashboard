
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.queries import get_user_by_id
from app.security import decode_access_token
from app.services.sse_broker import sse_broker

router = APIRouter(prefix="/api/v1", tags=["Stream"])
security_bearer = HTTPBearer(auto_error=False)


async def authenticate_stream_user(
    request: Request,
    token: str | None = Query(None),
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
):
    jwt_token = None
    if credentials and credentials.credentials:
        jwt_token = credentials.credentials
    elif token:
        jwt_token = token

    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Missing authentication token for event stream"}},
        )

    payload = decode_access_token(jwt_token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid token payload"}},
        )

    user = await get_user_by_id(int(user_id_str))
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "USER_INACTIVE", "message": "User inactive or deleted"}},
        )

    return user


@router.get("/stream")
async def stream_events(
    request: Request,
    current_user=Depends(authenticate_stream_user)
):
    queue = await sse_broker.subscribe()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream",
    }

    return StreamingResponse(
        sse_broker.sse_generator(queue),
        media_type="text/event-stream",
        headers=headers
    )
