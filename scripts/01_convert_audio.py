"""音频格式转换：mp3/m4a/flac/wav → wav (24000Hz / mono / PCM16)"""
import argparse
import yaml
from pathlib import Path
import soundfile as sf
import librosa


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="音频格式转换")
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / config["data_dir"]
    output_dir = project_root / config["output_dir"] / "wavs"
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_rate = config["sample_rate"]

    audio_files = sorted(data_dir.glob("*"))
    converted = 0

    for audio_path in audio_files:
        if not audio_path.is_file():
            continue
        suffix = audio_path.suffix.lower()
        if suffix not in (".mp3", ".m4a", ".flac", ".wav"):
            continue

        y, sr = librosa.load(str(audio_path), sr=sample_rate, mono=True)
        out_path = output_dir / f"{audio_path.stem}.wav"
        sf.write(str(out_path), y, sample_rate, subtype="PCM_16")
        converted += 1
        print(f"  ✓ {audio_path.name} → {out_path.name}")

    print(f"转换完成，共 {converted} 条音频 → {output_dir}")


if __name__ == "__main__":
    main()
