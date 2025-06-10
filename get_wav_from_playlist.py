import subprocess
import os
import pandas as pd
import re

os.environ['PYTHONUTF8'] = '1'

# 재생목록 리스트
yt_list = [
    'PLjj5QK2aFwtxvqUCAhTywPry4Znd0bBU4'
]

# 다운로드 경로
os.makedirs("downloads", exist_ok=True)

# 파일 이름에 쓸 수 없는 문자 제거
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

data_pairs = []

for list_name in yt_list:
    playlist_url = f"https://www.youtube.com/playlist?list={list_name}"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--skip-download",
        "--get-title",
        "--get-id",
        "--get-duration",
        "--encoding", "utf-8",
        playlist_url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        lines = result.stdout.splitlines()

        # 영상 정보는 3줄씩 묶임: title, id, duration
        print(lines)
        for i in range(0, len(lines), 3):
            title = lines[i]
            video_id = lines[i+1]
            duration = lines[i+2]
            url = f"https://www.youtube.com/watch?v={video_id}"
            safe_title = sanitize_filename(title)
            output_path = f"downloads/{safe_title}.wav"

            # wav 파일로 저장
            if not os.path.exists(output_path):
                print(f"Downloading: {title}")
                try:
                    subprocess.run([
                        "yt-dlp",
                        "-x", "--audio-format", "wav",
                        "-o", output_path,
                        url
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to download {title}: {e}")
                    continue
            else:
                print(f"Already exists: {safe_title}.wav")

            # 데이터 저장
            data_pairs.append((title, video_id, duration))

    except subprocess.CalledProcessError as e:
        print(f"Failed to process playlist {playlist_url}")
        print(e.stderr)

# CSV 저장
df = pd.DataFrame(data_pairs, columns=["Title of Video", "YT id", "Duration"])
df.to_csv("playlist_data.csv", index=False, encoding='utf-8')
print("CSV saved: playlist_output.csv")
