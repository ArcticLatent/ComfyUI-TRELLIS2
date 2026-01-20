#!/usr/bin/env python3
"""
Installation script for ComfyUI-TRELLIS2 with ComfyUI venv.

This script installs all dependencies into ComfyUI's main venv.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path


# =============================================================================
# ComfyUI venv helpers
# =============================================================================

def _get_comfyui_venv_python(node_root):
    """Return ComfyUI venv python path if it exists, otherwise None."""
    comfyui_root = node_root.parent.parent
    python_path = comfyui_root / "venv" / "bin" / "python"
    return python_path if python_path.exists() else None


def ensure_venv_requirements(node_root):
    """Install requirements.txt into the ComfyUI venv."""
    req_path = node_root / "requirements.txt"
    if not req_path.exists():
        print(f"[TRELLIS2] requirements.txt not found at {req_path}")
        return False

    venv_python = _get_comfyui_venv_python(node_root)
    python_exec = str(venv_python) if venv_python else sys.executable
    if venv_python:
        print(f"[TRELLIS2] Using ComfyUI venv python: {venv_python}")
    else:
        print("[TRELLIS2] ComfyUI venv python not found; using current Python.")

    try:
        result = subprocess.run(
            [python_exec, "-m", "pip", "install", "-r", str(req_path)],
            check=False
        )
    except Exception as e:
        print(f"[TRELLIS2] Failed to run pip: {e}")
        return False

    if result.returncode != 0:
        print(f"[TRELLIS2] pip exited with code {result.returncode}")
        return False

    return True


def _split_env_list(value):
    if not value:
        return []
    parts = []
    for item in value.replace(";", ",").split(","):
        item = item.strip()
        if item:
            parts.append(item)
    return parts


def ensure_cuda_packages(node_root):
    """Install CUDA extension packages into the ComfyUI venv."""
    wheel_urls = [
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/cumesh-0.0.1-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/flex_gemm-1.0.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/nvdiffrast-0.4.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/nvdiffrec_render-0.0.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/o_voxel-0.0.1-cp312-cp312-linux_x86_64.whl",
    ]
    venv_python = _get_comfyui_venv_python(node_root)
    python_exec = str(venv_python) if venv_python else sys.executable
    if venv_python:
        print(f"[TRELLIS2] Using ComfyUI venv python: {venv_python}")
    else:
        print("[TRELLIS2] ComfyUI venv python not found; using current Python.")

    extra_index_urls = _split_env_list(os.environ.get("TRELLIS2_WHEEL_INDEX_URL"))
    find_links = _split_env_list(os.environ.get("TRELLIS2_WHEEL_FIND_LINKS"))

    cmd = [python_exec, "-m", "pip", "install", *wheel_urls]
    for url in extra_index_urls:
        cmd.extend(["--extra-index-url", url])
    for link in find_links:
        cmd.extend(["--find-links", link])

    if extra_index_urls or find_links:
        print("[TRELLIS2] Using custom wheel sources for CUDA packages.")
    else:
        print("[TRELLIS2] No custom wheel sources set for CUDA packages.")

    try:
        result = subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"[TRELLIS2] Failed to run pip: {e}")
        return False

    if result.returncode != 0:
        print(f"[TRELLIS2] pip exited with code {result.returncode}")
        print("[TRELLIS2] If these wheels are not on PyPI, set:")
        print("  TRELLIS2_WHEEL_INDEX_URL=https://... (comma-separated for multiple)")
        print("  TRELLIS2_WHEEL_FIND_LINKS=/path/to/wheels (comma-separated for multiple)")
        return False

    return True


# =============================================================================
# Main Installation
# =============================================================================

def main():
    """Main installation function."""
    print("\n" + "=" * 60)
    print("ComfyUI-TRELLIS2 Installation (ComfyUI venv)")
    print("=" * 60)

    node_root = Path(__file__).parent.absolute()

    print("[TRELLIS2] Installing requirements into ComfyUI venv.")
    if not ensure_venv_requirements(node_root):
        print("[TRELLIS2] ERROR: Failed to install requirements into venv.")
        return 1
    if not ensure_cuda_packages(node_root):
        print("[TRELLIS2] ERROR: Failed to install CUDA extension packages.")
        return 1
    return 0



if __name__ == "__main__":
    sys.exit(main())
