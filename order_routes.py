from fastapi import APIRouter, Depends, HTTPException, status

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@order_router.get("/")
def order():
    return {"message": "In Orders"}