# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tigeropen/push/pb/SocketCommon.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$tigeropen/push/pb/SocketCommon.proto\x12\x11tigeropen.push.pb\"\x9c\x03\n\x0cSocketCommon\"\x93\x01\n\x07\x43ommand\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07\x43ONNECT\x10\x01\x12\r\n\tCONNECTED\x10\x02\x12\x08\n\x04SEND\x10\x03\x12\r\n\tSUBSCRIBE\x10\x04\x12\x0f\n\x0bUNSUBSCRIBE\x10\x05\x12\x0e\n\nDISCONNECT\x10\x06\x12\x0b\n\x07MESSAGE\x10\x07\x12\r\n\tHEARTBEAT\x10\x08\x12\t\n\x05\x45RROR\x10\t\"\xc1\x01\n\x08\x44\x61taType\x12\x0b\n\x07Unknown\x10\x00\x12\t\n\x05Quote\x10\x01\x12\n\n\x06Option\x10\x02\x12\n\n\x06\x46uture\x10\x03\x12\x0e\n\nQuoteDepth\x10\x04\x12\r\n\tTradeTick\x10\x05\x12\t\n\x05\x41sset\x10\x06\x12\x0c\n\x08Position\x10\x07\x12\x0f\n\x0bOrderStatus\x10\x08\x12\x14\n\x10OrderTransaction\x10\t\x12\x0c\n\x08StockTop\x10\n\x12\r\n\tOptionTop\x10\x0b\x12\t\n\x05Kline\x10\x0c\"2\n\tQuoteType\x12\x08\n\x04None\x10\x00\x12\t\n\x05\x42\x41SIC\x10\x01\x12\x07\n\x03\x42\x42O\x10\x02\x12\x07\n\x03\x41LL\x10\x03\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tigeropen.push.pb.SocketCommon_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SOCKETCOMMON._serialized_start=60
  _SOCKETCOMMON._serialized_end=472
  _SOCKETCOMMON_COMMAND._serialized_start=77
  _SOCKETCOMMON_COMMAND._serialized_end=224
  _SOCKETCOMMON_DATATYPE._serialized_start=227
  _SOCKETCOMMON_DATATYPE._serialized_end=420
  _SOCKETCOMMON_QUOTETYPE._serialized_start=422
  _SOCKETCOMMON_QUOTETYPE._serialized_end=472
# @@protoc_insertion_point(module_scope)
