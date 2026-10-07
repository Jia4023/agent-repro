# opencode.ai 中转站要求每个会话携带 x-opencode-session 头（稳定的会话 ID）。
# 此文件随 .venv 自动加载，为发往 opencode.ai 的 requests 请求注入该头。
import os
import uuid

import requests

_SESSION_ID = os.environ.get("OPENCODE_SESSION_ID") or str(uuid.uuid4())

_orig_request = requests.Session.request


def _patched_request(self, method, url, **kwargs):
    if "opencode.ai" in str(url):
        headers = kwargs.get("headers") or {}
        if "x-opencode-session" not in {k.lower() for k in headers}:
            headers = {**headers, "x-opencode-session": _SESSION_ID}
            kwargs["headers"] = headers
    return _orig_request(self, method, url, **kwargs)


requests.Session.request = _patched_request
