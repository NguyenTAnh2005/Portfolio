from app.core.exception import AppException
from fastapi import status
from typing import Optional

def to_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        raise AppException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="NOT_INVALID_VALUE",
            message=f"'{value}' không phải số nguyên hợp lệ"
        )
        # raise HTTPException(status_code=422, detail=f"'{value}' không phải số nguyên hợp lệ")