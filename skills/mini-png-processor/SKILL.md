---
name: Mini PNG Processor
description: 精確的 PNG 圖片處理技能，支援 AI 去背、縮放與裁切。(A precise PNG processing skill supporting AI background removal, scaling, and cropping.)
---

# Mini PNG Processor Skill

This skill allows AI agents to automate image editing tasks seamlessly using `mini_png_editor.py`.
(本技能旨在讓 AI 代理人可以自動化操作 `mini_png_editor.py` 進行圖片編修。)

## 🛠️ Core Capabilities / 核心功能
1. **AI Background Removal (AI 去背)**: Uses `rembg` to strip backgrounds, outputting a transparent PNG. (使用 `rembg` 技術移除圖片背景，輸出為透明 PNG。)
2. **Smart Scaling (智慧縮放)**: Resizes images while optionally maintaining aspect ratio. (調整圖片尺寸，支援維持比例。)
3. **Precision Cropping (精確裁切)**: Crops specific areas based on X/Y coordinates and Width/Height dimensions. (根據座標與長寬進行精確裁切。)
4. **Metadata Query (元數據查詢)**: Fetches image dimensions and format info. (取得圖片的長、寬、格式等資訊。)

## 📋 Usage Guidelines / 執行準則

### 1. Operation Priority / 優先順序與依賴性
- The processing order is strictly: **AI Removal -> Scaling -> Cropping**.
  (處理順序固定如下：**AI 去背 -> 縮放 -> 裁切**。)
- Warning: If cropping is requested alongside scaling, the crop coordinates must be calculated based on the *post-scaled* dimensions.
  (注意：如果需要裁切，座標必須基於「縮放後」的圖片尺寸來計算。)

### 2. Execution Methods / 啟動方式
- **Primary (優先使用 MCP)**: Call the MCP server tools (`get_image_info` and `process_image`) natively if the server is active.
  (若環境已配置 MCP Server，請優先呼叫 `get_image_info` 與 `process_image` 工具。)
- **Fallback (後備 CLI 方案)**: If MCP is unavailable, execute via `run_command` using `python "d:\antigravity_workspace\mini_png_editor\mini_png_editor.py"` with the appropriate CLI flags.
  (若 MCP 未啟動，請使用命令列介面執行原生 Python 腳本。)

### 3. Agent Decision Workflow / AI 操作流程建議
- **Step A: Observe (觀察)**: Call `get_image_info` to read original dimensions.
- **Step B: Plan (規劃)**: Compute target dimensions and crop bounding boxes.
- **Step C: Execute (執行)**: Send the process command with absolute paths.
- **Step D: Verify (確認)**: Ensure the output file exists at the expected destination.

## ⌨️ CLI Command Examples / 常用命令範例 (CLI 版)
- **Removal & Scale (去背並縮放)**:
  `python "d:\antigravity_workspace\mini_png_editor\mini_png_editor.py" --input in.png --output out.png --rembg --scale 1024 1024`
- **Precision Cropping (精確裁切)**:
  `python "d:\antigravity_workspace\mini_png_editor\mini_png_editor.py" --input in.png --output out.png --crop 100 100 500 500`

## ⚠️ Important Notes / 注意事項
- **Headless Execution (背景執行)**: CLI and MCP modes do not launch the GUI.
  (CLI 與 MCP 模式純粹在背景運算，不會顯示圖形介面。)
- **Absolute Paths (絕對路徑)**: Always use absolute paths to prevent execution errors across workspaces.
  (強烈建議使用絕對路徑，以避免跨目錄呼叫時發生錯誤。)
- **Format Optimizations (格式限定)**: Optimized purely for PNG operations. Using other formats might trigger auto-conversion to RGBA.
  (核心優化針對 PNG 檔案，其他格式匯入後將自動轉換為具有透明通道的 RGBA 格式。)
