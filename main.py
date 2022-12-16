from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
import inspect, re
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi

# app = FastAPI()
app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})
app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title = "Delivery API",
        version = "1.0",
        description = "An API for a Delivery Service",
        routes = app.routes,
    )

    openapi_schema["info"] = {
        "title" : "Amazing Delivery API",
        "Content-Type": "application/json",
        "version" : "1.0",
        "description" : "Use this API to manage your delivery service",
        "contact": {
           "name": "API Support",
           "url": "https://portafolio.riodu.tech/",
           "email": "danieldevdu@gmail.com"
       },
    }

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "http",
            "scheme": "bearer",
            "Content-Type": "application/json",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]



        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

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