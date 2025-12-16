from datetime import datetime

class Logger:
    """
    Custom logger to handle application output with timestamps and formatting.
    """

    @staticmethod
    def log(message: str, level: str = "INFO"):
        """
        Print a message with a timestamp and log level.

        :param message: The message to print.
        :param level: The severity level (INFO, WARNING, ERROR, SUCCESS).
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        icons = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "MINING": "⛏️",
            "NETWORK": "🌐"
        }

        icon = icons.get(level, "")
        formatted_msg = f"[{timestamp}] {icon} {message}"
        print(formatted_msg)

    @staticmethod
    def info(message: str):
        Logger.log(message, "INFO")

    @staticmethod
    def warning(message: str):
        Logger.log(message, "WARNING")

    @staticmethod
    def error(message: str):
        Logger.log(message, "ERROR")

    @staticmethod
    def success(message: str):
        Logger.log(message, "SUCCESS")

    @staticmethod
    def mining(message: str):
        Logger.log(message, "MINING")

    @staticmethod
    def network(message: str):
        Logger.log(message, "NETWORK")

