from datetime import datetime

from fastapi import HTTPException

from app.logging_config import MyLogger

loger = MyLogger().logger


class HttpAPIException(Exception):

    def __init__(self, exception: str = ""):
        self.exception = exception

    @property
    def http_error_500(self):
        loger.error(self.exception + " Status 500")
        return HTTPException(status_code=500, detail={
            "status": "error",
            "data": f"{datetime.now()}",
            "details": f"Что-то пошло не так, попробуйте позже"
        })

    @property
    def http_error_400(self):
        loger.info(self.exception + " Status 400")
        return HTTPException(status_code=400, detail={
            "status": "error",
            "data": f"{datetime.now()}",
            "details": self.exception
        })

    @property
    def http_error_401(self):
        loger.info(self.exception + " Status 401")
        return HTTPException(status_code=401, detail={
            "status": "error",
            "data": f"{datetime.now()}",
            "details": self.exception
        })

    @property
    def http_error_403(self):
        loger.info(self.exception + " Status 403")
        return HTTPException(status_code=403, detail={
            "status": "error",
            "data": f"{datetime.now()}",
            "details": self.exception
        })
