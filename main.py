from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(auth_router, prefix="/api")
app.include_router(order_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    import environ

    # variables from environment
    env = environ.Env(DEBUG=(bool, False))

    # Read router.env file
    environ.Env.read_env(".env")
    HOST = env("HOST", default="0.0.0.0")
    PORT = env("PORT", default=8000)
    RELOAD = env("RELOAD", default=True)

    uvicorn.run("__main__:app", host=HOST, port=PORT, reload=RELOAD)