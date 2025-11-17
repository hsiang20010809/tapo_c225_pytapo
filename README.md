# Tapo C225 PTZ 控制系統技術文件

## 目錄
1. [概述](#概述)
2. [座標系統詳解](#座標系統詳解)
3. [安裝與設定](#安裝與設定)
4. [API 參考](#api-參考)
5. [使用範例](#使用範例)
6. [企業部署建議](#企業部署建議)
7. [故障排除](#故障排除)
8. [附錄](#附錄)

---

## 概述

本文件說明如何透過程式控制 TP-Link Tapo C225 攝影機的 PTZ（Pan-Tilt-Zoom）功能。本系統基於非官方的 `pytapo` 函式庫，提供完整的攝影機控制能力。

### 系統特點
- ✅ 完整的 PTZ 控制（水平旋轉、垂直傾斜）
- ✅ 預設位置管理
- ✅ 自動追蹤控制
- ✅ 隱私模式管理
- ✅ 多攝影機批次管理
- ✅ REST API 介面
- ✅ 場景管理

---

## 座標系統詳解

### 重要概念：相對座標系統

Tapo 攝影機使用**相對座標系統**，而非絕對座標系統。

#### 工作原理

```
當前位置 = (0, 0)
        ↓
執行 moveMotor(10, 5)
        ↓
攝影機移動到新位置
        ↓
新位置變成 (0, 0)
```

**關鍵特性：**
1. 每次移動後，當前位置重置為 (0, 0)
2. 攝影機重啟時會執行校準，回到機械預設位置
3. 沒有「絕對座標」的概念
4. 必須使用**預設位置（Preset）**來記錄和回到特定位置

### 座標範圍

根據 Tapo C200/C210 的資料（C225 應類似）：

| 軸向 | 最小值 | 最大值 | 說明 |
|------|--------|--------|------|
| X（水平） | -170 | +170 | 正值 = 向右，負值 = 向左 |
| Y（垂直） | -35 | +35 | 正值 = 向上，負值 = 向下 |

### 實際應用

由於是相對座標，建議的使用方式：

1. **校準攝影機** → 攝影機回到預設位置
2. **移動到目標位置** → 使用 `moveMotor(x, y)`
3. **儲存為預設** → 使用 `savePreset("名稱")`
4. **之後直接使用預設** → 使用 `setPreset(id)`

---

## 安裝與設定

### 系統需求

- Python 3.8+
- pip
- 網路存取權限到 Tapo 攝影機

### 安裝步驟

```bash
# 1. 安裝 Python 套件
pip install pytapo flask

# 或使用 requirements.txt
pip install -r requirements.txt

# 2. 攝影機設定（在 Tapo App 中）
# - 進入 設定 > 進階設定 > 攝影機帳戶
# - 建立攝影機帳戶（記住帳號密碼）
# - 可能需要啟用 Tapo Lab > 第三方相容性

# 3. 確認網路連線
ping <攝影機IP>
```

### 認證方式

根據韌體版本，認證方式可能不同：

**方式 1：攝影機帳戶**
```python
user = "你設定的帳號"
password = "你設定的密碼"
```

**方式 2：雲端帳戶（較新韌體）**
```python
user = "admin"
password = "TP-Link雲端帳號密碼"
```

---

## API 參考

### TapoC225Controller 類別

#### 初始化
```python
from tapo_c225_controller import TapoC225Controller

controller = TapoC225Controller(
    host="192.168.1.100",
    user="admin",
    password="your_password"
)
controller.connect()
```

#### 移動控制

| 方法 | 參數 | 說明 |
|------|------|------|
| `move(x, y)` | x: int, y: int | 相對位移移動 |
| `move_left(amount)` | amount: int = 10 | 向左移動 |
| `move_right(amount)` | amount: int = 10 | 向右移動 |
| `move_up(amount)` | amount: int = 5 | 向上移動 |
| `move_down(amount)` | amount: int = 5 | 向下移動 |
| `move_step(angle)` | angle: 0-359 | 步進移動（角度控制） |

**步進角度對照：**
- 0° = 順時針/向右
- 90° = 向上
- 180° = 逆時針/向左
- 270° = 向下

#### 預設位置管理

| 方法 | 參數 | 說明 |
|------|------|------|
| `get_presets()` | - | 獲取所有預設位置 |
| `save_preset(name)` | name: str | 儲存當前位置 |
| `goto_preset(preset_id)` | preset_id: str | 移動到預設位置 |
| `delete_preset(preset_id)` | preset_id: str | 刪除預設位置 |

#### 系統控制

| 方法 | 參數 | 說明 |
|------|------|------|
| `calibrate()` | - | 校準馬達（回到預設位置） |
| `get_auto_track()` | - | 獲取自動追蹤狀態 |
| `set_auto_track(enabled)` | enabled: bool | 設定自動追蹤 |
| `enable_privacy_mode()` | - | 啟用隱私模式 |
| `disable_privacy_mode()` | - | 停用隱私模式 |

---

## 使用範例

### 基本控制

```python
from tapo_c225_controller import TapoC225Controller

# 連接
ctrl = TapoC225Controller("192.168.1.100", "admin", "password")
ctrl.connect()

# 移動攝影機
ctrl.move_right(20)    # 向右 20 單位
ctrl.move_up(10)       # 向上 10 單位

# 儲存位置
ctrl.save_preset("入口監控")

# 校準回到預設
ctrl.calibrate()

# 移動到預設位置
presets = ctrl.get_presets()
print(presets)  # {'1': '入口監控', '2': '走廊監控', ...}
ctrl.goto_preset("1")
```

### 自動巡邏

```python
import time

# 在多個預設位置之間巡邏
preset_ids = ["1", "2", "3"]
interval = 30  # 每個位置停留 30 秒

while True:
    for preset_id in preset_ids:
        ctrl.goto_preset(preset_id)
        time.sleep(interval)
```

### REST API 使用

啟動伺服器：
```bash
export TAPO_HOST=192.168.1.100
export TAPO_USER=admin
export TAPO_PASSWORD=your_password
python tapo_rest_api.py
```

API 呼叫範例：
```bash
# 獲取狀態
curl http://localhost:5000/status

# 移動攝影機
curl -X POST http://localhost:5000/move \
  -H "Content-Type: application/json" \
  -d '{"x": 10, "y": 5}'

# 移動到預設位置
curl -X POST http://localhost:5000/goto_preset \
  -H "Content-Type: application/json" \
  -d '{"preset_id": "1"}'

# 儲存預設位置
curl -X POST http://localhost:5000/save_preset \
  -H "Content-Type: application/json" \
  -d '{"name": "會議室入口"}'
```

### 多攝影機管理

```python
from tapo_multi_camera import TapoMultiCameraManager

manager = TapoMultiCameraManager()

# 新增攝影機
manager.add_camera("entrance", "192.168.1.101", "admin", "password")
manager.add_camera("warehouse", "192.168.1.102", "admin", "password")
manager.add_camera("office", "192.168.1.103", "admin", "password")

# 建立場景
manager.create_scene("上班模式", {
    "entrance": "1",
    "warehouse": "2",
    "office": "1"
})

# 套用場景
manager.apply_scene("上班模式")

# 批次操作
manager.calibrate_all()
manager.set_auto_track_all(True)
```

---

## 企業部署建議

### 架構設計

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  前端介面    │────▶│  REST API    │────▶│  Tapo 攝影機 │
│  (Web/App)  │     │   Server     │     │  (Multiple)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   場景管理    │
                    │   排程系統    │
                    │   事件記錄    │
                    └──────────────┘
```

### 安全建議

1. **網路隔離**
   - 將攝影機放在獨立的 VLAN
   - 限制存取權限
   - 使用防火牆規則

2. **密碼管理**
   - 使用環境變數儲存密碼
   - 定期更換密碼
   - 避免在程式碼中硬編碼

3. **API 安全**
   - 加入身份驗證（API Key / JWT）
   - 使用 HTTPS
   - 記錄所有操作

### 監控與維護

1. **定期校準**
   ```python
   # 每天凌晨 3 點校準所有攝影機
   import schedule
   
   def daily_calibration():
       manager.calibrate_all()
   
   schedule.every().day.at("03:00").do(daily_calibration)
   ```

2. **健康檢查**
   ```python
   def health_check():
       for cam_id, ctrl in manager.cameras.items():
           try:
               ctrl.tapo.getBasicInfo()
               print(f"{cam_id}: OK")
           except:
               print(f"{cam_id}: ERROR - 需要檢查")
   ```

3. **日誌記錄**
   ```python
   import logging
   
   logging.basicConfig(
       filename='tapo_operations.log',
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   ```

### 效能考量

- 避免頻繁移動操作（間隔至少 1-2 秒）
- 批次操作時考慮網路頻寬
- 監控馬達壽命（避免 24/7 連續巡邏）

---

## 故障排除

### 常見問題

#### 1. 連線失敗
```
Exception: Invalid authentication data
```
**解決方案：**
- 確認 IP 位址正確
- 嘗試使用 `admin` 作為使用者名稱
- 使用 TP-Link 雲端密碼
- 檢查防火牆設定

#### 2. PTZ 操作失敗
```
Error: -64316
```
**解決方案：**
- 確認隱私模式已關閉
- 檢查攝影機是否支援 PTZ
- 嘗試重新連線

#### 3. 預設位置操作失敗
```
Exception: Preset X is not set in the app
```
**解決方案：**
- 使用 `getPresets()` 確認可用的預設 ID
- 預設 ID 是字串格式

#### 4. 韌體相容性
**解決方案：**
- 更新 pytapo 到最新版本
- 在 Tapo App 中啟用「Tapo Lab > 第三方相容性」
- 查看 pytapo GitHub 的 Issues

### 診斷命令

```python
# 檢查連線
tapo = Tapo(host, user, password)
print(tapo.getBasicInfo())

# 檢查馬達能力
print(tapo.getMotorCapability())

# 檢查隱私模式
print(tapo.getPrivacyMode())

# 測試移動
tapo.moveMotor(0, 0)  # 應該成功但不移動
```

---

## 附錄

### A. 完整方法列表

pytapo 提供的所有可用方法：

```
基本操作：
- getBasicInfo()
- reboot()

PTZ 控制：
- moveMotor(x, y)
- moveMotorStep(angle)
- calibrateMotor()
- getMotorCapability()
- getRotationStatus()

預設位置：
- getPresets()
- savePreset(name)
- setPreset(preset_id)
- deletePreset(preset_id)

追蹤功能：
- getAutoTrackTarget()
- setAutoTrackTarget(enabled)

隱私模式：
- getPrivacyMode()
- setPrivacyMode(enabled)

影像設定：
- getDayNightMode()
- setDayNightMode(mode)
- getImageFlipVertical()
- setImageFlipVertical(enabled)
- getLightFrequencyMode()
- setLightFrequencyMode(mode)

偵測功能：
- getMotionDetection()
- setMotionDetection(enabled, sensitivity)
- getPersonDetection()
- setPersonDetection(enabled, sensitivity)
- getPetDetection()
- setBabyCryDetection(enabled)
- setBarkDetection(enabled)
- setMeowDetection(enabled)

其他：
- getLED()
- setLED(enabled)
- getAlarm()
- setAlarm(enabled)
- getTime()
- setTime()
- getOsd()
- setOsd(enabled)
```

### B. 錯誤代碼參考

| 錯誤代碼 | 說明 | 解決方案 |
|----------|------|----------|
| -64316 | 隱私模式啟用中 | 關閉隱私模式 |
| -40210 | 請求格式錯誤 | 檢查參數 |
| -40401 | 認證失敗 | 檢查帳號密碼 |

### C. 參考資源

- [pytapo GitHub](https://github.com/JurajNyiri/pytapo)
- [Home Assistant Tapo Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control)
- [Tapo 官方支援](https://www.tapo.com/en/support/)

---

## 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| 1.0.0 | 2025-11 | 初始版本 |

---

**注意事項：**
- pytapo 是非官方函式庫，功能可能因韌體更新而改變
- 請遵守當地隱私法規使用監控設備
- 定期備份配置和預設位置設定
