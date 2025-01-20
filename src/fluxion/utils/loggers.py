from enum import Enum
import json
from typing import Optional
from datetime import datetime




class FluxionLogger:
    """ Logger class for logging output """

    def __init__(self, logger_name: str, file_path:  Optional[str] = None, log_level: str = "INFO", is_json: bool = False):
        """
        Initialize the logger.

        Args:
            logger_name (str): The name of the logger.
            file_path (str, optional): The file path to write the log output. Defaults to None.
            log_level (str, optional): The log level to use. Defaults to "INFO".
            is_json (bool, optional): Whether to log in JSON format. Defaults to False.
        """
        self.file_path = file_path
        self.logger_name = logger_name
        self.log_level = log_level
        self.is_json = is_json


    def log(self, message: str, level: str = "INFO"):
        """
        Log a message.

        Args:
            message (str): The message to log.
        """
        if self.log_level == "INFO" and level == "INFO":
            self.__log_message(message, level)
        elif self.log_level == "DEBUG" and (level == "DEBUG" or level == "INFO"):
            self.__log_message(message, level)
        elif self.log_level == "ERROR" and (level == "ERROR" or level == "DEBUG" or level == "INFO"):
            self.__log_message(message, level)
        elif self.log_level == "WARNING" and (level == "WARNING" or level == "ERROR" or level == "DEBUG" or level == "INFO"):
            self.__log_message(message, level)
        
    

    def __log_message(self, message: str, log_level: str):
        """
        Log a message.

        Args:
            message (str): The message to log.
        """
        formatted_message = self.construct_message(message, log_level)
        if self.file_path is not None:
            with open(self.file_path, mode="a") as output_file:
                output_file.write(formatted_message + "\n")
        else:
            print(formatted_message)

    def info(self, message: str):
        """
        Log an info message.

        Args:
            message (str): The message to log.
        """
        self.log(message, "INFO")
    
    def debug(self, message: str):
        """
        Log a debug message.

        Args:
            message (str): The message to log.
        """
        self.log(message, "DEBUG")

    def error(self, message: str):
        """
        Log an error message.

        Args:
            message (str): The message to log.
        """
        self.log(message, "ERROR")

    def warning(self, message: str):
        """
        Log a warning message.

        Args:
            message (str): The message to log.
        """
        self.log(message, "WARNING")        

    def construct_message(self, message: str, log_level: str) -> str:
        """
        Construct a message with additional key-value pairs.

        Args:
            message (str): The message template.
            log_level (str): The log level.

        Returns:
            str: The formatted message.
        """
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.is_json:
            return json.dumps({
                "timestamp": date_time,
                "logger": self.logger_name,
                "message": message,
                "level": log_level
            })
        return f"{log_level}: {date_time} - [{self.logger_name}] - {message}"
    

