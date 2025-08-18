import sys
import traceback
from logger.custom_logger import CustomLogger
logger = CustomLogger().get_logger(__file__)
from typing import Optional, cast


class AssistIQAppException(Exception):
    """Base class for all exceptions in the application.

    Args:
        Exception (_type_): _description_
    """

    def __init__(self, error_message, error_details: Optional[object] = None):
        
        # Normalize message
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Resolve exc_info (supports: sys module, Exception object, or current context)
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys
                #exc_type, exc_value, exc_tb = error_details.exc_info()
                exc_info_obj = cast(sys, error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to the last frame to report the most relevant location
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.line_number = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Full pretty traceback (if available)
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

        

    def __str__(self) -> str:
        """Set Compact, logger-friendly message

        Returns:
            str: Error message
        """
        base = f"Error in [{self.file_name}] at line [{self.line_number}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self) -> str:
        """_summary_

        Returns:
            str: User friendly exception message
        """
        return f"AssistIQAppException(file={self.file_name!r}, line={self.line_number}, message={self.error_message!r})"


if __name__ == "__main__":
    try:
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc = AssistIQAppException(e,sys)
        logger = CustomLogger().get_logger(__file__)
        logger.error(app_exc)
        raise app_exc from e