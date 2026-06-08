from db import DATABASE_URL, engine,create_tables
from model import UserCreate,User,UserLogin,UserResponse,Image
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File
from sqlmodel import Session,select
from db import get_session
from security import hash_password,verify_password,get_current_user,create_access_token,create_refresh_token,exchange_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
import os
from fastapi.responses import FileResponse
import time 
from fastapi import Request
from fastapi.responses import JSONResponse
from exception import global_exception_handler
from jose import jwt,JWTError

app=FastAPI()
app.add_exception_handler(
    Exception,
    global_exception_handler
)
@app.on_event("startup")
def startup():
    create_tables()


@app.middleware("http")
async def logger(request:Request,call_next):

    
  
    start=time.time()
    response =await call_next(request)
    end =time.time()
    
    
    print(
        f"{request.method}{request.url.path}\n"
        f"took:{end-start}\n"
    )
    return response
request_log={}
@app.middleware("http")
async def rate_limiter(
    request: Request,call_next):


    


    client=request.client
    ip=client.host if client else "unknown"
    if ip not in request_log:
        request_log[ip] =[]
    now=time.time()
    request_log[ip].append(now)
    request_log[ip]=[t 
              for t in request_log[ip]
                         if now-t<60           ]
    if len(request_log[ip])>=100:
        return JSONResponse(
    status_code=429,
    content={
        "detail": "Too many requests"
    })
    response=await call_next(request)
    return response        

        
        



@app.get("/")
def home():
    return {
        "message": "Welcome to ImageVault"
    }


@app.post("/register",response_model=User)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(
            User.username == user_data.username
        )
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
    ,
    session: Session = Depends(get_session)
):
    username = form_data.username
    statement = select(User).where(
        User.username == username
    )
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    access_token = create_access_token(
        {"sub": str(user.id)}
    )
    refresh_token=create_refresh_token({"sub":str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token":refresh_token,
        "token_type": "bearer"
    }



@app.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user

    
@app.post("/upload")
async def upload_image(file: UploadFile = File(...),
                       current_user: User = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    filename = file.filename
    allowed_extensions = [
        ".png",
        ".jpg",
        ".jpeg"
    ]
    if filename is None:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    name, ext = os.path.splitext(filename)  # split filename to name and extension
    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
    existing_file = session.exec(
        select(Image).where(Image.filename == filename)
    ).first()
    if existing_file:
        filename = f'{name}({existing_file.id}){ext}'

    contents = await file.read()  # ->actual image byte

    with open(
        f"uploads/{filename}",  # ->tell to open folder uploads filename and wb means in binary mode as f
        "wb"
    ) as f:
        f.write(contents)
        image = Image(
            filename=filename,
            owner_id=current_user.id or 0
        )

        session.add(image)
        session.commit()
        session.refresh(image)

        return {"message": "file uploaded"}

# Create/Open file called filename
#           ↓
# Take uploaded image bytes
#           ↓
# Write them into that file



@app.get("/my-images")
def get_my_images(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Image).where(Image.owner_id == current_user.id)
    images = session.exec(statement).all()

    return  [
        {
            "id": image.id,
            "filename": image.filename,
            "url": f"/images/{image.filename}"
        }
        for image in images
    ]


@app.get("/images/{image_id}")
def get_image(image_id:int,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    image=session.get(Image,image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )
    if image.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    



    return FileResponse(
        path=f"uploads/{image.filename}"
    )



@app.delete("/images/{image_id}")
def delete_image(image_id:int,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    image=session.get(Image,image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail="image doesnt exist"
        )
    if image.owner_id!=current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    filename=image.filename
    session.delete(image)
    session.commit()
    os.remove(
        f"uploads/{filename}"

    )
    return{"message":f"{filename} succesfully deleted"}
    


@app.post("/refresh")
def refresh_token(refresh_token:str):
    return  exchange_refresh_token(refresh_token)
   
   
