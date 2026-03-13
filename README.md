# Mini PNG Editor 🖼️

A lightweight, powerful desktop application for image processing, focusing on pixel-perfect cropping, scaling, and AI-powered background removal.
一個輕量且強大的圖片處理桌面程式，專注於精確裁切、縮放以及 AI 自動去背功能。

<img width="1194" height="825" alt="image" src="https://github.com/user-attachments/assets/2d9f2429-d73c-493a-b71e-aee1d817cac3" />

---

## ✨ Key Features / 主要功能
- **1:1 Pixel View / 1:1 像素顯示**: Accurate display of your images without unwanted scaling. (精確顯示圖片原始像素，避免不必要的縮放失真)
- **AI Background Removal / AI 自動去背**: One-click professional background removal using `rembg`. (使用 `rembg` 技術，一鍵實現專業級去背)
- **Interactive Cropping / 互動式裁切**: Drag and resize the crop area directly on the canvas. (直接在畫布上拖曳或縮放裁切區域)
- **Image Scaling / 圖片縮放**: Resize images with fixed or free aspect ratios. (支援固定比例或自由調整圖片尺寸)
- **Visual Zoom / 視覺縮放**: Smooth zooming (Ctrl + Mouse Wheel) for detailed work. (支援 Ctrl + 滾輪平滑縮放，方便細節處理)
- **Drag & Drop / 拖放支援**: Simply drop any PNG file into the app to start (Windows support). (支援將 PNG 檔案直接拖入程式視窗開啟)
- **Feature Toggles / 功能開關**: Easily enable/disable heavy AI features via `settings.py`. (可透過 `settings.py` 輕鬆開啟或關閉負擔較重的 AI 功能)

## 🚀 Installation / 安裝說明

Ensure you have Python installed, then run: (請確保已安裝 Python，並執行以下指令：)

```bash
pip install pillow rembg onnxruntime windnd
```

*Note: If you have an NVIDIA GPU, installing `onnxruntime-gpu` instead of `onnxruntime` will significantly speed up the AI background removal. (註：如果您有 NVIDIA 顯示卡，安裝 `onnxruntime-gpu` 取代 `onnxruntime` 將能大幅提升 AI 去背的速度。)*

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
