import grpc
from concurrent import futures
from api.proto.wildberries_service_pb2_grpc import add_WildberriesServiceServicer_to_server
from api.server import WildberriesService
import api.proto.wildberries_service_pb2
from grpc_reflection.v1alpha import reflection
import os
from dotenv import load_dotenv
from models import WildberriesParser

load_dotenv()

def serve():
    parser = WildberriesParser()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_WildberriesServiceServicer_to_server(WildberriesService(parser), server)
    SERVICE_NAMES = (
        api.proto.wildberries_service_pb2.DESCRIPTOR.services_by_name['WildberriesService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    port = os.getenv("WILDBERRIES_PARSER_API_PORT")
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()