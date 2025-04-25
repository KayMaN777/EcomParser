import grpc
from concurrent import futures
from api.proto.ozon_service_pb2_grpc import add_OzonServiceServicer_to_server
from api.server import OzonService
import api.proto.ozon_service_pb2
from grpc_reflection.v1alpha import reflection
import os
from dotenv import load_dotenv
from models import OzonParser

load_dotenv()

def serve():
    parser = OzonParser()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_OzonServiceServicer_to_server(OzonService(parser), server)
    SERVICE_NAMES = (
        api.proto.ozon_service_pb2.DESCRIPTOR.services_by_name['OzonService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    port = os.getenv("OZON_PARSER_API_PORT")
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()