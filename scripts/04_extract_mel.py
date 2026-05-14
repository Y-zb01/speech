"""Mel 特征提取：提取 Mel 频谱保存为 .npy，并绘制示例图"""
import argparse
import yaml
from pathlib import Path
import soundfile as sf
import numpy as np
import librosa
import matplotlib.pyplot as plt


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Mel 特征提取")
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    wav_dir = project_root / config.get("wav_dir", "outputs/processed_dataset/wavs")
    mel_dir = project_root / config.get("output_dir", "outputs/processed_dataset/mels")
    mel_dir.mkdir(parents=True, exist_ok=True)

    sample_rate = config["sample_rate"]
    n_fft = config["n_fft"]
    hop_length = config["hop_length"]
    win_length = config["win_length"]
    n_mels = config["n_mels"]
    fmin = config["fmin"]
    fmax = config["fmax"]

    wav_files = sorted(Path(wav_dir).glob("*.wav"))
    if not wav_files:
        print("没有找到 wav 文件，请先运行 01_convert_audio.py")
        return

    for wav_path in wav_files:
        y, sr = librosa.load(str(wav_path), sr=sample_rate, mono=True)
        mel = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_length,
            win_length=win_length, n_mels=n_mels, fmin=fmin, fmax=fmax
        )
        mel_db = librosa.power_to_db(mel, ref=np.max)
        np.save(mel_dir / f"{wav_path.stem}.npy", mel_db)
        print(f"  ✓ {wav_path.name} → mel shape {mel_db.shape}")

    print(f"Mel 提取完成，共 {len(wav_files)} 条 → {mel_dir}")

    # 绘制第一个音频的 Mel 频谱图
    first_mel = sorted(mel_dir.glob("*.npy"))[0]
    mel = np.load(first_mel)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mel, sr=sample_rate, hop_length=hop_length,
                             x_axis="time", y_axis="mel", fmin=fmin, fmax=fmax)
    plt.colorbar(format="%+2.0f dB")
    plt.title(f"Mel Spectrogram — {first_mel.stem}")
    plt.tight_layout()

    chart_path = project_root / "docs" / "mel_example.png"
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"Mel 示例图 → {chart_path}")


if __name__ == "__main__":
    main()
