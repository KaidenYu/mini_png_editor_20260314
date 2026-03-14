# Mini PNG Editor 🖼️

A desktop application with a lightweight core for pixel-perfect cropping and scaling, plus an optional (and more resource-intensive) AI-powered background removal feature.
一個核心輕量的圖片處理桌面程式，專注於精確裁切與縮放，並提供可選的 AI 自動去背功能（後者需要依賴較大的模型與套件）。

<img width="1194" height="825" alt="image" src="https://github.com/user-attachments/assets/2d9f2429-d73c-493a-b71e-aee1d817cac3" />

---

## ✨ Key Features / 主要功能
- **1:1 Pixel View / 1:1 像素顯示**: Accurate display of your images without unwanted scaling. (精確顯示圖片原始像素，避免不必要的縮放失真)
- **AI Background Removal / AI 自動去背**: One-click professional background removal using `rembg`. (使用 `rembg` 技術，一鍵實現專業級去背)
- **Interactive Cropping / 互動式裁切**: Drag and resize the crop area directly on the canvas. (直接在畫布上拖曳或縮放裁切區域)
- **Image Scaling / 圖片縮放**: Resize images with fixed or free aspect ratios. (支援固定比例或自由調整圖片尺寸)
- **Visual Zoom / 視覺縮放**: Smooth zooming (Ctrl + Mouse Wheel) for detailed work. (支援 Ctrl + 滾輪平滑縮放，方便細節處理)
- **Drag & Drop / 拖放支援**: Simply drop any PNG file into the app to start (Windows support). (支援將 PNG 檔案直接拖入程式視窗開啟)
- **Crosshair Reference / 中心十字參考**: Toggleable crosshair to precisely align the center of your crop. (可開啟中心十字線，精確對齊裁切區域中心)
- **Save Preview / 存檔預覽**: Verify your final image in a dynamic, centered preview window before saving. (存檔前自動彈出自適應預覽視窗，確保編輯成果符合預期)
- **Feature Toggles / 功能開關**: Easily enable/disable heavy AI features via `settings.py`. (可透過 `settings.py` 輕鬆開啟或關閉負擔較重的 AI 功能)

## 🚀 Installation / 安裝說明

Ensure you have Python installed, then choose **ONE** of the following installation methods based on your hardware:
(請確保已安裝 Python，然後根據您的硬體狀況選擇**其中一種**安裝方式：)

**Option A: Standard / CPU-Only (標準版 / 純 CPU)**
Recommended for most users or computers without NVIDIA GPUs. 
(推薦多數使用者或無 NVIDIA 顯卡的電腦使用。)
```bash
pip install pillow rembg onnxruntime windnd
```

**Option B: NVIDIA GPU Accelerated (NVIDIA 顯示卡加速版)**
For users with NVIDIA GPUs (e.g., RTX 30/40 series) for significantly faster AI background removal. Please be aware of potential DLL dependency issues (see GPU Acceleration section below). 
(擁有 NVIDIA 顯示卡的使用者可大幅提升 AI 去背速度，但請注意可能會遇到 DLL 相依性的問題，詳見下方 GPU 加速說明。)
```bash
pip install pillow rembg onnxruntime-gpu windnd
```
*Note: Make sure to `pip uninstall onnxruntime` if you previously installed the CPU version.* 
*(註：如果之前曾安裝過 CPU 版的套件，請先將其解除安裝，避免衝突。)*

## 🎮 GPU Acceleration (Advanced) / GPU 加速 (進階說明)

To leverage NVIDIA GPU performance (e.g., RTX 4080/4090), follow these version-specific steps:
若要發揮 NVIDIA 顯示卡（例如 RTX 4080/4090）的高效能，請遵循以下特定版本要求：

**🔍 Why are these steps necessary? (為什麼需要這些繁瑣步驟？)**
The AI background removal uses `rembg`, which relies on the `onnxruntime-gpu` Python package as its core engine. This specific package (for example, what `pip` installed for my environment was version **1.24.3**) has strict, hardcoded dependencies for CUDA 12 and expects DLLs in standard paths, which causes version conflicts and path mismatch issues if not configured correctly.
(AI 去背的核心引擎是 Python 套件 `onnxruntime-gpu`。然而，該套件（例如我透過 pip 安裝的版本為 **1.24.3**）在底層寫死了對 **CUDA 12** 的依賴，且預設只會在系統內建的標準路徑尋找 DLL 檔案。這正是導致各種版本不相容以及找不到 cuDNN 錯誤的罪魁禍首。)

