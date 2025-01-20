from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from product import Product
from pydantic import BaseModel
from bdd import engine, create_db

app = FastAPI()

# create_db()

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
