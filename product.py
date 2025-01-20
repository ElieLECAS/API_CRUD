from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    product_number: str
    standard_cost: float
    list_price: float
    weight: float
    product_category_id: int

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str

    @classmethod
    def get_by_id(cls, user_id: int):
        with Session(engine) as session:
            return session.query(cls).filter(cls.id == user_id).first()
