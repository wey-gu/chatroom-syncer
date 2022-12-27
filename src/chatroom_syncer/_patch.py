"""
A dirty HACK to fix the proto mismatching problem.
It should be removed immediately after wechaty has released the version
with new proto.
"""
from wechaty_grpc.wechaty.puppet import MessagePayloadResponse


def patch_all():
    def _get_from_id(self):
        return self.talker_id

    def _get_to_id(self):
        return self.listener_id

    MessagePayloadResponse.from_id = property(_get_from_id)
    MessagePayloadResponse.to_id = property(_get_to_id)