1. **CUDA Toolkit 12.x**: `onnxruntime-gpu` currently requires **CUDA 12** (e.g., v12.4, v12.8, v12.9). **CUDA 13 is currently NOT supported.**
   (目前 `onnxruntime-gpu` 僅支援 **CUDA 12** 版本系列。請勿安裝最新的 CUDA 13，否則會找不到對應的 DLL。)
2. **cuDNN 9.x**: You must also install **cuDNN 9**.
   - **Important Note**: cuDNN 9 installs its DLLs in a deep, version-specific subfolder (e.g., `...\CUDNN\v9.x\bin\12.x\x64\`). By default, Python packages like `onnxruntime-gpu` will **fail** to find these because they only search standard PATH locations.
   - (除了 CUDA 外，您還必須安裝 **cuDNN 9**。)
   - (**重要注意**：cuDNN 9 的安裝路徑非常深且帶有版本號，例如 `...\CUDNN\v9.x\bin\12.x\x64\`，而 Python 的 AI 套件預設只會在標準路徑搜尋，這會導致即便安裝了也依然出現「找不到 DLL」的錯誤。)
3. **Portable DLL Support (`lib/`) / 解決方案**:
   - To solve the path mismatch and avoid polluting your system PATH, you can create a `lib/` folder in the project directory.
   - Copy the required DLLs from that deep cuDNN bin folder into this local `lib/` folder. The folder should contain at least:
     - `cudnn64_9.dll`
     - `cudnn_cnn64_9.dll`
     - `cudnn_engines_precompiled64_9.dll`
     - `cudnn_engines_runtime_compiled64_9.dll`
     - `cudnn_graph64_9.dll`
     - `cudnn_heuristic64_9.dll`
     - `cudnn_ops64_9.dll`
   - The application will automatically detect and load these DLLs on startup.
   - (為了徹底解決路徑不匹配的問題，並避免污染系統環境變數，建議在專案目錄下建立 `lib/` 資料夾，並將上述深層目錄內需要的 DLL 檔案複製進去。該資料夾應至少包含上述 7 個 DLL 檔案，確保驅動 AI 引擎所需的所有元件都已備齊。程式啟動時會自動讀取該目錄，確保 100% 成功驅動 GPU。)



## ⚙️ Configuration / 設定 (Settings.py)
The project includes a `settings.py` file that acts like a C-style macro system:
專案包含一個 `settings.py` 檔案，運作方式類似 C 語言的 Macro 系統：
- `ENABLE_REMBG`: Set to `True` (default) to enable AI features. Set to `False` to completely disable the `rembg` import and the associated UI tools, making the app even lighter. (設為 `True` 開啟 AI 功能；設為 `False` 則完全不匯入 `rembg` 套件，讓程式更加輕量。)

## ⚠️ Important Notes for AI / AI 功能注意事項
1. **First-Time Download / 首次下載**: When you use the "Remove BG" feature for the first time, the application will automatically download a pre-trained AI model (approx. 170MB). (首次使用去背功能時，程式會自動從網路下載 AI 模型檔，大小約 170MB。)
2. **Local Processing / 本地運算**: All AI calculations are performed **locally** on your machine. Your images are never uploaded to any server. (所有 AI 運算均在您的**本地電腦**完成，圖片不會上傳到任何伺服器，確保 100% 隱私。)
3. **Threading / 非同步處理**: The AI process runs on a separate thread to keep the user interface responsive. (AI 處理會在獨立執行緒執行，確保介面不會卡死。)

## 🛠️ Usage / 使用方式
1. Run the app / 啟動程式: `python mini_png_editor.py`.
2. Drag a PNG file into the window or use the **Open PNG** button. (將 PNG 檔案拖入視窗，或使用 **Open PNG** 按鈕。)
3. Adjust your crop or scale as needed. (根據需要調整裁切範圍或縮放比例。)
4. Click **Remove BG** if you want a transparent background. (如需去背，點擊 **Remove BG**。)
5. Click **Save PNG** to export your work. (點擊 **Save PNG** 匯出作品。)

---
