from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Dict, Optional


class CustomResponse(JSONResponse):
    def __init__(self, content: Any, status_code: int = 200, message: Optional[str] = None, **kwargs: Dict):
        data = {
            "status_code": status_code,
            "message": message,
            "data": content
        }
        super().__init__(content=jsonable_encoder(data), status_code=status_code, **kwargs)


class PostResponse(CustomResponse):
    def __init__(self, content: Any, status_code: int = 201, message: str = "Successfully created!", **kwargs: Dict):
        super().__init__(content=content, status_code=status_code, message=message, **kwargs)


class ListResponse(JSONResponse):
    def __init__(self, content: Any, status_code: int = 200, **kwargs: Dict):
        data = {
            "status_code": status_code,
            "data": content
        }
        super().__init__(content=jsonable_encoder(data), status_code=status_code, **kwargs)


class PutResponse(CustomResponse):
    def __init__(self, content: Any, status_code: int = 200, message: str = "Successfully updated!", **kwargs: Dict):
        super().__init__(content=content, status_code=status_code, message=message, **kwargs)


class DestroyResponse(CustomResponse):
    def __init__(self, content: Any, status_code: int = 204, message: str = "Successfully deleted!", **kwargs: Dict):
        super().__init__(content=content, status_code=status_code, message=message)
