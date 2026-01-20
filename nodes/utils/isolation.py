"""Isolation helper for running nodes with or without comfy-env."""

import os


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _noop_isolated(*_args, **_kwargs):
    def decorator(obj):
        return obj
    return decorator


def _get_isolated():
    # Default to running inside the ComfyUI venv without comfy-env.
    if _is_truthy(os.environ.get("TRELLIS2_ENABLE_COMFY_ENV")):
        try:
            from comfy_env import isolated as comfy_isolated
            return comfy_isolated
        except Exception as e:
            print(f"[TRELLIS2] comfy_env requested but unavailable ({e}); running without isolation.")
            return _noop_isolated

    print("[TRELLIS2] Using ComfyUI venv (comfy-env disabled).")
    return _noop_isolated


isolated = _get_isolated()

__all__ = ["isolated"]
