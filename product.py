from sqlmodel import SQLModel, Field
from pydantic import validator

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1, max_length=100)
    product_number: str = Field(..., min_length=1, max_length=50)
    standard_cost: float = Field(..., gt=0)
    list_price: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    product_category_id: int = Field(..., gt=0)

    @validator('list_price')
    def list_price_must_be_greater_than_standard_cost(cls, v, values):
        if 'standard_cost' in values and v <= values['standard_cost']:
            raise ValueError('list_price must be greater than standard_cost')
        return v
