import logging


class MyLogger:

    def __init__(self, pathname: str = ''):
        self.pathname = pathname
        self.logger = logging.getLogger("app_logger")

    @property
    def init(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format=f"%(asctime)s :: %(levelname)s :: {self.pathname}:%(lineno)d - %(message)s",
            handlers=[
                logging.FileHandler(filename="app.log", mode="w", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return self.logger
