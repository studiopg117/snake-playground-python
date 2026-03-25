# snake-playground Project (Python + Pygame)

> Follow this specification strictly. Do not ignore any constraints.

## 1. 專案目標

請在目前這個專案中建立一個「可實際遊玩的 Python 貪吃蛇遊戲」。

---

## 2. 環境與工具限制（最高優先）

### 必須遵守

- 必須使用 pipenv 作為虛擬環境與套件管理工具
- 所有套件安裝必須透過 pipenv install

### 禁止

- ❌ 使用 venv
- ❌ 使用 pip install（除非透過 pipenv）

---

## 3. 技術要求

- 使用 Python
- 使用 pygame
- 使用 pipenv 管理虛擬環境
- 以 main.py 作為主程式入口

---

## 4. 專案輸出

### 請建立以下檔案

- main.py（遊戲主程式）
- Pipfile（由 pipenv 自動產生）
- requirements.txt
- README.md

---

## 5. 功能需求

### 請實作以下遊戲功能

#### 核心玩法

- 使用方向鍵控制蛇移動
- 蛇吃到食物後身體變長
- 每吃一個食物分數 +1
- 蛇撞到牆時，不會死亡，需從畫面另一側穿出（wrap-around）

#### 遊戲結束條件

- 撞到自己時遊戲結束

#### UI需求

- 畫面需顯示目前分數
- 遊戲結束後可按鍵重新開始

---

## 6. 專案結構

### 原則

- 保持結構簡單清晰
- 不要過度設計

### 可選

- src/
- assets/

---

## 7. 程式碼品質要求

- 必須加入基本註解
- 命名需清楚
- 保持可讀性
- 避免過度工程化

---

## 8. README.md 要求

### 必須包含

#### 環境安裝

- 說明如何安裝 pipenv

#### 專案啟動流程

- pipenv install
- pipenv shell
- python main.py

#### 遊戲說明

- 操作方式
- 遊戲規則

---

## 9. 執行與驗證

### 請完成以下動作

1. 使用 pipenv install 安裝所有依賴
2. 使用 pipenv shell 啟動虛擬環境
3. 確認 pygame 成功安裝
4. 執行 python main.py
5. 確保遊戲可以正常啟動與遊玩
6. 驗證蛇撞牆後會從另一邊出現，而不是結束遊戲
7. 驗證只有撞到自己時才會遊戲結束
8. 若發生錯誤請自動修正

---

## 10. 最終輸出

### 完成後請提供

1. 建立與修改的所有檔案列表
2. 專案結構說明
3. 如何執行專案
4. 下一步優化建議
