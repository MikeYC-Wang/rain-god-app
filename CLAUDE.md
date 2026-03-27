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

## 🚀 常用操作指令
- **啟動全環境**: `docker compose up -d --build`
- **停止並清空環境**: `docker compose down -v`
- **前端開發**: `cd frontend && npm run dev`
- **後端日誌**: `docker logs -f raingod_api`

## 🎯 階段性目標 (Agent Team Mission - Sprint 1)

### 1. 後端代理 (Backend Agent)
- 在 `backend` 實作氣象爬蟲腳本。
- 串接氣象署 API，抓取鄉鎮降雨預報。
- 設計 PostGIS 資料表：`weather_grids` (儲存網格與降雨率) 及 `user_routes` (儲存路線)。
- 實作空間查詢 API：給予一條路線，回傳是否會與高降雨網格交集。

### 2. 前端代理 (Frontend Agent)
- 建立 Vue 3 基礎介面，套用 Tailwind v4 設定。
- 整合 Google Maps API 顯示地圖。
- 實作路徑規劃功能：使用者點擊地圖產生起點與終點，並獲取 Polyline 經緯度陣列。
- 套用 `rounded-3xl` 與粉蠟藍配色。

### 3. QA 代理 (QA Agent)
- 撰寫測試腳本驗證後端 API。
- 確保經緯度資料存入 PostGIS 時格式正確（SRID 4326）。
- 測試氣象資料抓取失敗時的例外處理。

## 📂 檔案結構規範
- `/backend`: FastAPI 程式碼、Dockerfile、requirements.txt。
- `/frontend`: Vue 3 程式碼、Vite 設定、Tailwind 設定。
- `/.env`: 存放 DB_PASSWORD, CWA_API_KEY, GOOGLE_MAPS_API_KEY。