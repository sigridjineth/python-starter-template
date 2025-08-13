from typing import List

from fastapi import FastAPI
from fastapi import HTTPException
from my_core.models import User

app = FastAPI(title="My API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to My API"}


# in-memory store
users: List[User] = []


@app.post("/users/", response_model=User)
def create_user(user: User) -> User:
    users.append(user)
    return user


@app.get("/users/", response_model=List[User])
def list_users() -> List[User]:
    return users


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    for u in users:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")
