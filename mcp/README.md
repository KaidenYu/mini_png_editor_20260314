# Mini PNG Editor MCP Server 🛠️

This directory contains the MCP (Model Context Protocol) server for the Mini PNG Editor. It is the bridge that allows AI agents to directly query image metadata and seamlessly perform complex image processing tasks (like AI background removal, intelligent scaling, and precise cropping) in the background.
(此目錄包含 Mini PNG Editor 的核心 MCP 伺服器實作，它是讓 AI Agent 可以直接查詢圖片元數據並無縫於背景執行複雜圖片處理任務（如 AI 去背、智慧縮放與精確裁切）的溝通橋樑。)

---

## 🚀 Key Architectural Optimizations / 核心架構優化

This MCP server has been specifically engineered to be **hyper-stable** for autonomous agents working in complex Windows environments.
(此 MCP 伺服器經過特別的工程設計，旨在讓自主代理人於複雜的 Windows 環境中達到**極致穩定**。)

- **Zero Deadlocks (零死鎖防護)**: By explicitly redirecting child process data streams (`stdin=subprocess.DEVNULL`) and hiding console windows (`CREATE_NO_WINDOW`), this server eliminates the infamous JSON-RPC pipe deadlock that causes connection timeouts (EOF errors) during heavy subprocess tasks.
  (透過強制將子進程資料流重定向以及隱藏控制台視窗，此伺服器徹底消除了在執行繁重子任務時，經常導致連線逾時或 EOF 錯誤的 JSON-RPC Pipe 死鎖問題。)
- **Nano-Second Startup (極速啟動)**: Integration with the main script features lazy-loading of heavy AI and GUI dependencies, ensuring that lightweight queries (like `--info`) execute in milliseconds without bogging down the server.
  (與主程式的整合採用了對重型 AI 與 GUI 套件的延遲載入技術，確保輕量級查詢（如 `--info`）能在毫秒內完成，絕不拖垮伺服器效能。)

---

## 🚀 Getting Started / 快速入門

### 1. Prerequisites / 前置需求
Ensure you have the MCP Python SDK installed:
(請確保您的 Python 環境已安裝 MCP 伺服器核心 SDK：)
```bash
pip install mcp
```

### 2. Configuration / 設定範例
To let your **AI agent (like Antigravity)** use these tools, register this server in your global MCP configuration file (e.g., `mcp_config.json`):
(要讓您的 **AI agent (如 Antigravity)** 使用這些神級工具，請將本伺服器註冊至您全域的 MCP 設定檔中：)

```json
{
  "mcpServers": {
    "mini-png-editor": {
      "command": "C:\\Path\\To\\Your\\Python\\Environment\\python.exe",
      "args": [
        "D:\\Absolute\\Path\\To\\mini_png_editor\\mcp\\mcp_server.py"
      ]
    }
  }
}
```
*💡 **Pro Tip / 專業建議**: It is highly recommended to use the absolute path to your specific `python.exe` instead of just `"python"` to prevent unexpected PATH environment mismatches.*
*(強烈建議：請填寫您 Python 環境體的「絕對路徑」而非單純使用 `"python"`，以預防非預期的 PATH 環境變數錯亂。)*

### 3. Absolute Pathing / 路徑綁定
- The `mcp_server.py` relies on an absolute path variable `EDITOR_SCRIPT` to locate the main logic script.
- **If you move the project directory (若您移動了專案資料夾)**: Please open `mcp_server.py` and manually update the `EDITOR_SCRIPT` variable to point to the new absolute path of `mini_png_editor.py`.
- **(解決方案)**：若您移動了整個專案資料夾導致伺服器找不到編輯器主程式，請直接編輯 `mcp_server.py`，將 `EDITOR_SCRIPT` 變數修改為 `mini_png_editor.py` 所在的新絕對路徑。

---

## 🛠️ Available Tools / 可用工具詳解

### `get_image_info`
Instantly queries an image's metadata without triggering heavy AI loads. Returns a JSON string.
(瞬間查詢圖片的元數據，不會觸發繁重的 AI 載入程序。以 JSON 字串格式回傳。)
- `input_path`: Absolute path to the source image. (原始圖片的絕對路徑)

### `process_image`
Performs automated, multi-step image processing natively.
(原生執行自動化、多步驟的圖片處理流程。)
- `input_path`: Source absolute path. (來源絕對路徑)
- `output_path`: Destination absolute path. (輸出絕對路徑)
- `rembg`: *(bool)* Enable AI background removal. (是否啟用 AI 自動去背)
- `scale_w/h`: *(int)* Target dimensions for scaling. (縮放目標寬高)
- `crop_x/y/w/h`: *(int)* Crop coordinates and dimensions. (裁切起始座標與長寬)

**⚙️ Processing Order / 執行順序說明:**
1. AI Background Removal (去背) 
2. Scaling (縮放) 
3. Cropping (裁切)
*Remember: Crop coordinates should be calculated based on the image size AFTER it has been scaled.*
*(請注意：裁切的座標必須基於圖片「縮放完成後」的尺寸來計算。)*
