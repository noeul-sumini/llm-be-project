from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn 
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from main_router import api_router
app = FastAPI(
    title="llm-be-project",
    version="0.0.1"
)

@app.on_event("startup")
def startup():
    print("Start server")


@app.on_event("shutdown")
def shutdown():
    print("Shutdown server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(api_router)




if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8080, reload = True)