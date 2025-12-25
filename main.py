import asyncio
import edge_tts
import csv
import os
import pykakasi  # 新增：用於日文轉拼音

# 1. 你的資料清單
data_list = [
    ("私", "我"),
    ("学校", "學校"),
    ("食べる", "吃"),
    ("勉強", "學習"),
    ("美味しい", "好吃"),
    ("おやすみなさい", "晚安"),
]

# 2. 設定
JP_VOICE = "ja-JP-NanamiNeural"
ZH_VOICE = "zh-TW-HsiaoChenNeural"
OUTPUT_FOLDER = r"C:\Users\pfii1\AppData\Roaming\Anki2\job\collection.media"

CSV_FILENAME = "anki_import_with_romaji.csv"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 初始化拼音轉換器
kks = pykakasi.kakasi()


async def generate_anki_data():
    csv_rows = []

    for jp_text, zh_text in data_list:
        print(f"正在處理: {jp_text}...")

        # --- A. 生成羅馬拼音 ---
        result = kks.convert(jp_text)
        # 取得平文式羅馬字 (Hepburn)，並用空白隔開
        romaji = " ".join([item['hepburn'] for item in result])

        # --- B. 生成語音檔案 ---
        jp_filename = f"jp_{jp_text}.mp3"
        zh_filename = f"zh_{zh_text}.mp3"

        # 日文語音
        jp_comm = edge_tts.Communicate(jp_text, JP_VOICE)
        await jp_comm.save(os.path.join(OUTPUT_FOLDER, jp_filename))

        # 中文語音
        zh_comm = edge_tts.Communicate(zh_text, ZH_VOICE)
        await zh_comm.save(os.path.join(OUTPUT_FOLDER, zh_filename))

        # --- C. 整理 CSV 格式 ---
        # 正面：日文 + 聲音
        front_content = f"{jp_text}<br>[sound:{jp_filename}]"

        # 背面：中文 + 羅馬拼音 (小括號) + 中文聲音
        # 使用 <small> 標籤讓羅馬拼音看起來小一點，比較精緻
        back_content = f"{zh_text}<br><small style='color:gray'>({romaji})</small><br>[sound:{zh_filename}]"

        csv_rows.append([front_content, back_content])

    # 寫入 CSV
    with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)

    print(f"\n✅ 處理完成！已加入羅馬拼音。")
    print(f"請記得將 MP3 移至 Anki 媒體資料夾，並匯入 {CSV_FILENAME}")


if __name__ == "__main__":
    asyncio.run(generate_anki_data())