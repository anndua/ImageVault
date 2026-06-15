from sqlmodel import SQLModel,Field


class User(SQLModel,table =True):
    id:int|None=Field(default=None,primary_key=True)
    username:str
    email:str
    
    hashed_password:str


class UserCreate(SQLModel):
    username: str
    email: str
    password: str



class UserLogin(SQLModel):
    email: str
    username:str
    password: str

class UserResponse(SQLModel):
    id: int
    username: str

class Image(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True
    )

    filename: str

    owner_id: int =Field(foreign_key="user.id")
    file_size: int|None =None

    


    

