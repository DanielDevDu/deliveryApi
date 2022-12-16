from fastapi import APIRouter, Depends, HTTPException, status
from schemas import OrderModel, OrderStatusModel, UpdateOrderModel
from models import User, Order
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from database import Session, engine

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

session = Session(bind=engine)

@order_router.get("/all", status_code=status.HTTP_200_OK)
async def order(Authorize:AuthJWT=Depends()):
    """
        ## Get all orders
        Return a list of all orders
        Only superuser can access this route
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        all_orders = session.query(Order).all()
        response = []
        for order in all_orders:
            response.append({
                "order_id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.code,
                "pizza_size": order.pizza_size.code,
                "user_id": order.user_id
            })

        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Superuser")

# create orders
@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Create new order
        Any user can create new order with
        body:
            - quantity: int
            - pizza_size: str
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_status,
        pizza_size=order.pizza_size,
        user_id=db_user.id
    )
    new_order.users = db_user
    session.add(new_order)
    session.commit()

    response = {
        "order_id": new_order.id,
        "quantity": new_order.quantity,
        "order_status": new_order.order_status.code,
        "pizza_size": new_order.pizza_size.code,
        "user_id": new_order.user_id
    }


    return jsonable_encoder(response)

# Get One Order by ID
@order_router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_order(order_id: int, Authorize:AuthJWT=Depends()):
    """
        ## Get order by ID
        Return a single order
        - On Route:
            - order_id: int
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()
    db_order = session.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if db_user.is_staff or db_user.id == db_order.user_id:
        response = {
            "order_id": db_order.id,
            "quantity": db_order.quantity,
            "order_status": db_order.order_status.code,
            "pizza_size": db_order.pizza_size.code,
            "user_id": db_order.user_id
        }
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to access this order")

# Get all orders for the current user
@order_router.get("/user/orders", status_code=status.HTTP_200_OK)
async def get_my_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get all orders for the current user
        Return a list of all orders
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    response = []
    for order in user.orders:
        response.append({
            "order_id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.code,
            "pizza_size": order.pizza_size.code,
            "user_id": order.user_id
        })

    return jsonable_encoder(response)

# Get a single order for the current user
@order_router.get("/user/order/{order_id}", status_code=status.HTTP_200_OK)
async def get_my_order(order_id: int, Authorize:AuthJWT=Depends()):
    """
        ## Get a single order for the current user
        - On Route:
            - order_id: int
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    orders = user.orders
    
    for order in orders:
        if order.id == order_id:
            response = {
                "order_id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.code,
                "pizza_size": order.pizza_size.code,
                "user_id": order.user_id
            }
            return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not order found for this user")

# Update an order by id
@order_router.patch("/order/update/{order_id}", status_code=status.HTTP_202_ACCEPTED)
async def patch_order(update_order: UpdateOrderModel, order_id:int, Authorize:AuthJWT=Depends()):
    """
        ## Update an order by id
        You can only update the order if its status is pending
        - On route:
            - order_id: int
        - Body: UpdateOrderModel
            - quantity: int
            - pizza_size: str
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    order = session.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.user_id == user.id:
        # update order (Just Quantity and Pizza Size Only if the order is pending)
        if order.order_status == "PENDING":
            if update_order.quantity is not None:
                order.quantity = update_order.quantity
            if update_order.pizza_size is not None:
                order.pizza_size = update_order.pizza_size
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You can't update this order becouse is {}".format(order.order_status.code))

        session.commit()
    
        response = {
            "order_id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.code,
            "pizza_size": order.pizza_size.code,
            "user_id": order.user_id
        }
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to update this order")

# Update Order status by id
@order_router.put("/order/status/{order_id}", status_code=status.HTTP_200_OK)
async def put_order_status(update_order: OrderStatusModel, order_id:int, Authorize:AuthJWT=Depends()):
    """
        ## Update Order status by id
        Only staff can update order status
        - On route:
            - order_id: int
        - Body: OrderStatusModel
            - order_status: str
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if user.is_staff:
        order = session.query(Order).filter(Order.id == order_id).first()
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # update order status
        order.order_status = update_order.order_status
        session.commit()
    
        response = {
            "message": "Order status updated successfully",
        }
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to update status")

# Delete an order by id
@order_router.delete("/order/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id:int, Authorize:AuthJWT=Depends()):
    """
        ## Delete an order by id
        You can only delete the order if its status is pending
        - On route:
            - order_id: int
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.user_id == user.id:
        if order.order_status != "PENDING":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You can't delete this order becouse is {}".format(order.order_status.code))

        # delete order
        session.delete(order)
        session.commit()

        response = {
            "message": "Order deleted successfully",
        }

        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to delete this order")

