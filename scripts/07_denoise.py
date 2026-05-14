#!/usr/bin/env python3
"""
07_denoise.py — 简单降噪处理
对 VAD 切分后的片段进行频谱减法降噪，输出降噪后音频。

用法：
    python scripts/07_denoise.py --input_dir outputs/preprocess_output/segments --output_dir outputs/preprocess_output/denoised
"""

import argparse
import numpy as np
import soundfile as sf
import noisereduce as nr
from pathlib import Path


def denoise_file(input_path: Path, output_path: Path, sr: int = 16000) -> None:
    """对单文件降噪"""
    signal, orig_sr = sf.read(str(input_path))

    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    # noisereduce 需要至少 0.5 秒的音频
    if len(signal) < sr * 0.5:
        sf.write(str(output_path), signal, orig_sr)
        return

    try:
        cleaned = nr.reduce_noise(
            y=signal,
            sr=orig_sr,
            stationary=False,
            prop_decrease=0.85,
        )
    except Exception:
        # 降噪失败就用原音频
        cleaned = signal

    sf.write(str(output_path), cleaned, orig_sr)


def main():
    parser = argparse.ArgumentParser(description="音频降噪处理")
    parser.add_argument("--input_dir", required=True, help="输入目录（VAD 切分后的 segments）")
    parser.add_argument("--output_dir", required=True, help="输出目录（降噪后）")
    parser.add_argument("--sr", type=int, default=16000, help="采样率")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_files = sorted(input_dir.glob("*.wav"))
    if not audio_files:
        print(f"未找到 wav 文件: {input_dir}")
        return

    print(f"降噪处理: {len(audio_files)} 个文件")
    for i, fpath in enumerate(audio_files):
        out_path = output_dir / fpath.name
        denoise_file(fpath, out_path, args.sr)
        print(f"  [{i+1}/{len(audio_files)}] {fpath.name} ✓")

    print(f"\n降噪完成 → {output_dir}/ ({len(audio_files)} 个文件)")


if __name__ == "__main__":
    main()
