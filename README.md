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
- 每吃一個食物，分數加 `1`。
- 撞到牆壁或撞到自己時遊戲結束。
- 畫面左上角會顯示目前分數。
