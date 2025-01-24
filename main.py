from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from product import Product
from models.user import User, UserCreate
from bdd import engine
from auth import get_current_user, authenticate_user, create_access_token
from typing import List

app = FastAPI(
    title="API CRUD",
    description="API de gestion de produits avec authentification",
    version="1.0.0"
)

# Routes d'authentification
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Créer un nouvel utilisateur"""
    with Session(engine) as session:
        if session.exec(select(User).where(User.email == user.email)).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        db_user = User.create(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Obtenir un token JWT"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Routes protégées pour les produits
@app.get("/products", response_model=List[Product])
def get_products(current_user: User = Depends(get_current_user)):
    """Récupérer tous les produits"""
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, current_user: User = Depends(get_current_user)):
    """Récupérer un produit spécifique par ID"""
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        return product

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: Product, current_user: User = Depends(get_current_user)):
    """Créer un nouveau produit"""
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: Product,
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un produit existant"""
    with Session(engine) as session:
        existing_product = session.get(Product, product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        for key, value in product.dict(exclude_unset=True).items():
            setattr(existing_product, key, value)
        session.commit()
        session.refresh(existing_product)
        return existing_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, current_user: User = Depends(get_current_user)):
    """Supprimer un produit"""
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        session.delete(product)
        session.commit()
        return {"message": "Produit supprimé avec succès"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Récupérer les informations de l'utilisateur connecté"""
    return current_user
