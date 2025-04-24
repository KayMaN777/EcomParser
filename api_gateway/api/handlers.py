from fastapi import APIRouter, Header, HTTPException
import grpc
from dotenv import load_dotenv
import os
import api.proto.wildberries_service_pb2_grpc as wildberries_service_pb2_grpc
import api.proto.wildberries_service_pb2 as wildberries_service_pb2
from models import (
    ListProductResponse,
    SearchRequest,
    CategoryRequest,
    SellerRequest
)

load_dotenv()

router = APIRouter()

def get_wildberries_stub():
    host = os.getenv("WILDBERRIES_PARSER_API_HOST")
    port = os.getenv("WILDBERRIES_PARSER_API_PORT")
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = wildberries_service_pb2_grpc.WildberriesServiceStub(channel)
    return stub 

def proto_to_json(response):
    products = []
    for product in response.data:
        products.append({
            'productId': product.product_id,
            'name': product.name,
            'brand': product.brand,
            'price': product.price,
            'discountPrice': product.discount_price,
            'rating': product.rating,
            'reviews': product.reviews
        })
    return ListProductResponse(filename=response.filename, data = products)

@router.post("/wildberries/search", response_model=ListProductResponse)
async def wildberries_search(request: SearchRequest):
    stub = get_wildberries_stub()
    search_req = wildberries_service_pb2.SearchRequest(
        text = request.text,
        num = request.num,
        order = request.order
    )
    try:
        response = stub.search(search_req)
        return proto_to_json(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Internal Error")

@router.post("/wildberries/category", response_model=ListProductResponse)
async def wildberries_category(request: CategoryRequest):
    stub = get_wildberries_stub()
    category_req = wildberries_service_pb2.CategoryRequest(
        link = request.link,
        num = request.num,
        order = request.order
    )
    try:
        response = stub.category(category_req)
        return proto_to_json(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Internal Error")

@router.post("/wildberries/seller", response_model=ListProductResponse)
async def wildberries_seller(request: SellerRequest):
    stub = get_wildberries_stub()
    seller_req = wildberries_service_pb2.SellerRequest(
        link = request.link,
        num = request.num,
        order = request.order
    )
    try:
        response = stub.seller(seller_req)
        return proto_to_json(response)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Internal Error")
