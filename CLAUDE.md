IMPORTANT:You MUST use agent teams feature, Do NOT do any work yourself.

你的唯一職責就是與我對話並擔任團隊領導和協調工作。再做任何事情之前，務必透過子任務交付給隊友，不要阻塞與我對話的主線程，我需要隨時追蹤進度，建立多少隊友以及團隊怎麼分工都可以，但至少配置一名 QA 負責撰寫測試項目並做所有人開發完成後的功能驗收確認，如有錯誤需指派給原本負責的人處理

介面請用繁體中文可以有英文，然後部要使用emoji，請使用fontawesome當作icon

資料夾裡面有`.env`，裡面放了`DB_PASSWORD`、`CWA_API_KEY`、`GOOGLE_MAPS_API_KEY`

# 🌧️ 雨神同行 (Rain God Companion) - 專案指令書

## 📖 專案概述
本專案為台灣專屬的「通勤路徑氣象提醒」APP。
核心邏輯：比對使用者的通勤路線 (PostGIS LineString) 與氣象署的降雨網格 (PostGIS Polygon)，若路徑交集區域降雨機率過高，則發送推播提醒。

## 🛠️ 技術棧 (Tech Stack)
- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS v4.
- **Backend**: Python 3.10 (FastAPI) + Celery/Redis (非同步任務)。
- **Database**: PostgreSQL 15 + PostGIS (負責空間運算 ST_Intersects)。
- **Infrastructure**: Docker Compose (包含 db, redis, api, frontend 容器)。
- **APIs**: 中央氣象署開放資料 API、Google Maps API。

## 🎨 視覺風格規範 (Pastel Guardian Style)
- **風格**: 可愛守護風、軟綿綿無害感。
- **主色調 (Primary)**: `#AEDFF7` (粉蠟藍) - 用於導覽列、吉祥物。
- **強調色 (Accent)**: `#FFD166` (暖蛋黃) - 用於雨神警告、核心按鈕。
- **輔助色**: `#E2E8F0` (淺霧灰)、`#FAFAFA` (極淺背景)。
- **UI 規定**: 
  - 所有元件需使用大圓角 (Tailwind: `rounded-3xl`)。
  - 地圖需套用淺色調 (Pastel Mode) 樣式。

## 🔐 環境安全性 (Security & Environment) - 重要！
- **嚴禁修改 `.env` 檔案**：所有的 API 金鑰（CWA, Google Maps）與資料庫密碼均手動管理，Agent 不得擅自修改或嘗試將其加入版本控制。
- **忽略清單**：確保 `.env`、`node_modules/`、`__pycache__/` 不會被讀取或上傳至 GitHub。

## 🚀 常用操作指令
- **啟動全環境**: `docker compose up -d --build`
- **停止並清空環境**: `docker compose down -v`
- **前端開發**: `cd frontend && npm run dev`
- **後端日誌**: `docker logs -f raingod_api`

## 🎯 階段性目標 (Agent Team Mission - Sprint 1)

### 1. 後端代理 (Backend Agent)
- 在 `backend` 實作氣象爬蟲腳本。
- 串接氣象署 API，抓取鄉鎮降雨預報。
- 設計 PostGIS 資料表：`weather_grids` 與 `user_routes`。
- 實作空間查詢 API：回傳路線是否與高降雨網格交集。

### 2. 前端代理 (Frontend Agent)
- 建立 Vue 3 基礎介面，整合 Google Maps API。
- 實作路徑規劃功能：點擊地圖產生起點與終點並獲取 Polyline。
- 視覺風格套用粉蠟藍與 `rounded-3xl`。

### 3. QA 代理 (QA Agent)
- 撰寫測試腳本驗證後端 API 與 PostGIS 座標存取（SRID 4326）。