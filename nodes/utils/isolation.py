"""Isolation helper that runs nodes directly in the ComfyUI venv."""


def _noop_isolated(*_args, **_kwargs):
    def decorator(obj):
        return obj
    return decorator


isolated = _noop_isolated()

__all__ = ["isolated"]
