from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from product import Product
from bdd import engine, create_db
from auth import get_current_user

app = FastAPI()

create_db()

@app.get("/products")
def get_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

@app.post("/products")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
    return product

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

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(product)
        session.commit()
    return {"message": "Product deleted successfully"}

@app.get("/users/me")
def read_users_me(current_user: Product = Depends(get_current_user)):
    return current_user
