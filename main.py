from fastapi import (
    FastAPI, HTTPException, BackgroundTasks,
    File, UploadFile, Form, Depends, Response, Request
)
import uvicorn

app = FastAPI()


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
