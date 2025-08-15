import os

# disable protobuf version check
os.environ.setdefault('TEMORARILY_DISABLE_PROTOBUF_VERSION_CHECK', 'true')

from google.protobuf import runtime_version
runtime_version._MAX_WARNING_COUNT = 0