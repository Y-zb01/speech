"""MOS 主观听音评测页面 —— Gradio 实现"""
import argparse
import json
import csv
import os
from pathlib import Path

import gradio as gr
import yaml


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def build_app(metadata_path, result_path, labels_path):
    metadata_path = Path(metadata_path)
    result_path = Path(result_path)

    # 加载 Bad Case 标签
    with open(labels_path, "r") as f:
        label_data = json.load(f)
    label_choices = label_data["labels"]

    # 加载音频列表
    samples = []
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                samples.append({
                    "id": row.get("id", row.get("sample_id", "")),
                    "ref_audio": row.get("ref_audio", row.get("reference_audio", "")),
                    "syn_audio": row.get("syn_audio", row.get("generated_audio", "")),
                    "text": row.get("text", ""),
                    "model": row.get("model_name", ""),
                })
    else:
        csv_header = ["id", "ref_audio", "syn_audio", "text", "model_name"]

        # 如果 metadata 不存在，扫描 data/eval_data/ 目录自动生成
        eval_dir = Path("data/eval_data")
        if eval_dir.exists():
            syn_files = sorted(eval_dir.glob("*.wav"))
            for f in syn_files:
                samples.append({
                    "id": f.stem,
                    "ref_audio": "",
                    "syn_audio": str(f),
                    "text": "",
                    "model": "",
                })

    if not samples:
        print("没有找到评测音频，请将合成语音放入 data/eval_data/")
        return

    total = len(samples)
    current_idx = [0]

    def load_sample(idx):
        if 0 <= idx < total:
            s = samples[idx]
            info = f"**{idx+1}/{total}**  |  ID: {s['id']}  |  模型: {s.get('model','')}  |  文本: {s.get('text','')}"
            ref = s["ref_audio"] if s["ref_audio"] and Path(s["ref_audio"]).exists() else None
            syn = s["syn_audio"] if Path(s["syn_audio"]).exists() else None
            return info, ref, syn
        return "加载中...", None, None

    def save_result(sample_id, mos_nat, mos_sim, badcase_str, note):
        result_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = result_path.exists()
        with open(result_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["id", "mos_naturalness", "mos_similarity", "badcase_labels", "note"])
            writer.writerow([sample_id, mos_nat, mos_sim, badcase_str, note])

    def on_submit(mos_nat, mos_sim, badcase_list, note):
        idx = current_idx[0]
        if idx >= total:
            return "已完成全部评测", None, None, "", 5, 5
        s = samples[idx]
        bc_str = ",".join(badcase_list) if badcase_list else ""
        save_result(s["id"], mos_nat, mos_sim, bc_str, note)
        current_idx[0] += 1
        if current_idx[0] >= total:
            return "全部评测完成！", None, None, "全部评测完成！", 5, 5
        info, ref, syn = load_sample(current_idx[0])
        return info, ref, syn, info, 5, 5

    def on_skip():
        current_idx[0] += 1
        if current_idx[0] >= total:
            return "已跳过全部", None, None, "已跳过全部", 5, 5
        info, ref, syn = load_sample(current_idx[0])
        return info, ref, syn, info, 5, 5

    init_info, init_ref, init_syn = load_sample(0)

    with gr.Blocks(title="MOS 听音评测") as demo:
        gr.Markdown("# MOS 主观听音评测")
        info_md = gr.Markdown(init_info)

        with gr.Row():
            ref_audio = gr.Audio(init_ref, label="参考音频", type="filepath")
            syn_audio = gr.Audio(init_syn, label="合成音频", type="filepath")

        gr.Markdown("### 评分")
        with gr.Row():
            mos_nat = gr.Slider(1, 5, value=5, step=0.5, label="自然度 MOS", scale=1)
            mos_sim = gr.Slider(1, 5, value=5, step=0.5, label="音色相似度 MOS", scale=1)

        gr.Markdown("### 问题标注")
        badcase = gr.CheckboxGroup(choices=label_choices, label="Bad Case 标签")
        note = gr.Textbox(label="备注", placeholder="补充问题描述...")

        with gr.Row():
            submit_btn = gr.Button("提交并下一题", variant="primary")
            skip_btn = gr.Button("跳过")

        status = gr.Textbox(label="状态", value=f"共 {total} 条待评测", interactive=False)

        submit_btn.click(
            fn=on_submit, inputs=[mos_nat, mos_sim, badcase, note],
            outputs=[status, ref_audio, syn_audio, info_md, mos_nat, mos_sim]
        )
        skip_btn.click(
            fn=on_skip, inputs=[],
            outputs=[status, ref_audio, syn_audio, info_md, mos_nat, mos_sim]
        )

    return demo


def main():
    parser = argparse.ArgumentParser(description="MOS 听音评测页面")
    parser.add_argument("--config", default="configs/eval_config.yaml", help="YAML 配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = Path(__file__).resolve().parents[1]
    metadata_path = project_root / config.get("eval_metadata", "data/eval_data/eval_metadata.csv")
    result_path = project_root / config.get("result_path", "evaluation/mos_results.csv")
    labels_path = project_root / config.get("badcase_labels", "evaluation/badcase_labels.json")

    demo = build_app(metadata_path, result_path, labels_path)
    if demo is None:
        return

    server = config.get("server_name", "0.0.0.0")
    port = config.get("server_port", 7860)
    demo.launch(server_name=server, server_port=port)


if __name__ == "__main__":
    main()
