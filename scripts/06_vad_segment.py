#!/usr/bin/env python3
"""
06_vad_segment.py — VAD 语音活动检测与长音频切分
基于能量阈值 + 平滑处理，将长音频切分为多个短语音片段。

用法：
    python scripts/06_vad_segment.py --config configs/vad_config.yaml
"""

import argparse
import numpy as np
import soundfile as sf
import librosa
import yaml
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def energy_vad(
    signal: np.ndarray,
    sr: int,
    frame_ms: float = 25.0,
    min_speech_duration: float = 1.0,
    max_speech_duration: float = 15.0,
    merge_gap: float = 0.3,
    threshold_scale: float = 0.3,
) -> list:
    """
    基于能量的 VAD 检测。
    返回 [(start_sec, end_sec), ...]
    """
    frame_len = int(sr * frame_ms / 1000)
    hop_len = frame_len // 2

    if len(signal) < frame_len:
        return []

    # 计算每帧能量
    num_frames = (len(signal) - frame_len) // hop_len + 1
    energy = np.zeros(num_frames)
    for i in range(num_frames):
        start = i * hop_len
        chunk = signal[start : start + frame_len]
        energy[i] = np.sqrt(np.mean(chunk**2))

    if np.max(energy) < 1e-8:
        return []

    # 归一化
    energy = energy / np.max(energy)

    # 阈值
    threshold = np.mean(energy) * threshold_scale + np.median(energy) * (1 - threshold_scale) * 0.5
    if threshold < 0.01:
        threshold = 0.01

    # 找到语音 / 非语音帧
    is_speech = energy > threshold

    # 平滑：去掉孤立帧
    min_speech_frames = max(1, int(0.1 / (hop_len / sr)))
    min_silence_frames = max(1, int(merge_gap / (hop_len / sr)))

    # 中值滤波平滑
    from scipy.ndimage import median_filter
    is_speech = median_filter(is_speech.astype(float), size=3) > 0.5

    # 合并相邻语音段
    segments = []
    in_speech = False
    speech_start = 0

    for i in range(len(is_speech)):
        t = i * hop_len / sr
        if is_speech[i] and not in_speech:
            speech_start = t
            in_speech = True
        elif not is_speech[i] and in_speech:
            segments.append((speech_start, t))
            in_speech = False

    if in_speech:
        segments.append((speech_start, (len(is_speech) - 1) * hop_len / sr))

    # 合并间隔 < merge_gap 的相邻段
    merged = []
    for seg in segments:
        if not merged:
            merged.append(seg)
        else:
            if seg[0] - merged[-1][1] < merge_gap:
                merged[-1] = (merged[-1][0], seg[1])
            else:
                merged.append(seg)

    # 按最小时长/最大时长过滤
    result = []
    for start, end in merged:
        dur = end - start
        if min_speech_duration <= dur:
            # 过长则截断
            if dur > max_speech_duration:
                for sub_start in np.arange(start, end, max_speech_duration):
                    sub_end = min(sub_start + max_speech_duration, end)
                    if sub_end - sub_start >= min_speech_duration:
                        result.append((sub_start, sub_end))
            else:
                result.append((start, end))

    return result


def plot_vad(
    signal: np.ndarray,
    sr: int,
    segments: list,
    output_path: str,
):
    """绘制 VAD 检测结果可视化图"""
    time = np.arange(len(signal)) / sr

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(time, signal, color="steelblue", alpha=0.6, linewidth=0.5)

    # 高亮语音段
    for start, end in segments:
        ax.axvspan(start, end, color="limegreen", alpha=0.25)
        ax.axvline(start, color="green", alpha=0.5, linewidth=0.8)
        ax.axvline(end, color="green", alpha=0.5, linewidth=0.8)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"VAD Segmentation ({len(segments)} speech segments)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"VAD 结果图 → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="VAD 语音活动检测与切分")
    parser.add_argument("--config", default="configs/vad_config.yaml", help="配置文件路径")
    args = parser.parse_args()

    cfg = load_config(args.config)

    input_audio = Path(cfg["input_audio"])
    output_dir = Path(cfg["output_dir"])
    segments_dir = output_dir
    segments_dir.mkdir(parents=True, exist_ok=True)

    target_sr = cfg.get("sample_rate", 16000)
    min_dur = cfg.get("min_speech_duration", 1.0)
    max_dur = cfg.get("max_speech_duration", 15.0)
    merge_gap = cfg.get("merge_gap", 0.3)

    print(f"读取长音频: {input_audio}")
    signal, orig_sr = sf.read(str(input_audio))

    # 转 mono
    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    # 重采样到目标采样率
    if orig_sr != target_sr:
        signal = librosa.resample(signal, orig_sr=orig_sr, target_sr=target_sr)

    duration = len(signal) / target_sr
    print(f"音频时长: {duration:.1f}s, 采样率: {target_sr}Hz")

    # VAD 检测
    print(f"VAD 参数: min={min_dur}s, max={max_dur}s, merge_gap={merge_gap}s")
    segments = energy_vad(
        signal,
        target_sr,
        min_speech_duration=min_dur,
        max_speech_duration=max_dur,
        merge_gap=merge_gap,
    )

    print(f"检测到 {len(segments)} 个语音片段")

    # 保存 vad_result.csv
    csv_path = segments_dir.parent / "vad_result.csv"
    stem = input_audio.stem
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("file,segment_id,start_s,end_s,duration_s\n")
        for i, (start, end) in enumerate(segments):
            dur = end - start
            seg_name = f"{stem}_seg_{i:03d}.wav"
            f.write(f"{input_audio.name},{seg_name},{start:.3f},{end:.3f},{dur:.3f}\n")

            # 切出音频片段
            start_sample = int(start * target_sr)
            end_sample = int(end * target_sr)
            seg_signal = signal[start_sample:end_sample]
            sf.write(str(segments_dir / seg_name), seg_signal, target_sr)
            print(f"  [{i+1:03d}] {seg_name}  ({start:.2f}s - {end:.2f}s, {dur:.2f}s)")

    print(f"\nVAD 结果 → {csv_path}")
    print(f"切分音频 → {segments_dir}/ ({len(segments)} 个片段)")

    # 绘图
    plot_vad(signal, target_sr, segments, "docs/vad_result.png")


if __name__ == "__main__":
    main()
