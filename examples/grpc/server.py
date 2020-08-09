# --*-- coding: utf-8 --*--
"""
=========================
project -> file: moontree.github.io -> server.py
author: zhangchao
datetime: 2020/7/30 11:20 AM
=========================
"""
import grpc
import logging
import time
from concurrent import futures


from rpc_package.service_pb2_grpc import add_StarSeaServiceServicer_to_server, StarSeaServiceServicer
from rpc_package.service_pb2 import HelloRequest, HelloResponse, AddRequest, AddResponse


class AService(StarSeaServiceServicer):

    def SayHello(self, request, context):
        print(request, context)
        return HelloResponse(message="Hello, %s!" % request.name)

    def Add(self, request, context):
        res = 0
        return AddResponse(sum_val=sum(request.vals))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    add_StarSeaServiceServicer_to_server(AService(), server)

    server.add_insecure_port('localhost:50000')
    server.start()
    print("server: start")
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logging.basicConfig()
    serve()
