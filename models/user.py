from sqlmodel import SQLModel, Field
from pydantic import EmailStr, validator
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(SQLModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., unique=True)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str

    @classmethod
    def create(cls, user_create: UserCreate):
        return cls(
            username=user_create.username,
            email=user_create.email,
            hashed_password=pwd_context.hash(user_create.password)
        )

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password) 