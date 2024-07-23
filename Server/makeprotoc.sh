I_PATH=../protos/.
GO_OUT_PATH=./protos

protoc -I=$I_PATH \
    --go_out=$GO_OUT_PATH \
    entity.proto
