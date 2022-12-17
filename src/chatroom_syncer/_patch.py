"""
A dirty HACK to fix the proto mismatching problem.
It should be removed immediately after wechaty has released the version
with new proto.
"""
import importlib.util

MODULES_TO_PATCH = [
    "wechaty_puppet_service.puppet",
    "wechaty_grpc",
    "wechaty_grpc.wechaty.puppet",
]


def _patch_one(module_name: str) -> None:
    # Find the file path of the given module
    spec = importlib.util.find_spec(module_name)
    file_path = spec.origin
    if not file_path:
        return
    with open(file_path, "rb") as f:
        content = f.read()

    with open(file_path, "wb") as f:
        f.write(content.replace(b"filebox", b"file_box"))


def patch_all():
    for module in MODULES_TO_PATCH:
        _patch_one(module)
