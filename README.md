# Snake Playground

這是一個使用 Python + pygame 製作的可實際遊玩的貪吃蛇遊戲，並使用 `pipenv` 管理虛擬環境與套件。

## Preview

<p align="center">
  <a href="https://drive.google.com/file/d/1lRFaf8gT5_yfv8bi1jo5-XhSNil38mN3/view?usp=drive_link" target="_blank" rel="noopener">
    <img src="assets/preview.png" alt="Snake Playground" width="300">
  </a>
</p>

---

## 環境安裝

1. 安裝 Python 3
2. 安裝 `pipenv`

```bash
pip install pipenv
```

## 專案啟動流程

1. 安裝專案依賴

```bash
pipenv install
```

2. 啟動虛擬環境

```bash
pipenv shell
```

3. 執行遊戲

```bash
python main.py
```

---

## 遊戲說明

### 操作方式

- 遊戲啟動後會先進入主選單。
- 主選單可使用方向鍵切換，按 `Enter` 或 `Space` 確認。
- 主選單也支援滑鼠 hover 與點擊 `Start Game`、`High Scores`、`Quit`。
- 遊戲中使用方向鍵控制蛇移動。
- 遊戲結束後可按 `Enter`、`Space` 或 `R` 重新開始；按 `Esc` 或 `M` 返回主選單。
- 若分數進入前五名，會進入名字輸入畫面：
  - 支援英數與空白鍵輸入
  - 支援 `Backspace`
  - 輸入框有閃爍游標（caret）
  - 名稱最大長度為 `10`
  - 若名稱為空或全空白，會自動改用 `Player`

### 遊戲規則

- 吃到食物後蛇身變長。
- 蛇撞牆不會死亡，會從另一側穿出（wrap-around）。
- 只有撞到自己才會遊戲結束。
- 等級依據「吃到的食物數量」提升，不是依據分數直接提升。
- 每吃到 `5` 個食物升 `1` 級，Level 1 為起始等級。
- 計分、等級、速度聯動：
  - Level 1：每個食物 `+1` 分，速度 `6 FPS`
  - Level 2：每個食物 `+2` 分，速度 `7 FPS`
  - Level 3：每個食物 `+3` 分，速度 `8 FPS`
  - 之後依此類推，速度最高 `20 FPS`
- 遊戲區固定為 `320 x 320`，HUD 位於上方（高度 `40`），不覆蓋遊戲區。
- HUD 只顯示 `Score` 與 `Level`，不顯示速度。

### 主選單與排行榜

- 主選單為封面式畫面，包含背景漸層、裝飾圖形、標題區與選單面板。
- 選單項目在鍵盤選取或滑鼠 hover 時都有明確視覺反饋（高亮、邊框、指示符）。
- `High Scores` 畫面顯示前五名玩家名稱與分數。
- 排行榜資料儲存於 `data/high_scores.json`，重新啟動後仍會保留。
- 若 `data/high_scores.json` 不存在，程式會自動建立預設資料。
