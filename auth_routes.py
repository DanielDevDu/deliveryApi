from fastapi import APIRouter, Depends, HTTPException, status
from database import Session, engine
from schemas import SignUpModel, LoginModel, ShowUser
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

session = Session(bind=engine)


@auth_router.get("/all", status_code=status.HTTP_200_OK)
async def auth(Authorize:AuthJWT=Depends()):
    """
        ## Get all users
        ### Return a list of all users
        Only superuser can access this route
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        response = []
        all_users = session.query(User).all()

        for user in all_users:
            response.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_active": user.is_active
            })

        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Superuser", headers={"WWW-Authenticate": "Bearer"}) 


@auth_router.post(
    "/signup",
    # response_model=SignUpModel,
    status_code=status.HTTP_201_CREATED
)
async def signup(user: SignUpModel):
    """
        ## Create new user
        Any user can create new user with
        - username: str
        - email: str
        - password: str
        - is_staff: bool
        - is_active: bool
    """
    db_email = session.query(User).filter(User.email == user.email).first()

    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    db_username = session.query(User).filter(User.username == user.username).first()

    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_staff=user.is_staff,
        is_active=user.is_active
    )

    session.add(new_user)
    session.commit()
    
    return {"message": "User created successfully"}

# Login route
@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize:AuthJWT=Depends()):
    """
        ## Login user
        - username: str
        - password: str
    """
    db_user = session.query(User).filter(User.username == user.username).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not check_password_hash(db_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    try:
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return jsonable_encoder(response)

# Refresh token route
@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(Authorize:AuthJWT=Depends()):
    """
        ## Refresh token
        Return new access token
    """
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        # current_user = Authorize.get_jwt_identity()
        new_access_token = Authorize.create_access_token(subject=current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token")

    return jsonable_encoder({"access_token": new_access_token})