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
# VC++ Redistributable Check (Windows only)
# =============================================================================

VCREDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"


def check_vcredist_installed():
    """Check if VC++ Redistributable DLLs are actually present on the system."""
    if platform.system() != "Windows":
        return True  # Not needed on non-Windows

    required_dlls = ['vcruntime140.dll', 'msvcp140.dll']

    # Search locations in order of preference
    search_paths = []

    # 1. System directory (most reliable)
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    search_paths.append(os.path.join(system_root, 'System32'))

    # 2. Python environment directories
    if hasattr(sys, 'base_prefix'):
        search_paths.append(os.path.join(sys.base_prefix, 'Library', 'bin'))
        search_paths.append(os.path.join(sys.base_prefix, 'DLLs'))
    if hasattr(sys, 'prefix') and sys.prefix != getattr(sys, 'base_prefix', sys.prefix):
        search_paths.append(os.path.join(sys.prefix, 'Library', 'bin'))
        search_paths.append(os.path.join(sys.prefix, 'DLLs'))

    # Check each required DLL
    for dll in required_dlls:
        found = False
        for search_path in search_paths:
            dll_path = os.path.join(search_path, dll)
            if os.path.exists(dll_path):
                found = True
                break
        if not found:
            return False

    return True


def install_vcredist():
    """Download and install VC++ Redistributable with UAC elevation."""
    import urllib.request
    import tempfile

    print("[TRELLIS2] Downloading VC++ Redistributable...")

    # Download to temp file
    temp_path = os.path.join(tempfile.gettempdir(), "vc_redist.x64.exe")
    try:
        urllib.request.urlretrieve(VCREDIST_URL, temp_path)
    except Exception as e:
        print(f"[TRELLIS2] Failed to download VC++ Redistributable: {e}")
        print(f"[TRELLIS2] Please download manually from: {VCREDIST_URL}")
        return False

    print("[TRELLIS2] Installing VC++ Redistributable (UAC prompt may appear)...")

    # Run with elevation - /passive shows progress, /quiet is fully silent
    try:
        result = subprocess.run(
            [temp_path, '/install', '/passive', '/norestart'],
            capture_output=True
        )
    except Exception as e:
        print(f"[TRELLIS2] Failed to run installer: {e}")
        print(f"[TRELLIS2] Please run manually: {temp_path}")
        return False

    # Clean up
    try:
        os.remove(temp_path)
    except:
        pass

    if result.returncode == 0:
        print("[TRELLIS2] VC++ Redistributable installer completed.")
    elif result.returncode == 1638:
        # 1638 = newer version already installed
        print("[TRELLIS2] VC++ Redistributable already installed (newer version)")
    else:
        print(f"[TRELLIS2] Installation returned code {result.returncode}")
        print(f"[TRELLIS2] Please install manually from: {VCREDIST_URL}")
        return False

    # Verify DLLs are actually present after installation
    if check_vcredist_installed():
        print("[TRELLIS2] VC++ Redistributable DLLs verified!")
        return True
    else:
        print("[TRELLIS2] Installation completed but DLLs not found in expected locations.")
        print("[TRELLIS2] You may need to restart your system or terminal.")
        return False


def ensure_vcredist():
    """Check and install VC++ Redistributable if needed (Windows only)."""
    if platform.system() != "Windows":
        return True

    if check_vcredist_installed():
        print("[TRELLIS2] VC++ Redistributable: OK (DLLs found)")
        return True

    print("[TRELLIS2] VC++ Redistributable DLLs not found - attempting automatic install...")

    if install_vcredist():
        return True

    # Fallback: provide clear manual instructions
    print("")
    print("=" * 70)
    print("[TRELLIS2] MANUAL INSTALLATION REQUIRED")
    print("=" * 70)
    print("")
    print("  The automatic installation of VC++ Redistributable failed.")
    print("  This is required for PyTorch CUDA and other native extensions.")
    print("")
    print("  Please download and install manually:")
    print(f"    {VCREDIST_URL}")
    print("")
    print("  After installation, restart your terminal and try again.")
    print("=" * 70)
    print("")
    return False


# =============================================================================
# ComfyUI venv helpers
# =============================================================================

def _get_comfyui_venv_python(node_root):
    """Return ComfyUI venv python path if it exists, otherwise None."""
    comfyui_root = node_root.parent.parent
    if platform.system() == "Windows":
        python_path = comfyui_root / "venv" / "Scripts" / "python.exe"
    else:
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

    # Check VC++ Redistributable first (required for PyTorch CUDA and native extensions)
    if not ensure_vcredist():
        print("[TRELLIS2] WARNING: VC++ Redistributable installation failed.")
        print("[TRELLIS2] Some features may not work. Continuing anyway...")

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
