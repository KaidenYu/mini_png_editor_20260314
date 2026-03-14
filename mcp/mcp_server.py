import os
import sys
import json
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("MiniPngEditor")

# --- Path Configuration / 路徑設定 ---
# We need to find the main 'mini_png_editor.py' relative to this MCP server script.
# 我們需要找到主程式的路徑，並確保不論從哪裡執行都能正確定位。

# 1. Get the directory where THIS script resides (the 'mcp' folder)
# 獲取本腳本所在的目錄（即 mcp 資料夾）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go one level up to find the project root directory
# 往上一層找到專案的根目錄
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# 3. Define the full absolute path to the main editor script
# 定義主程式的完整絕對路徑
EDITOR_SCRIPT = os.path.join(PROJECT_ROOT, "mini_png_editor.py")

@mcp.tool()
def get_image_info(input_path: str) -> str:
    """
    Get dimensions and metadata of an image.
    :param input_path: Absolute or relative path to the image.
    """
    try:
        cmd = [sys.executable, EDITOR_SCRIPT, "--input", input_path, "--info"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr or str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

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
    """
    Process an image: remove background, scale, and/or crop.
    :param input_path: Source image path.
    :param output_path: Destination image path.
    :param rembg: Set to True to remove background using AI.
    :param scale_w: Target width for scaling.
    :param scale_h: Target height for scaling.
    :param crop_x: X coordinate for cropping.
    :param crop_y: Y coordinate for cropping.
    :param crop_w: Width of the cropped area.
    :param crop_h: Height of the cropped area.
    """
    try:
        cmd = [sys.executable, EDITOR_SCRIPT, "--input", input_path, "--output", output_path]
        
        if rembg:
            cmd.append("--rembg")
        
        if scale_w is not None and scale_h is not None:
            cmd.extend(["--scale", str(scale_w), str(scale_h)])
            
        if all(v is not None for v in [crop_x, crop_y, crop_w, crop_h]):
            cmd.extend(["--crop", str(crop_x), str(crop_y), str(crop_w), str(crop_h)])
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr or str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
