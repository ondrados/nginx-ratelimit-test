import random
import string
import time
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from typing import Annotated

app = FastAPI()

tokens = []


@app.get("/")
def read_root(access_token: Annotated[str | None, Header()] = None):
    if access_token not in tokens:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid token"},
        )
    time.sleep(0.1)
    return JSONResponse(
        status_code=200,
        content={"message": "Ok"},
    )


@app.post("/token")
def get_token():
    k = 10

    if len(tokens) < 9999:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
        tokens.append(token)
        return JSONResponse(
            status_code=200,
            content={"access_token": token, "expires_in": 300},
        )
    else:
        return JSONResponse(
            status_code=400,
            content={"message": "Maximum token count exceeded"},
        )

