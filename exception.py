from fastapi import Request
from fastapi.responses import JSONResponse


async def global_exception_handler(
        request:Request,
        exec:Exception
):
    print(f"ERROR:{exec}")
    return JSONResponse(
        status_code=500,
        content={
            "detail":"internal server error"
        }
    )
    
