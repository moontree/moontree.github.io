```
pip install grpcio
pip install grpcio-tools
```
将proto编译为python\python grpc库：
`
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. dynamic_masker.proto
`