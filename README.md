# オブジェクト軌跡追跡システム

動画内のオブジェクトを色で検出し、その軌跡を可視化するPythonプログラムです。

## 機能

- **汎用色検出**: 黄色、赤、青、緑、オレンジ、紫など任意の色のオブジェクトを検出
- **カスタム色設定**: HSV範囲を指定して独自の色を追加可能
- **軌跡可視化**: 線と点で軌跡を描画した動画を生成
- **設定カスタマイズ**: 線の太さ、色、検出パラメータを調整可能
- **オーバーレイ機能**: 元動画に軌跡を重ねた動画を生成

## ファイル構成

### メインファイル
- `universal_object_tracker.py` - 汎用オブジェクト追跡システム（**推奨**）
- `detect_ball.py` - ボール検出とCSV出力（旧版）
- `ball_trajectory_video.py` - 軌跡動画生成（旧版）

### 設定・データファイル
- `requirements.txt` - 必要なPythonライブラリ
- `tracker_config.json` - 追跡設定ファイル（自動生成）
- `*.csv` - 座標データ

## 使用方法

### 1. 環境セットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 汎用オブジェクト追跡（推奨）

```python
from universal_object_tracker import ColorTracker

# トラッカーを初期化
tracker = ColorTracker()

# 利用可能な色を確認
tracker.list_available_colors()

# オブジェクト検出とCSV出力
csv_file = tracker.extract_object_coordinates('video.mp4', 'yellow')

# 軌跡動画生成
tracker.create_trajectory_video(csv_file, 'yellow', 'video.mp4', 'output.mp4')
```

### 3. カスタム色を追加

```python
# ピンク色を追加する例
tracker.add_custom_color(
    color_name="pink",
    hsv_range=[[160, 100, 100], [180, 255, 255]],
    track_color=[255, 192, 203],
    highlight_color=[255, 20, 147],
    display_name="ピンク色"
)
```

### 4. 旧システム（黄色ボール専用）

```bash
python detect_ball.py          # ボール検出
python ball_trajectory_video.py   # 軌跡動画生成
```

## 利用可能な色

- `yellow`: 黄色
- `red`: 赤色  
- `blue`: 青色
- `green`: 緑色
- `orange`: オレンジ色
- `purple`: 紫色

## 出力ファイル

- `detected_[色名]_coordinates.csv` - 検出した座標データ
- `[色名]_trajectory.mp4` - 軌跡のみの動画
- `[色名]_trajectory_overlay.mp4` - 元動画に軌跡をオーバーレイした動画

## 要件

- Python 3.7+
- OpenCV 4.5.0+
- pandas 1.3.0+
- numpy 1.21.0+