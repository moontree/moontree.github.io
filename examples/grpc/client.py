# --*-- coding: utf-8 --*--
"""
=========================
project -> file: moontree.github.io -> client.py
author: zhangchao
datetime: 2020/7/30 11:32 AM
=========================
"""

import grpc
from rpc_package.service_pb2 import HelloRequest, HelloResponse, AddRequest, AddResponse
from rpc_package.service_pb2_grpc import StarSeaServiceStub


def run():
    channel = grpc.insecure_channel("127.0.0.1:50000")
    print(channel)
    stub = StarSeaServiceStub(channel)
    print(stub)
    response = stub.SayHello(HelloRequest(name="starsea"))
    print(response)
    req = AddRequest()
    req.vals.extend([1, 2, 3, 4])
    print(req)
    response = stub.Add(req)

    print(response)

run()