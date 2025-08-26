import cv2
import numpy as np
import pandas as pd
from typing import Tuple, Optional, List, Dict
import json
import os

class ColorTracker:
    """
    任意の色のオブジェクトを追跡するクラス
    """
    
    def __init__(self, config_file: str = None):
        """
        初期化
        
        Args:
            config_file: 設定ファイルのパス
        """
        self.config = self.load_config(config_file) if config_file else self.default_config()
        
    def default_config(self) -> Dict:
        """デフォルト設定"""
        return {
            "colors": {
                "yellow": {
                    "hsv_range": [[15, 50, 50], [35, 255, 255]],
                    "track_color": [0, 255, 0],  # BGR緑
                    "highlight_color": [0, 255, 255],  # BGR黄色
                    "name": "黄色"
                },
                "red": {
                    "hsv_range": [[0, 100, 100], [10, 255, 255]],
                    "track_color": [255, 0, 0],  # BGR青
                    "highlight_color": [0, 0, 255],  # BGR赤
                    "name": "赤色"
                },
                "blue": {
                    "hsv_range": [[100, 100, 100], [130, 255, 255]],
                    "track_color": [0, 255, 255],  # BGR黄色
                    "highlight_color": [255, 0, 0],  # BGR青
                    "name": "青色"
                },
                "green": {
                    "hsv_range": [[40, 100, 100], [80, 255, 255]],
                    "track_color": [255, 0, 255],  # BGRマゼンタ
                    "highlight_color": [0, 255, 0],  # BGR緑
                    "name": "緑色"
                },
                "orange": {
                    "hsv_range": [[10, 100, 100], [25, 255, 255]],
                    "track_color": [0, 128, 255],  # BGRオレンジ
                    "highlight_color": [0, 165, 255],  # BGRオレンジ
                    "name": "オレンジ色"
                },
                "purple": {
                    "hsv_range": [[130, 100, 100], [160, 255, 255]],
                    "track_color": [255, 255, 0],  # BGRシアン
                    "highlight_color": [128, 0, 128],  # BGR紫
                    "name": "紫色"
                }
            },
            "detection": {
                "min_area": 50,
                "morphology_kernel_size": 5,
                "blur_kernel_size": 5
            },
            "trajectory": {
                "line_thickness": 6,
                "highlight_circle_size": 8,
                "fps": 60
            }
        }
    
    def load_config(self, config_file: str) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print(f"設定ファイル {config_file} の読み込みに失敗しました。デフォルト設定を使用します。")
            return self.default_config()
    
    def save_config(self, config_file: str):
        """設定ファイルを保存"""
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def add_custom_color(self, color_name: str, hsv_range: List[List[int]], 
                        track_color: List[int], highlight_color: List[int], 
                        display_name: str = None):
        """
        カスタム色設定を追加
        
        Args:
            color_name: 色の識別名
            hsv_range: HSV範囲 [[h_min, s_min, v_min], [h_max, s_max, v_max]]
            track_color: 軌跡の色 [B, G, R]
            highlight_color: ハイライトの色 [B, G, R]
            display_name: 表示用の名前
        """
        self.config["colors"][color_name] = {
            "hsv_range": hsv_range,
            "track_color": track_color,
            "highlight_color": highlight_color,
            "name": display_name or color_name
        }
    
    def detect_colored_object(self, frame: np.ndarray, color_name: str) -> Optional[Tuple[int, int]]:
        """
        指定した色のオブジェクトを検出
        
        Args:
            frame: 入力フレーム
            color_name: 検出する色の名前
            
        Returns:
            検出されたオブジェクトの中心座標 (x, y) または None
        """
        if color_name not in self.config["colors"]:
            print(f"未知の色: {color_name}")
            return None
        
        color_config = self.config["colors"][color_name]
        hsv_range = color_config["hsv_range"]
        
        # HSVに変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # ガウシアンブラーでノイズ軽減
        blur_size = self.config["detection"]["blur_kernel_size"]
        if blur_size > 1:
            hsv = cv2.GaussianBlur(hsv, (blur_size, blur_size), 0)
        
        # カラーマスクを作成
        lower = np.array(hsv_range[0])
        upper = np.array(hsv_range[1])
        mask = cv2.inRange(hsv, lower, upper)
        
        # 赤色の場合、HSVの境界を跨ぐので特別処理
        if color_name == "red":
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask, mask2)
        
        # モルフォロジー処理でノイズ除去
        kernel_size = self.config["detection"]["morphology_kernel_size"]
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 輪郭検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 最大の輪郭を選択
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 面積チェック
            area = cv2.contourArea(largest_contour)
            min_area = self.config["detection"]["min_area"]
            
            if area > min_area:
                # 重心を計算
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy)
        
        return None
    
    def extract_object_coordinates(self, video_path: str, color_name: str, 
                                 output_csv: str = None, show_preview: bool = True) -> str:
        """
        動画からオブジェクトの座標を抽出
        
        Args:
            video_path: 動画ファイルのパス
            color_name: 検出する色の名前
            output_csv: 出力CSVファイル名
            show_preview: プレビューを表示するか
            
        Returns:
            出力CSVファイルのパス
        """
        if output_csv is None:
            output_csv = f"detected_{color_name}_coordinates.csv"
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        color_config = self.config["colors"][color_name]
        color_name_jp = color_config["name"]
        
        print(f"{color_name_jp}オブジェクトの検出を開始...")
        print(f"動画情報: {frame_count}フレーム, FPS: {fps:.2f}")
        
        results = []
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_number += 1
            timestamp_ms = (frame_number - 1) * (1000 / fps)
            
            # オブジェクト検出
            obj_pos = self.detect_colored_object(frame, color_name)
            
            if obj_pos:
                x, y = obj_pos
                results.append({
                    'frame': frame_number,
                    'timestamp_ms': round(timestamp_ms, 1),
                    'x': x,
                    'y': y
                })
                print(f"フレーム {frame_number}: {color_name_jp}オブジェクト検出 ({x}, {y})")
            else:
                print(f"フレーム {frame_number}: {color_name_jp}オブジェクト未検出")
            
            # プレビュー表示
            if show_preview:
                if obj_pos:
                    highlight_color = tuple(color_config["highlight_color"])
                    cv2.circle(frame, obj_pos, 10, highlight_color, 2)
                    cv2.putText(frame, f"Frame: {frame_number}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, highlight_color, 2)
                
                # 小さく表示
                small_frame = cv2.resize(frame, (540, 960))
                cv2.imshow(f'{color_name_jp}オブジェクト検出', small_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # 結果をCSVに保存
        if results:
            df = pd.DataFrame(results)
            df.to_csv(output_csv, index=False)
            print(f"\n検出結果を {output_csv} に保存しました")
            print(f"検出されたフレーム数: {len(df)}/{frame_count}")
            return output_csv
        else:
            print(f"{color_name_jp}オブジェクトが検出されませんでした")
            return None
    
    def create_trajectory_video(self, csv_path: str, color_name: str, 
                              original_video_path: str = None, 
                              output_path: str = None,
                              custom_line_thickness: int = None,
                              custom_circle_size: int = None) -> str:
        """
        軌跡動画を作成
        
        Args:
            csv_path: CSVファイルのパス
            color_name: 使用する色設定の名前
            original_video_path: 元動画のパス
            output_path: 出力動画のパス
            custom_line_thickness: カスタム線の太さ
            custom_circle_size: カスタム円のサイズ
            
        Returns:
            出力動画のパス
        """
        if output_path is None:
            if original_video_path:
                output_path = f"{color_name}_trajectory_overlay.mp4"
            else:
                output_path = f"{color_name}_trajectory.mp4"
        
        # CSVデータを読み込み
        df = pd.read_csv(csv_path)
        color_config = self.config["colors"][color_name]
        
        if original_video_path and os.path.exists(original_video_path):
            # 元動画を読み込み
            cap = cv2.VideoCapture(original_video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
        else:
            # 座標から動画サイズを決定
            width = int(df['x'].max() - df['x'].min()) + 200
            height = int(df['y'].max() - df['y'].min()) + 200
            fps = self.config["trajectory"]["fps"]
            cap = None
        
        # 動画の初期化
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        track_color = tuple(color_config["track_color"])
        highlight_color = tuple(color_config["highlight_color"])
        line_thickness = custom_line_thickness or self.config["trajectory"]["line_thickness"]
        circle_size = custom_circle_size or self.config["trajectory"]["highlight_circle_size"]
        
        print(f"軌跡動画作成中: {width}x{height}, {len(df)}フレーム")
        
        # 各フレームを処理
        for i in range(len(df)):
            if cap:
                ret, frame = cap.read()
                if not ret:
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
            else:
                frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 軌跡を線で描画
            points = []
            for j in range(i + 1):
                x = int(df.iloc[j]['x'])
                y = int(df.iloc[j]['y'])
                if 0 <= x < width and 0 <= y < height:
                    points.append((x, y))
            
            # 線で軌跡を描画
            if len(points) > 1:
                points_array = np.array(points, dtype=np.int32)
                cv2.polylines(frame, [points_array], False, track_color, thickness=line_thickness)
            
            # 現在のオブジェクト位置を強調
            current_x = int(df.iloc[i]['x'])
            current_y = int(df.iloc[i]['y'])
            
            if 0 <= current_x < width and 0 <= current_y < height:
                cv2.circle(frame, (current_x, current_y), circle_size, highlight_color, -1)
            
            out.write(frame)
        
        # リソースを解放
        out.release()
        if cap:
            cap.release()
        
        print(f"軌跡動画が作成されました: {output_path}")
        return output_path
    
    def list_available_colors(self):
        """利用可能な色設定を表示"""
        print("利用可能な色:")
        for color_key, color_config in self.config["colors"].items():
            hsv_range = color_config["hsv_range"]
            print(f"- {color_key}: {color_config['name']} (HSV: {hsv_range[0]}-{hsv_range[1]})")

def demo_usage():
    """使用例のデモ"""
    # トラッカー初期化
    tracker = ColorTracker()
    
    # 設定を保存
    tracker.save_config("tracker_config.json")
    
    # 利用可能な色を表示
    tracker.list_available_colors()
    
    # カスタム色を追加する例
    tracker.add_custom_color(
        color_name="pink",
        hsv_range=[[160, 100, 100], [180, 255, 255]],
        track_color=[255, 192, 203],  # ライトピンク
        highlight_color=[255, 20, 147],  # ディープピンク
        display_name="ピンク色"
    )
    
    print("\nカスタム色を追加後:")
    tracker.list_available_colors()
    
    # 動画ファイルのパス（実際のファイルに変更してください）
    video_file = "/Users/kashiwabaisamuto/Documents/ロトスコープ/黄色いボールを投げる.mp4"
    
    if os.path.exists(video_file):
        # 黄色のオブジェクトを追跡
        color_to_track = "yellow"
        csv_file = tracker.extract_object_coordinates(video_file, color_to_track, show_preview=False)
        
        if csv_file:
            # 軌跡動画を作成（カスタム設定で）
            tracker.create_trajectory_video(
                csv_file, 
                color_to_track, 
                video_file,
                custom_line_thickness=10,
                custom_circle_size=12
            )
    else:
        print(f"動画ファイルが見つかりません: {video_file}")

if __name__ == "__main__":
    demo_usage()