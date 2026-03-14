import os
import sys
import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MiniPngEditor")

# Use a pre-defined absolute path for the main script
EDITOR_SCRIPT = r"d:\antigravity_workspace\mini_png_editor\mini_png_editor.py"

@mcp.tool()
def get_image_info(input_path: str) -> str:
    """Get dimensions and metadata of an image."""
    try:
        PYTHON_EXE = sys.executable
        
        # CRITICAL: Pass stdin=subprocess.DEVNULL to prevent child process from 
        # grabbing the parent's stdio descriptors (protects JSON-RPC flow)
        result = subprocess.run(
            [PYTHON_EXE, EDITOR_SCRIPT, "--input", input_path, "--info"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15, 
            cwd=os.path.dirname(EDITOR_SCRIPT),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
            
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Image information query timed out. The system might be busy."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def process_image(
    input_path: str, 
    output_path: str, 
    rembg: bool = False, 
    scale_w: int = None, 
    scale_h: int = None,
    crop_x: int = None,
    crop_y: int = None,
    crop_w: int = None,
    crop_h: int = None
) -> str:
    """Process an image (rembg, scale, crop)."""
    try:
        PYTHON_EXE = sys.executable
        cmd = [PYTHON_EXE, EDITOR_SCRIPT, "--input", input_path, "--output", output_path]
        if rembg: cmd.append("--rembg")
        if scale_w and scale_h: cmd.extend(["--scale", str(scale_w), str(scale_h)])
        if all(v is not None for v in [crop_x, crop_y, crop_w, crop_h]):
            cmd.extend(["--crop", str(crop_x), str(crop_y), str(crop_w), str(crop_h)])
            
        result = subprocess.run(
            cmd, 
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, 
            timeout=60,
            cwd=os.path.dirname(EDITOR_SCRIPT),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout.strip() or result.stderr.strip() or "Processing completed successfully."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
