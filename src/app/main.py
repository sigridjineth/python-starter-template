from fastapi import FastAPI
from my_api.main import app as my_api_app

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from python-starter-template!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


# Mount the workspace API under /api
app.mount("/api", my_api_app)
