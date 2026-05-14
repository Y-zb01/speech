"""生成 metadata：汇总音频路径、文本和时长，输出 metadata.csv"""
import argparse
import yaml
from pathlib import Path
import soundfile as sf


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="生成 metadata")
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / config["output_dir"]
    wav_dir = output_dir / "wavs"
    transcript_path = output_dir / "transcript_clean.txt"

    # 读取文本
    text_map = {}
    if transcript_path.exists():
        with open(transcript_path, "r") as f:
            for line in f:
                parts = line.strip().split("|", 1)
                if len(parts) == 2:
                    text_map[parts[0]] = parts[1]

    # 生成 metadata
    metadata_path = output_dir / "metadata.csv"
    with open(metadata_path, "w") as f:
        f.write("id,audio_path,duration_seconds,text\n")
        for wav_path in sorted(wav_dir.glob("*.wav")):
            stem = wav_path.stem
            duration = sf.info(str(wav_path)).duration
            text = text_map.get(stem, "")
            f.write(f"{stem},{wav_path},{duration:.2f},{text}\n")
            print(f"  {stem}: {duration:.2f}s")

    print(f"metadata → {metadata_path}")


if __name__ == "__main__":
    main()
