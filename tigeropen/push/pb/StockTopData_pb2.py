# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tigeropen/push/pb/StockTopData.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$tigeropen/push/pb/StockTopData.proto\x12\x11tigeropen.push.pb\"\x8a\x02\n\x0cStockTopData\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12\x38\n\x07topData\x18\x03 \x03(\x0b\x32\'.tigeropen.push.pb.StockTopData.TopData\x1aV\n\x07TopData\x12\x12\n\ntargetName\x18\x01 \x01(\t\x12\x37\n\x04item\x18\x02 \x03(\x0b\x32).tigeropen.push.pb.StockTopData.StockItem\x1a\x45\n\tStockItem\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x13\n\x0blatestPrice\x18\x02 \x01(\x01\x12\x13\n\x0btargetValue\x18\x03 \x01(\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tigeropen.push.pb.StockTopData_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STOCKTOPDATA._serialized_start=60
  _STOCKTOPDATA._serialized_end=326
  _STOCKTOPDATA_TOPDATA._serialized_start=169
  _STOCKTOPDATA_TOPDATA._serialized_end=255
  _STOCKTOPDATA_STOCKITEM._serialized_start=257
  _STOCKTOPDATA_STOCKITEM._serialized_end=326
# @@protoc_insertion_point(module_scope)
