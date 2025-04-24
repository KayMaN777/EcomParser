from typing import List, Optional

from pydantic import BaseModel, Field

class ProductResponse(BaseModel):
    productId: int
    name: str
    brand: str
    price: int
    discountPrice: int
    rating: float
    reviews: int

class ListProductResponse(BaseModel):
    filename: str
    data: List[ProductResponse]

class SearchRequest(BaseModel):
    text: str
    num: int = Field(..., ge=0, le=1000, description="От 0 до 1000")
    order: str

class CategoryRequest(BaseModel):
    link: str
    num: int = Field(..., ge=0, le=1000, description="От 0 до 1000")
    order: str

class SellerRequest(BaseModel):
    link: str
    num: int = Field(..., ge=0, le=1000, description="От 0 до 1000")
    order: str