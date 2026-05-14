"""文本清洗：读取 transcript.txt，规范化文本内容"""
import argparse
import yaml
import re
from pathlib import Path


def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace(""", "\"").replace(""", "\"")
    return text


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="文本清洗")
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    transcript_path = project_root / config["transcript_path"]
    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "transcript_clean.txt"
    cleaned = 0

    with open(transcript_path, "r") as fin, open(output_path, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                name, text = parts[0].strip(), clean_text(parts[1])
                fout.write(f"{name}|{text}\n")
                cleaned += 1
            else:
                fout.write(f"{line}\n")
                cleaned += 1

    print(f"文本清洗完成，共 {cleaned} 条 → {output_path}")


if __name__ == "__main__":
    main()
