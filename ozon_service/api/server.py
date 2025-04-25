import grpc
from concurrent import futures
from api.proto.ozon_service_pb2_grpc import OzonServiceServicer
from api.proto.ozon_service_pb2 import (
    ListProductResponse
)

class OzonService(OzonServiceServicer):
    def __init__(self, parser):
        self.parser = parser

    def search(self, request, context):
        response = self.parser.search(request.text, request.num, request.order)
        if response is None:
            context.set_details('Internal Error')
            context.set_code(grpc.StatusCode.INTERNAL)
            return ListProductResponse()

        return ListProductResponse(
            filename = response['filename'], 
            data = response['data']    
        )

    def category(self, request, context):
        response = self.parser.category(request.link, request.num, request.order)
        if response is None:
            context.set_details('Internal Error')
            context.set_code(grpc.StatusCode.INTERNAL)
            return ListProductResponse()

        return ListProductResponse(
            filename = response['filename'], 
            data = response['data']    
        )
    
    def seller(self, request, context):
        response = self.parser.seller(request.link, request.num, request.order)
        if response is None:
            context.set_details('Internal Error')
            context.set_code(grpc.StatusCode.INTERNAL)
            return ListProductResponse()

        return ListProductResponse(
            filename = response['filename'], 
            data = response['data']    
        )