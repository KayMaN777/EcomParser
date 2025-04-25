import grpc
from concurrent import futures
from api.proto.yamarket_service_pb2_grpc import add_YamarketServiceServicer_to_server
from api.server import YamarketService
import api.proto.yamarket_service_pb2
from grpc_reflection.v1alpha import reflection
import os
from dotenv import load_dotenv
from models import YamarketParser

load_dotenv()

def serve():
    parser = YamarketParser()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_YamarketServiceServicer_to_server(YamarketService(parser), server)
    SERVICE_NAMES = (
        api.proto.yamarket_service_pb2.DESCRIPTOR.services_by_name['YamarketService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    port = os.getenv("YAMARKET_PARSER_API_PORT")
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()