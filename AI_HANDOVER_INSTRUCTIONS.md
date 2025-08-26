# iPhoneアプリ開発への引き継ぎ指示書

## プロジェクト概要

動画内のオブジェクトを色で検出し、その軌跡を可視化するPythonシステムを開発済み。これをベースにiPhoneアプリを作成する。

## 既存システムの詳細

### プロジェクト場所
```
/Users/kashiwabaisamuto/Documents/ロトスコープ/
```

### 主要ファイル構成
- `universal_object_tracker.py` - **メインシステム**: 汎用オブジェクト追跡クラス
- `detect_ball.py` - 旧版: ボール検出専用
- `ball_trajectory_video.py` - 旧版: 軌跡動画生成専用
- `requirements.txt` - Python依存関係
- `tracker_config.json` - 色設定・パラメータ
- `README.md` - 詳細なドキュメント
- `yellowball.csv` - 手動作成の座標データ（参考用）
- `detected_yellowball.csv` - 自動検出の座標データ
- `黄色いボールを投げる.mp4` - テスト動画
- `.gitignore` - Git除外設定

### システム機能

1. **汎用色検出**: 任意の色のオブジェクトを検出
2. **プリセット色**: 黄色、赤、青、緑、オレンジ、紫の6色
3. **カスタム色追加**: HSV範囲を指定して独自色を定義
4. **軌跡可視化**: 線で軌跡を描画した動画生成
5. **オーバーレイ機能**: 元動画に軌跡を重ねた動画出力
6. **設定カスタマイズ**: 線の太さ、色、検出パラメータを調整可能

### 技術仕様

**Python環境:**
- Python 3.7+
- OpenCV 4.5.0+
- pandas 1.3.0+
- numpy 1.21.0+

**主要クラス: `ColorTracker`**
```python
# 初期化
tracker = ColorTracker()

# オブジェクト検出
csv_file = tracker.extract_object_coordinates('video.mp4', 'yellow')

# 軌跡動画生成
tracker.create_trajectory_video(csv_file, 'yellow', 'video.mp4', 'output.mp4')

# カスタム色追加
tracker.add_custom_color(
    color_name="pink",
    hsv_range=[[160, 100, 100], [180, 255, 255]],
    track_color=[255, 192, 203],
    highlight_color=[255, 20, 147]
)
```

### 検出アルゴリズム
1. BGRからHSV色空間に変換
2. 指定HSV範囲でカラーマスク作成
3. ガウシアンブラーでノイズ軽減
4. モルフォロジー処理（オープン・クローズ）
5. 輪郭検出で最大面積のオブジェクトを選択
6. モーメントで重心計算

### 出力形式
- **CSV**: `frame,timestamp_ms,x,y`
- **動画**: MP4形式、元動画と同じ解像度・FPS

## iPhoneアプリ開発要件

### 目標
既存のPythonシステムの機能をiOSアプリとして実装し、iPhone単体で動画撮影・オブジェクト追跡・軌跡表示を可能にする。

### 必須機能
1. **動画撮影**: iPhoneカメラでリアルタイム撮影
2. **色選択UI**: プリセット色選択 + カスタム色設定
3. **オブジェクト検出**: リアルタイムまたは撮影後処理
4. **軌跡表示**: 検出したオブジェクトの軌跡を可視化
5. **動画保存**: 軌跡付き動画をカメラロールに保存
6. **設定画面**: 検出パラメータ・表示設定の調整

### 技術選択肢
- **言語**: Swift
- **フレームワーク**: UIKit + AVFoundation + Vision + Core Image
- **画像処理**: OpenCV for iOS または Core Image + Vision
- **UI**: Storyboard または SwiftUI

### アーキテクチャ提案
```
ObjectTracker/
├── Models/
│   ├── ColorConfig.swift      # 色設定モデル
│   ├── TrackingResult.swift   # 追跡結果モデル
│   └── VideoProcessor.swift   # 動画処理クラス
├── Views/
│   ├── CameraViewController.swift    # カメラ画面
│   ├── ColorSelectorView.swift      # 色選択UI
│   ├── SettingsViewController.swift  # 設定画面
│   └── TrajectoryOverlayView.swift  # 軌跡オーバーレイ
├── Services/
│   ├── ObjectDetectionService.swift # オブジェクト検出
│   ├── TrajectoryRenderer.swift     # 軌跡描画
│   └── VideoExporter.swift          # 動画出力
└── Resources/
    ├── ColorPresets.plist           # プリセット色設定
    └── DetectionSettings.plist      # 検出パラメータ
```

### UI/UX要件
1. **メイン画面**: カメラプレビュー + 録画ボタン
2. **色選択**: タップで色選択 + HSVスライダー
3. **リアルタイムフィードバック**: 検出対象をハイライト表示
4. **軌跡設定**: 線の太さ・色・透明度調整
5. **結果表示**: 軌跡付き動画のプレビューと保存

### Core Image/Vision実装方針
```swift
// HSVフィルタリング
let hsvFilter = CIFilter.colorMatrix()
hsvFilter.inputImage = inputImage
hsvFilter.rVector = CIVector(x: r, y: g, z: b, w: a)

// Vision使用例
let request = VNDetectRectanglesRequest { request, error in
    // 検出結果処理
}
```

### 参考実装ポイント
1. **HSV変換**: `CIFilter.colorMatrix`または手動実装
2. **モルフォロジー**: `CIFilter.morphologyGradient`
3. **輪郭検出**: Vision framework + カスタム処理
4. **動画合成**: `AVMutableComposition`で軌跡オーバーレイ

### Pythonコードからの移植対象
- `detect_colored_object()` → `ObjectDetectionService`
- `create_trajectory_video()` → `TrajectoryRenderer` + `VideoExporter`
- HSV範囲設定 → `ColorConfig`モデル
- 設定システム → UserDefaults + Settings画面

## 作業開始手順

### 1. 既存コードの理解
```bash
cd "/Users/kashiwabaisamuto/Documents/ロトスコープ"
git log --oneline  # コミット履歴確認
python universal_object_tracker.py  # 動作テスト
```

### 2. Xcodeプロジェクト作成
- Single View App テンプレート
- Camera usage permission設定
- OpenCV または Core Image + Vision導入

### 3. 段階的実装
1. **Phase 1**: カメラプレビュー + 基本UI
2. **Phase 2**: 静止画での色検出テスト
3. **Phase 3**: リアルタイム検出
4. **Phase 4**: 軌跡描画・動画保存
5. **Phase 5**: UI/UX改善・設定機能

### 4. テストデータ
- `黄色いボールを投げる.mp4`を使用してテスト
- HSV範囲: 黄色 `[15,50,50]-[35,255,255]`

## 重要な技術的詳細

### HSV範囲（既存システムで動作確認済み）
- **黄色**: `[[15, 50, 50], [35, 255, 255]]`
- **赤**: `[[0, 100, 100], [10, 255, 255]]` + `[[170, 100, 100], [180, 255, 255]]`
- **青**: `[[100, 100, 100], [130, 255, 255]]`

### 検出パラメータ
- 最小面積: 50px
- モルフォロジーカーネル: 5x5
- ガウシアンブラー: 5x5

### パフォーマンス考慮事項
- リアルタイム処理のためフレーム解像度を調整
- バックグラウンド処理でUI応答性確保
- メモリ効率的な画像処理

このシステムは完全に動作しており、40フレームの黄色ボール軌跡を正確に検出・可視化できることを確認済みです。

---
**作業開始前に必ず既存のREADME.mdと実際のコードを確認してください。**