#!/usr/bin/env python3
"""
tts_infer.py — Edge-TTS 批量推理脚本
读取测试文本，调用 Microsoft Edge TTS API 生成合成语音。

用法：
    python tts_demo/tts_infer.py
"""

import asyncio
import csv
import time
from pathlib import Path

# 测试文本（可换你自己的）
TEST_SENTENCES = [
    "今天下午我去了趟图书馆，借了两本关于人工智能的书。",
    "回来的时候路过咖啡店，点了杯拿铁，味道还挺不错的。",
    "最近天气开始热起来了，街上的人都换上了短袖。",
    "我觉得这个项目挺有意思的，如果能顺利跑通就太好了。",
    "语音合成技术这几年进步很快，效果越来越自然了。",
    "明天打算去公园跑步，顺便拍几张照片。",
    "这本书讲的是深度学习在自然语言处理中的应用。",
    "我喜欢在下雨天待在家里听音乐，感觉很放松。",
    "周末约了朋友一起吃饭，好久没见了。",
    "这道数学题有点难，需要花时间仔细想想。",
]

VOICES = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]
OUTPUT_DIR = Path("outputs/generated_audio")
LOG_PATH = Path("tts_demo/inference_log.csv")


async def generate_one(text: str, voice: str, output_path: Path) -> float:
    """生成一条合成语音，返回推理耗时（秒），失败自动重试"""
    import edge_tts

    start = time.time()
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
            elapsed = time.time() - start
            return elapsed
        except Exception as e:
            if attempt == 2:
                raise
            wait = (attempt + 1) * 2
            print(f"          ⚠ 重试 {attempt+1}/3（{wait}s 后）: {e}")
            await asyncio.sleep(wait)
    return 0.0


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logs = []
    sample_id = 1

    for voice in VOICES:
        voice_short = voice.replace("Neural", "").replace("zh-CN-", "")
        for text in TEST_SENTENCES:
            filename = f"edge_{voice_short}_{sample_id:03d}.wav"
            output_path = OUTPUT_DIR / filename

            print(f"  [{sample_id:03d}] {voice_short}: {text[:30]}...")
            elapsed = await generate_one(text, voice, output_path)

            logs.append({
                "id": f"{sample_id:03d}",
                "model_name": "edge-tts",
                "voice": voice,
                "text": text,
                "reference_audio": "N/A",
                "generated_audio": str(output_path),
                "inference_time": f"{elapsed:.1f}",
                "ref_duration": "N/A",
                "remark": "",
            })
            print(f"          → {filename}  ({elapsed:.1f}s)")
            sample_id += 1

            # 间隔 0.5s 防限流
            await asyncio.sleep(0.5)

    # 写 inference_log.csv
    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "model_name", "voice", "text", "reference_audio",
            "generated_audio", "inference_time", "ref_duration", "remark",
        ])
        writer.writeheader()
        writer.writerows(logs)

    print(f"\n  完成！{sample_id - 1} 条合成语音")
    print(f"  音频: {OUTPUT_DIR}/")
    print(f"  日志: {LOG_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
