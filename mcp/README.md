# Mini PNG Editor MCP Server 🛠️

This directory contains the MCP (Model Context Protocol) server for the Mini PNG Editor. It allows AI agents to query image metadata and perform image processing tasks (background removal, scaling, cropping) directly.
此目錄包含 Mini PNG Editor 的 MCP 伺服器實作，讓 AI Agent 可以直接查詢圖片元數據並執行圖片處理任務（去背、縮放、裁切）。

## 🚀 Getting Started / 快速入門

### 1. Prerequisites / 前置需求
Ensure you have the MCP Python SDK installed:
(請確保已安裝 MCP Python SDK：)
```bash
pip install mcp
```

### 2. Configuration / 設定範例
To let your **AI agent (like Antigravity)** use these tools, add the following to your MCP configuration:
(要讓您的 **AI agent (如 Antigravity)** 使用這些工具，請將以下內容加入您的 MCP 設定中：)

```json
{
  "mcpServers": {
    "mini-png-editor": {
      "command": "python",
      "args": [
        "D:/antigravity_workspace/mini_png_editor/mcp/mcp_server.py"
      ]
    }
  }
}
```
*Note: Tested and verified with **Antigravity**. (Compatible with all MCP-enabled clients).*
*(註：已在 **Antigravity** 上測試並驗證通過。同時也支援其他所有相容於 MCP 協定的工具。)*
*Note: Use absolute paths for the script to ensure it can be found by the client.*
*(註：建議使用絕對路徑以確保 Client 能正確讀取腳本。)*

- **If you move the script (若改變目錄結構)**: If you decide to move `mcp_server.py` to a different location, simply open the file and manually update the `EDITOR_SCRIPT` variable with the new absolute path to `mini_png_editor.py`.
- **(解決方案)**：若您搬移了 `mcp_server.py` 導致自動偵測失效，請直接編輯該檔案，將 `EDITOR_SCRIPT` 變數修改為 `mini_png_editor.py` 所在的新絕對路徑即可。

  **Example (範例):**
  ```python
  # In mcp_server.py:
  EDITOR_SCRIPT = r"C:\Path\To\Your\mini_png_editor.py"
  ```

## 🖥️ Headless Operation / 背景執行說明
The MCP server communicates via the **CLI mode** of the editor. This means:
- **No GUI will appear** during processing.
- Everything happens in the background for a seamless automated experience.

此 MCP 伺服器是透過主程式的 **CLI (命令行) 模式** 進行連動，這意味著：
- 執行過程中 **不會彈出圖形介面 (GUI)**。
- 所有處理都在背景完成，提供流暢的自動化體驗。

## 🛠️ Available Tools / 可用工具

### `get_image_info`
Queries an image's width, height, and mode. Returns a JSON string.
(查詢圖片的寬度、高度與格式。以 JSON 字串格式回傳。)
- `input_path`: Path to the image. (圖片路徑)

### `process_image`
Performs automated image processing.
(執行自動化圖片處理。)
- `input_path`: Source path. (來源路徑)
- `output_path`: Destination path. (輸出路徑)
- `rembg`: (bool) AI background removal. (是否啟用 AI 去背)
- `scale_w/h`: (int) Target dimensions. (縮放目標寬高)
- `crop_x/y/w/h`: (int) Crop parameters. (裁切座標與長寬)

**Processing Order / 執行順序說明:**
AI Removal (去背) -> Scaling (縮放) -> Cropping (裁切)
