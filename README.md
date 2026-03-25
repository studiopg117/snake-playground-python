# Snake Playground

這是一個使用 Python 與 pygame 製作的可實際遊玩的貪吃蛇遊戲，並使用 `pipenv` 管理虛擬環境與套件。

## 環境安裝

1. 安裝 Python 3
2. 安裝 `pipenv`

```bash
pip install pipenv
```

如果你的系統已安裝 `pipenv`，可以直接進行下一步。

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

## 遊戲說明

### 操作方式

- 使用鍵盤方向鍵控制蛇移動。
- 遊戲結束後可按 `Enter`、`Space` 或 `R` 重新開始。

### 遊戲規則

- 吃到紅色食物後，蛇身會變長。
- 等級依據吃到的食物數量提升，而不是依據分數直接提升。
- 每吃到 `5` 個食物提升 `1` 個等級，Level 1 為起始等級。
- Level 1 每次吃到食物加 `1` 分，Level 2 每次加 `2` 分，Level 3 每次加 `3` 分，之後依此類推。
- 遊戲速度會依據目前等級自動調整，Level 1 為 `6 FPS`，每提升 1 個等級增加 `1 FPS`，最高為 `20 FPS`。
- 撞到牆壁時會從另一側穿出（wrap-around），只有撞到自己時才會遊戲結束。
- 畫面頂部有獨立 HUD 資訊列，會顯示目前分數、等級與速度，且不會覆蓋遊戲區。
