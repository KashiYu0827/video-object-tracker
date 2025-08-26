# オブジェクト軌跡追跡システム

動画内のオブジェクトを色で検出し、その軌跡を可視化するPythonプログラムです。

## 機能

- 黄色いボールなど、指定した色のオブジェクトを自動検出
- フレームごとの座標をCSVファイルに出力
- 軌跡を線で描画した動画を生成
- 元動画にオーバーレイ表示も可能

## ファイル構成

- `detect_ball.py` - ボール検出とCSV出力
- `ball_trajectory_video.py` - 軌跡動画生成
- `yellowball.csv` - 元のボール座標データ（手動作成）
- `detected_yellowball.csv` - 自動検出したボール座標データ

## 使用方法

### 1. 環境セットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install opencv-python pandas numpy
```

### 2. オブジェクト検出

```bash
python detect_ball.py
```

### 3. 軌跡動画生成

```bash
python ball_trajectory_video.py
```

## 出力ファイル

- `ball_trajectory.mp4` - 軌跡のみの動画
- `ball_trajectory_overlay.mp4` - 元動画に軌跡をオーバーレイした動画

## 要件

- Python 3.7+
- OpenCV
- pandas
- numpy