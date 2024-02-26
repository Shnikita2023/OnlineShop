from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from collections import deque

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Класс для блокировки частых запросов
    """

    REQUESTS_LIMIT: int = 100
    TIME_LIMIT: int = 60
    requests_dict: dict[str: [datetime]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        ip_address_user: str = request.client.host
        current_time: datetime = datetime.now()

        if ip_address_user not in self.requests_dict:
            self.requests_dict[ip_address_user] = deque()

        while (self.requests_dict[ip_address_user] and
               (current_time - self.requests_dict[ip_address_user][0]).total_seconds() > self.TIME_LIMIT):
            self.requests_dict[ip_address_user].popleft()

        if len(self.requests_dict[ip_address_user]) >= self.REQUESTS_LIMIT:
            return JSONResponse(status_code=429, content={"message": "Too many requests. Please try again later."})

        self.requests_dict[ip_address_user].append(current_time)

        response = await call_next(request)
        return response
