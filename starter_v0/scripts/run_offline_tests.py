"""Run all tests without credentials or external connections, including Windows UI tests."""
from pathlib import Path
import os
import socket
import sys
import threading
import uuid


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0, str(root))
    for key in list(os.environ):
        if key.endswith("_KEY") or "TOKEN" in key or key == "DAY03_ENV_FILE":
            os.environ.pop(key, None)
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    class NetworkBlocked(BaseException):
        pass

    def deny(*args, **kwargs):
        raise NetworkBlocked("External connections are forbidden in offline tests")

    # On Windows asyncio's internal socketpair uses a loopback connection.
    # Permit only that synchronous socketpair implementation on its own thread;
    # ordinary loopback connections, provider/tool requests, and DNS stay blocked.
    original_connect = socket.socket.connect
    original_socketpair = socket.socketpair
    state = threading.local()

    def guarded_connect(self, address):
        if (getattr(state, "creating_pair", False)
                and isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}):
            return original_connect(self, address)
        return deny()

    def internal_socketpair(*args, **kwargs):
        state.creating_pair = True
        try:
            return original_socketpair(*args, **kwargs)
        finally:
            state.creating_pair = False

    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = deny
    socket.socketpair = internal_socketpair
    socket.create_connection = deny
    socket.getaddrinfo = deny
    # A new absolute path avoids pytest removing a reused or unrelated directory.
    base = root / ".pytest-offline" / uuid.uuid4().hex
    assert base.resolve().is_relative_to(root.resolve())
    base.parent.mkdir(exist_ok=True)
    import pytest
    return pytest.main(["-q", "-ra", "--tb=short", "-p", "no:cacheprovider",
                        "--basetemp", str(base), "tests"])


if __name__ == "__main__":
    raise SystemExit(main())
