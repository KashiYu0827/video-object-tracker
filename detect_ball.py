import cv2
import numpy as np
import pandas as pd
from typing import Tuple, Optional

def detect_yellow_ball(frame: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    フレームから黄色いボールを検出する
    
    Args:
        frame: 入力フレーム
        
    Returns:
        検出されたボールの中心座標 (x, y) または None
    """
    # HSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 黄色の範囲を定義（複数の黄色の範囲を試す）
    # 範囲1: より明るい黄色
    lower_yellow1 = np.array([20, 100, 100])
    upper_yellow1 = np.array([30, 255, 255])
    
    # 範囲2: より暗い黄色
    lower_yellow2 = np.array([15, 50, 50])
    upper_yellow2 = np.array([35, 255, 255])
    
    # マスクを作成
    mask1 = cv2.inRange(hsv, lower_yellow1, upper_yellow1)
    mask2 = cv2.inRange(hsv, lower_yellow2, upper_yellow2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # ノイズ除去
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 輪郭検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 最大の輪郭を選択
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 面積が十分大きい場合のみ
        area = cv2.contourArea(largest_contour)
        if area > 50:  # 最小面積を設定
            # 重心を計算
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)
    
    return None

def extract_ball_coordinates(video_path: str, output_csv: str = 'detected_ball_coordinates.csv'):
    """
    動画からボールの座標を抽出してCSVに保存
    
    Args:
        video_path: 動画ファイルのパス
        output_csv: 出力CSVファイル名
    """
    cap = cv2.VideoCapture(video_path)
    
    # 動画情報を取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"動画情報: {frame_count}フレーム, FPS: {fps:.2f}")
    
    results = []
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_number += 1
        timestamp_ms = (frame_number - 1) * (1000 / fps)
        
        # ボール検出
        ball_pos = detect_yellow_ball(frame)
        
        if ball_pos:
            x, y = ball_pos
            results.append({
                'frame': frame_number,
                'timestamp_ms': round(timestamp_ms, 1),
                'x': x,
                'y': y
            })
            print(f"フレーム {frame_number}: ボール検出 ({x}, {y})")
        else:
            print(f"フレーム {frame_number}: ボール未検出")
        
        # プレビュー表示（オプション）
        if ball_pos:
            cv2.circle(frame, ball_pos, 10, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_number}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 小さく表示（確認用）
        small_frame = cv2.resize(frame, (540, 960))
        cv2.imshow('Detection Preview', small_frame)
        
        # 'q'キーで終了
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
    else:
        print("ボールが検出されませんでした")

def create_detection_preview(video_path: str):
    """
    検出プロセスのプレビュー版（手動確認用）
    """
    cap = cv2.VideoCapture(video_path)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # ボール検出
        ball_pos = detect_yellow_ball(frame)
        
        if ball_pos:
            cv2.circle(frame, ball_pos, 10, (0, 255, 0), 2)
            cv2.putText(frame, f"Ball: {ball_pos}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 小さく表示
        small_frame = cv2.resize(frame, (540, 960))
        cv2.imshow('Ball Detection Preview', small_frame)
        
        # キー操作
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # スペースキーで一時停止
            cv2.waitKey(0)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_file = "/Users/kashiwabaisamuto/Documents/ロトスコープ/黄色いボールを投げる.mp4"
    
    print("ボール検出を開始します...")
    print("プレビューウィンドウが開きます。'q'で終了、スペースで一時停止")
    
    # まずプレビューで確認
    # create_detection_preview(video_file)
    
    # 実際の検出とCSV出力
    extract_ball_coordinates(video_file, 
                           "/Users/kashiwabaisamuto/Documents/ロトスコープ/detected_yellowball.csv")