from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from product import Product
from pydantic import BaseModel
from bdd import engine
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.user import User

app = FastAPI()

# Configuration
SECRET_KEY = "votre_clé_secrète_très_longue_et_complexe"  # À mettre dans .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Route pour récupérer tous les produits
@app.get("/products")
def get_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
    return products

# Route pour récupérer un produit spécifique par ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

# Route pour créer un produit
@app.post("/products")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
    return product

# Route pour mettre à jour un produit
@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    with Session(engine) as session:
        existing_product = session.get(Product, product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in product.dict(exclude_unset=True).items():
            setattr(existing_product, key, value)
        session.commit()
        session.refresh(existing_product)
    return existing_product

# Route pour supprimer un produit
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(product)
        session.commit()
    return {"message": "Product deleted successfully"}

# Route protégée pour récupérer l'utilisateur actuel
@app.get("/users/me")
def read_users_me(current_user: Product = Depends(get_current_user)):  # Remarque : il doit être 'User' et non 'Product'
    return current_user

# Classe Pydantic pour l'utilisateur (modèle pour la connexion)
class User(BaseModel):
    username: str
    password: str

# Endpoint pour obtenir un token JWT
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

def get_user(username: str) -> Optional[User]:
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user or not user.verify_password(password):
        return None
    return user

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user
