# Mini PNG Editor 技能庫 (Skills Repository) 🧠

This folder contains custom skills designed specifically for AI Agents (like Antigravity). These skills empower AI assistants with the ability to fully automate the core processing engine of `mini_png_editor.py` in the background, without requiring any graphical user interface.
(這個資料夾包含了專為 AI Agent (例如 Antigravity) 所設計的自訂技能 (Skills)。這些技能賦予了 AI 能力，讓 AI 代理人可以完全自動化地在背景操作 `mini_png_editor.py` 的核心處理引擎，而無需開啟圖形化介面。)

## 🌟 Available Skills / 目前可用的技能

### 1. [Mini PNG Processor](./mini-png-processor/SKILL.md)
A powerful and highly stable image processing automation skill. It integrates the native Command Line Interface (CLI) with a Model Context Protocol (MCP) server, enabling the AI to perform the following operations:
(這是一個強大且高度穩定的影像處理自動化技能。它整合了原生命令列介面 (CLI) 與 Model Context Protocol (MCP) 伺服器，讓 AI 可以執行以下操作：)

*   **Image Info Query / 獲取圖片資訊**: Instantly read the image's height, width, color mode, and filename (`get_image_info`).
    (瞬間讀取圖片的長度、寬度、色彩模式與檔名。)
*   **AI Background Removal / AI 智慧去背**: Utilize the built-in `rembg` engine to remove image backgrounds and convert them to transparent PNGs with a single command.
    (透過內建的 `rembg` 引擎，一鍵去除圖片背景並轉為透明 PNG。)
*   **Precision Scaling & Cropping / 精準縮放與裁切**: Supports high-quality Lanczos resampling for scaling and precise, coordinate-based area cropping.
    (支援高品質的 Lanczos 重新取樣縮放，以及基於精確座標的區域裁切。)

#### **Engineering Under the Hood / 運作原理解析：**
This skill is powered by our meticulously optimized **fully-defensive MCP Server** (`mcp/mcp_server.py`). It features:
(這套技能背後搭載了我們精心優化的**全環境防禦型 MCP Server** (`mcp/mcp_server.py`)。它具備以下特點：)

1.  **Lightning-Fast Startup / 極速啟動**: Lazy loads heavy AI modules, ensuring that image info queries (Info mode) complete in milliseconds.
    (延遲載入重型 AI 模組，使得查詢圖片資訊的速度達到毫秒級。)
2.  **Deadlock Prevention / 死鎖防護**: By strictly isolating the child process data streams (`stdin=subprocess.DEVNULL`) and hiding the console window (`CREATE_NO_WINDOW`), it completely prevents the notorious Pipe Deadlock (connection timeouts, EOF errors) common in Windows background execution.
    (透過強制隔離子進程資料流與隱藏視窗，徹底杜絕了在 Windows 背景執行時常見的 Pipe Deadlock (連線超時、EOF 中斷) 問題。)
3.  **Absolute Path Locking / 絕對路徑鎖定**: Guarantees that the agent will accurately locate the editor's Python environment and engine script, no matter what **workspace or project** it is called from.
    (保證了代理人在**任何專案/工作區**呼叫此技能時，都能精準鎖定到這個編輯器的 Python 環境與引擎腳本。)

---

## 💡 How to Use This Skill in Other Projects / 如何在其他專案中使用

If you want to leverage this image processing capability in other Antigravity workspaces, simply ensure:
(如果您在其他 Antigravity 工作區想使用這套影像處理能力，只需確保：)

1.  The `mcp/mcp_server.py` path is added to your global `mcp_config.json` configuration.
    (已將 `mcp/mcp_server.py` 加入到您全域的 `mcp_config.json` 設定中。)
2.  Provide a natural language request in your prompt, for example:
    (在 Prompt 中自然地提出需求，例如：)
    > *"Hey, use the skill to remove the background of this image, and then scale it down to 512x512."*
    > *("幫我用 skill 把這張圖片去背，然後把尺寸縮小到 512x512")*

The AI agent will automatically infer your intent, load this `Mini PNG Processor` skill, and flawlessly complete the complex image processing tasks in the background within a second!
(AI 代理人就會自動解析您的意圖，載入這個 `Mini PNG Processor` 技能，並完美地將繁雜的圖片處理工作在背景一秒完成！)
