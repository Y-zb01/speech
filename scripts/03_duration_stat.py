"""时长统计：统计每条音频时长，输出报告和分布图"""
import argparse
import yaml
from pathlib import Path
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="时长统计")
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    wav_dir = project_root / config["output_dir"] / "wavs"
    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    durations = []
    for wav_path in sorted(wav_dir.glob("*.wav")):
        info = sf.info(str(wav_path))
        d = info.duration
        durations.append((wav_path.name, d))
        print(f"  {wav_path.name}: {d:.2f}s")

    # 保存 CSV
    csv_path = output_dir / "duration_report.csv"
    with open(csv_path, "w") as f:
        f.write("file,duration_seconds\n")
        for name, d in durations:
            f.write(f"{name},{d:.2f}\n")
    print(f"时长报告 → {csv_path}")

    # 绘制分布图
    durs = [d for _, d in durations]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].bar(range(len(durs)), durs, color="steelblue")
    axes[0].set_xlabel("Sample index")
    axes[0].set_ylabel("Duration (s)")
    axes[0].set_title("Audio Duration per Sample")

    axes[1].hist(durs, bins=max(5, len(durs)), color="coral", edgecolor="white")
    axes[1].set_xlabel("Duration (s)")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Duration Distribution")

    plt.tight_layout()
    chart_path = project_root / "docs" / "duration_distribution.png"
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"分布图 → {chart_path}")

    if durs:
        print(f"统计: 共 {len(durs)} 条, 最短 {min(durs):.2f}s, 最长 {max(durs):.2f}s, 平均 {np.mean(durs):.2f}s")


if __name__ == "__main__":
    main()
