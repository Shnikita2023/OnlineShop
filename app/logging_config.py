import logging


class MyLogger:

    def __init__(self,
                 pathname: str = '',
                 name_logger: str = "app_logger",
                 filename: str = "app.log"):
        self.pathname = pathname
        self.logger = logging.getLogger(name_logger)
        self.filename = filename

    @property
    def init_logger(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format=f"%(asctime)s :: %(levelname)s :: {self.pathname}:%(lineno)d - %(message)s",
            handlers=[
                logging.FileHandler(filename=self.filename, mode="w", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return self.logger
