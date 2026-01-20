"""Isolation helper that runs nodes directly in the ComfyUI venv."""


def _noop_isolated(*_args, **_kwargs):
    def decorator(obj):
        return obj
    return decorator


def isolated(*_args, **_kwargs):
    return _noop_isolated(*_args, **_kwargs)

__all__ = ["isolated"]
