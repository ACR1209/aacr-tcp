from aacr.methods import get, post, delete, update
from aacr.listen import Server

@get("/")
def hello():
    return {"mesagge": "hello2"}

@get("/p", {"id": str})
def hello_with_params(id: str):
    return {"message": "hello " + id}

@post("/p", {"id": str})
def hello_with_params(id: str):
    return {"message": "hello " + id}


if __name__ == "__main__":
    Server().start()