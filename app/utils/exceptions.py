class CustomException(Exception):
    """Base class for custom exceptions."""
    pass

class SpecificException(CustomException):
    """Exception raised for specific errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class APIException(Exception):
    """Exception for API errors."""
    def __init__(self, status_code: int = 400, detail: str = "API error"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class ValidationException(APIException):
    """Exception for validation errors."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=400, detail=detail)

class YouTubeException(APIException):
    """Exception for YouTube URL errors."""
    def __init__(self, detail: str = "YouTube error"):
        super().__init__(status_code=422, detail=detail)

class TranscriptException(APIException):
    """Exception for transcript errors."""
    def __init__(self, detail: str = "Transcript error"):
        super().__init__(status_code=503, detail=detail)