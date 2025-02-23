from unittest import TestCase
from unittest.mock import patch, Mock, mock_open
import json
from fluxion_ai.utils.loggers import FluxionLogger
from datetime import datetime


class TestFluxionLogger(TestCase):

    def setUp(self):
        self.logger = FluxionLogger(logger_name="TestLogger", log_level="DEBUG")
    
    @patch("fluxion_ai.utils.loggers.print")
    @patch("fluxion_ai.utils.loggers.datetime")
    def test_log_message(self, mock_datetime, mock_print):
        message = "This is a test message"
        
        mock_datetime.now.return_value = Mock(strftime = lambda date: "2021-01-01 00:00:00")
        self.logger.debug(message)
        expected_message = f"DEBUG: 2021-01-01 00:00:00 - [TestLogger] - {message}"
        mock_print.assert_called_once_with(expected_message)

    @patch("fluxion_ai.utils.loggers.print")
    @patch("fluxion_ai.utils.loggers.datetime")
    def test_log_message_json(self, mock_datetime, mock_print):
        message = "This is a test message"
        self.logger.is_json = True
        
        mock_datetime.now.return_value = Mock(strftime = lambda date: "2021-01-01 00:00:00")
        self.logger.debug(message)
        expected_message = json.dumps({
            "timestamp": "2021-01-01 00:00:00",
            "logger": "TestLogger",
            "message": message,
            "level": "DEBUG"
        })
        mock_print.assert_called_once_with(expected_message)


    @patch("fluxion_ai.utils.loggers.datetime")
    def test_log_to_file(self, mock_datetime):
        message = "This is a test message"
        self.logger.file_path = "test.log"
        
        mock_datetime.now.return_value = Mock(strftime = lambda date: "2021-01-01 00:00:00")
        with patch("builtins.open", mock_open()) as mock_file:
            self.logger.debug(message)
            expected_message = f"DEBUG: 2021-01-01 00:00:00 - [TestLogger] - {message}"
            mock_file().write.assert_called_once_with(expected_message + "\n")

    @patch("fluxion_ai.utils.loggers.datetime")
    def test_log_higher_level(self, mock_datetime):
        message = "This is a test message"
        self.logger.log_level = "INFO"
    
        mock_datetime.now.return_value = Mock(strftime = lambda date: "2021-01-01 00:00:00")
        with patch("builtins.print") as mock_print:
            self.logger.debug(message)
            mock_print.assert_not_called()

        self.logger.log_level = "DEBUG"

        with patch("builtins.print") as mock_print:
            self.logger.debug(message)
            expected_message = f"DEBUG: 2021-01-01 00:00:00 - [TestLogger] - {message}"
            mock_print.assert_called_once_with(expected_message)

    
    