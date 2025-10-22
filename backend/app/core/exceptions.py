from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found"""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{resource_id}' not found",
        )


class ElasticsearchException(HTTPException):
    """Raised when Elasticsearch operations fail"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Elasticsearch error: {detail}",
        )


class StorageException(HTTPException):
    """Raised when storage operations fail"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage error: {detail}",
        )


class ValidationException(HTTPException):
    """Raised when validation fails"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
