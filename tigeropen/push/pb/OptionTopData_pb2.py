# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tigeropen/push/pb/OptionTopData.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%tigeropen/push/pb/OptionTopData.proto\x12\x11tigeropen.push.pb\"\xf0\x04\n\rOptionTopData\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12\x39\n\x07topData\x18\x03 \x03(\x0b\x32(.tigeropen.push.pb.OptionTopData.TopData\x1a\x95\x01\n\x07TopData\x12\x12\n\ntargetName\x18\x01 \x01(\t\x12;\n\x08\x62igOrder\x18\x02 \x03(\x0b\x32).tigeropen.push.pb.OptionTopData.BigOrder\x12\x39\n\x04item\x18\x03 \x03(\x0b\x32+.tigeropen.push.pb.OptionTopData.OptionItem\x1a\x98\x01\n\x08\x42igOrder\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x0e\n\x06\x65xpiry\x18\x02 \x01(\t\x12\x0e\n\x06strike\x18\x03 \x01(\t\x12\r\n\x05right\x18\x04 \x01(\t\x12\x0b\n\x03\x64ir\x18\x05 \x01(\t\x12\x0e\n\x06volume\x18\x06 \x01(\x01\x12\r\n\x05price\x18\x07 \x01(\x01\x12\x0e\n\x06\x61mount\x18\x08 \x01(\x01\x12\x11\n\ttradeTime\x18\t \x01(\x03\x1a\xcd\x01\n\nOptionItem\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x0e\n\x06\x65xpiry\x18\x02 \x01(\t\x12\x0e\n\x06strike\x18\x03 \x01(\t\x12\r\n\x05right\x18\x04 \x01(\t\x12\x13\n\x0btotalAmount\x18\x05 \x01(\x01\x12\x13\n\x0btotalVolume\x18\x06 \x01(\x01\x12\x14\n\x0ctotalOpenInt\x18\x07 \x01(\x01\x12\x17\n\x0fvolumeToOpenInt\x18\x08 \x01(\x01\x12\x13\n\x0blatestPrice\x18\t \x01(\x01\x12\x12\n\nupdateTime\x18\n \x01(\x03\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tigeropen.push.pb.OptionTopData_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _OPTIONTOPDATA._serialized_start=61
  _OPTIONTOPDATA._serialized_end=685
  _OPTIONTOPDATA_TOPDATA._serialized_start=173
  _OPTIONTOPDATA_TOPDATA._serialized_end=322
  _OPTIONTOPDATA_BIGORDER._serialized_start=325
  _OPTIONTOPDATA_BIGORDER._serialized_end=477
  _OPTIONTOPDATA_OPTIONITEM._serialized_start=480
  _OPTIONTOPDATA_OPTIONITEM._serialized_end=685
# @@protoc_insertion_point(module_scope)