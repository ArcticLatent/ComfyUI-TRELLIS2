"""Pre-startup script for ComfyUI-TRELLIS2.

This script runs before ComfyUI initializes. It copies example assets
and ensures required CUDA wheels are installed into the active venv.
"""
import os
import shutil
import subprocess
import sys
import importlib.util


def copy_assets_to_input():
    """Copy example assets to ComfyUI input directory."""
    script_dir = os.path.dirname(__file__)
    comfyui_root = os.path.dirname(os.path.dirname(script_dir))

    assets_src = os.path.join(script_dir, "assets")
    input_dst = os.path.join(comfyui_root, "input")

    if os.path.exists(assets_src):
        os.makedirs(input_dst, exist_ok=True)
        for asset in os.listdir(assets_src):
            src = os.path.join(assets_src, asset)
            dst = os.path.join(input_dst, asset)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f"[TRELLIS2] Copied asset: {asset}")


def _ensure_cuda_wheels():
    wheel_urls = [
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/cumesh-0.0.1-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/flex_gemm-1.0.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/nvdiffrast-0.4.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/nvdiffrec_render-0.0.0-cp312-cp312-linux_x86_64.whl",
        "https://huggingface.co/datasets/arcticlatent/trellis2/resolve/main/o_voxel-0.0.1-cp312-cp312-linux_x86_64.whl",
    ]
    modules = ["cumesh", "flex_gemm", "nvdiffrast", "nvdiffrec_render", "o_voxel"]
    missing = [name for name in modules if importlib.util.find_spec(name) is None]

    if not missing:
        return

    print(f"[TRELLIS2] Installing CUDA wheels into venv (missing: {', '.join(missing)})...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", *wheel_urls], check=False)
    except Exception as e:
        print(f"[TRELLIS2] Failed to install CUDA wheels: {e}")
        return

    if result.returncode != 0:
        print(f"[TRELLIS2] CUDA wheel install failed with code {result.returncode}")


copy_assets_to_input()
_ensure_cuda_wheels()
