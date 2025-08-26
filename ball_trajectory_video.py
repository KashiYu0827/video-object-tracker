import cv2
import pandas as pd
import numpy as np

def create_trajectory_video(csv_path, output_path='ball_trajectory.mp4', fps=60):
    """
    CSVファイルからボールの軌跡を描画した動画を作成
    
    Args:
        csv_path: CSVファイルのパス
        output_path: 出力動画のパス
        fps: フレームレート
    """
    
    # CSVデータを読み込み
    df = pd.read_csv(csv_path)
    
    # 動画のサイズを座標の範囲から決定
    width = int(max(df['x'].max(), df['y'].max())) + 100
    height = int(max(df['x'].max(), df['y'].max())) + 100
    
    # 動画の初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"動画サイズ: {width}x{height}")
    print(f"フレーム数: {len(df)}")
    
    # 各フレームを処理
    for i in range(len(df)):
        # 黒い背景を作成
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 現在のフレームまでの軌跡を線で描画
        points = []
        for j in range(i + 1):
            x = int(df.iloc[j]['x'])
            y = int(df.iloc[j]['y'])
            points.append((x, y))
        
        # 線で軌跡を描画
        if len(points) > 1:
            points_array = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [points_array], False, (0, 255, 0), thickness=8)
        
        # 現在のボール位置を黄色で強調
        current_x = int(df.iloc[i]['x'])
        current_y = int(df.iloc[i]['y'])
        cv2.circle(frame, (current_x, current_y), 8, (0, 255, 255), -1)
        
        # フレーム番号を表示
        cv2.putText(frame, f'Frame: {i+1}/{len(df)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    # リソースを解放
    out.release()
    print(f"動画が作成されました: {output_path}")

def create_trajectory_overlay_video(csv_path, original_video_path=None, output_path='ball_trajectory_overlay.mp4'):
    """
    元の動画に軌跡をオーバーレイする版
    
    Args:
        csv_path: CSVファイルのパス
        original_video_path: 元動画のパス（Noneの場合は軌跡のみ）
        output_path: 出力動画のパス
    """
    
    # CSVデータを読み込み
    df = pd.read_csv(csv_path)
    
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
        fps = 60
    
    # 動画の初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"動画サイズ: {width}x{height}")
    print(f"フレーム数: {len(df)}")
    
    # 各フレームを処理
    for i in range(len(df)):
        if original_video_path and os.path.exists(original_video_path):
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
            cv2.polylines(frame, [points_array], False, (0, 255, 0), thickness=6)
        
        # 現在のボール位置を黄色で強調
        current_x = int(df.iloc[i]['x'])
        current_y = int(df.iloc[i]['y'])
        
        if 0 <= current_x < width and 0 <= current_y < height:
            cv2.circle(frame, (current_x, current_y), 8, (0, 255, 255), -1)
        
        out.write(frame)
    
    # リソースを解放
    out.release()
    if original_video_path:
        cap.release()
    
    print(f"軌跡オーバーレイ動画が作成されました: {output_path}")

if __name__ == "__main__":
    import os
    
    csv_file = "/Users/kashiwabaisamuto/Documents/ロトスコープ/detected_yellowball.csv"
    original_video = "/Users/kashiwabaisamuto/Documents/ロトスコープ/黄色いボールを投げる.mp4"
    
    # 軌跡のみの動画を作成
    create_trajectory_video(csv_file, 
                          output_path="/Users/kashiwabaisamuto/Documents/ロトスコープ/ball_trajectory.mp4")
    
    # 元動画にオーバーレイ版も作成
    create_trajectory_overlay_video(csv_file,
                                   original_video_path=original_video,
                                   output_path="/Users/kashiwabaisamuto/Documents/ロトスコープ/ball_trajectory_overlay.mp4")