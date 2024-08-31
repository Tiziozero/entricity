I_PATH=../protos/.
PY_OUT_PATH=./src


# protoc -I=$I_PATH \
#     --python_out=$PY_OUT_PATH \
#     entity.proto
python3 -m grpc_tools.protoc -I=$I_PATH --python_out=$PY_OUT_PATH entity.proto

