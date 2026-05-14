"""MOS 评测结果分析：计算平均分、Bad Case 分布、输出图表"""
import argparse
import csv
import json
from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False
import pandas as pd
import yaml


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="MOS 结果分析")
    parser.add_argument("--config", default="configs/eval_config.yaml", help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    result_path = project_root / config.get("result_path", "evaluation/mos_results.csv")
    labels_path = project_root / config.get("badcase_labels", "evaluation/badcase_labels.json")
    output_dir = project_root / "outputs/evaluation_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not result_path.exists():
        print(f"评测结果文件不存在: {result_path}")
        return

    df = pd.read_csv(result_path)
    if df.empty:
        print("评测结果为空")
        return

    print(f"共 {len(df)} 条评测记录")

    # 平均 MOS
    avg_nat = df["mos_naturalness"].mean()
    avg_sim = df["mos_similarity"].mean()
    print(f"平均自然度 MOS: {avg_nat:.2f}")
    print(f"平均音色相似度 MOS: {avg_sim:.2f}")

    # Bad Case 统计
    all_labels = []
    for val in df["badcase_labels"].dropna():
        if val:
            for lb in str(val).split(","):
                lb = lb.strip()
                if lb:
                    all_labels.append(lb)
    label_counts = Counter(all_labels)

    # MOS 分布直方图
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].hist(df["mos_naturalness"].dropna(), bins=8, range=(1, 5),
                 color="steelblue", edgecolor="white")
    axes[0].set_xlabel("MOS")
    axes[0].set_ylabel("Count")
    axes[0].set_title(f"Naturalness MOS (avg={avg_nat:.2f})")

    axes[1].hist(df["mos_similarity"].dropna(), bins=8, range=(1, 5),
                 color="coral", edgecolor="white")
    axes[1].set_xlabel("MOS")
    axes[1].set_ylabel("Count")
    axes[1].set_title(f"Similarity MOS (avg={avg_sim:.2f})")

    # Bad Case 分布
    if label_counts:
        lbs, cnts = zip(*label_counts.most_common())
        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(lbs)))
        axes[2].barh(range(len(lbs)), cnts, color=colors, edgecolor="white")
        axes[2].set_yticks(range(len(lbs)))
        axes[2].set_yticklabels(lbs)
        axes[2].set_xlabel("Count")
        axes[2].set_title("Bad Case Distribution")
        axes[2].invert_yaxis()
    else:
        axes[2].text(0.5, 0.5, "无 Bad Case", transform=axes[2].transAxes,
                     ha="center", va="center")
        axes[2].set_title("Bad Case Distribution")

    plt.tight_layout()

    # 保存组合图
    combo_path = project_root / "docs" / "badcase_distribution.png"
    if combo_path.exists():
        combo_path.unlink()
    plt.savefig(combo_path, dpi=150)
    plt.close()
    print(f"Bad Case 分布图 → {combo_path}")

    # MOS 对比图（按模型分组）
    if "model_name" in df.columns and df["model_name"].nunique() > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        models = df.groupby("model_name").agg(
            nat_mean=("mos_naturalness", "mean"),
            sim_mean=("mos_similarity", "mean")
        )
        x = np.arange(len(models))
        w = 0.35
        ax.bar(x - w/2, models["nat_mean"], w, label="Naturalness", color="steelblue")
        ax.bar(x + w/2, models["sim_mean"], w, label="Similarity", color="coral")
        ax.set_xticks(x)
        ax.set_xticklabels(models.index)
        ax.set_ylabel("MOS")
        ax.set_title("Model MOS Comparison")
        ax.legend()
        ax.set_ylim(0, 5.5)
        plt.tight_layout()
        cmp_path = output_dir / "model_mos_comparison.png"
        plt.savefig(cmp_path, dpi=150)
        plt.close()
        print(f"MOS 对比图 → {cmp_path}")

    # 低分样本
    low_score = df[(df["mos_naturalness"] <= 2.5) | (df["mos_similarity"] <= 2.5)]
    if len(low_score) > 0:
        low_path = output_dir / "low_score_samples.csv"
        low_score.to_csv(low_path, index=False)
        print(f"低分样本 ({len(low_score)} 条) → {low_path}")

    print("分析完成")


if __name__ == "__main__":
    main()
