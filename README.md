# speech_intern_toolkit

语音算法实习生项目工具箱 —— 基于 Mac 主控端 + Windows GPU 训练端的双机协同方案。

## 功能模块

- **模块一**：语音数据处理与 Mel 特征提取
- **模块二**：VAD 语音活动检测与长音频切分
- **模块三**：TTS 合成语音 MOS 评测与 Bad Case 标注
- **可选模块四**：GPT-SoVITS / CosyVoice 推理或微调

## 快速开始

### Mac 端

```bash
conda activate speech_mac
python scripts/01_convert_audio.py --config configs/preprocess.yaml
python scripts/02_clean_text.py --config configs/preprocess.yaml
python scripts/03_duration_stat.py --config configs/preprocess.yaml
python scripts/04_extract_mel.py --config configs/mel_config.yaml
python scripts/05_generate_metadata.py --config configs/preprocess.yaml
```

### Windows WSL2 端

```bash
conda activate speech_train
python scripts/01_convert_audio.py --config configs/preprocess.yaml
python scripts/06_vad_segment.py --config configs/vad_config.yaml
```

## 目录结构

```
speech_intern_toolkit/
├── configs/         # YAML 配置文件
├── data/            # 音频数据（不提交 Git）
├── scripts/         # 数据处理脚本
├── tts_demo/        # TTS 模型推理
├── evaluation/      # MOS 评测工具
├── outputs/         # 脚本输出
└── docs/            # 项目文档
```

## 环境配置

详见 [docs/environment_setup.md](docs/environment_setup.md)
