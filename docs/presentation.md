# 语音算法工具箱 — 全面展示文档

## 项目概述

本项目从**原始音频数据 → Mel 特征提取 → VAD 切分 → TTS 合成 → MOS 主观评测**，完整跑通了语音算法工具箱的全链路。采用 **Mac 主控端 + Windows (WSL2) 训练端** 双机协同的开发方式，覆盖音频预处理、语音活动检测、文本转语音推理、主观评测四个核心模块。

**GitHub 仓库：** <https://github.com/Y-zb01/speech>

---

## 完整数据流全景

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          阶段一：音频预处理（Mac）                          │
│                                                                          │
│  data/samples/raw_audio/*.flac  ──┐                                      │
│  (10条 LibriSpeech 原始音频)       │                                      │
│                                   ▼                                      │
│  data/samples/transcript.txt ──→ 01_convert_audio ──→ outputs/processed_dataset/wavs/*.wav
│  (转录文本)                          │                   (24000Hz mono PCM16)       │
│                                      │                                                │
│                                      ├──→ 02_clean_text ──→ transcript_clean.txt      │
│                                      │    (文本清洗)                                   │
│                                      │                                                │
│                                      ├──→ 03_duration_stat ──→ duration_report.csv    │
│                                      │    (时长统计)              duration_distribution.png
│                                      │                                                │
│                                      ├──→ 04_extract_mel ──→ mels/*.npy              │
│                                      │    (Mel特征提取)          mel_example.png       │
│                                      │                                                │
│                                      └──→ 05_generate_metadata ──→ metadata.csv       │
│                                           (元数据生成)                                  │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       阶段二：VAD 语音活动检测（Mac）                        │
│                                                                          │
│  data/raw_long_audio/my_long_audio.wav  ──→ 06_vad_segment ──→ segments/*.wav (50段)
│  (用户160秒长音频)                             (能量检测+切分)      vad_result.csv
│                                                           vad_result.png│
│                                    │                                     │
│                                    ▼                                     │
│                            segments/*.wav  ──→ 07_denoise ──→ denoised/*.wav (50段)
│                                                (频谱减法降噪)             │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       阶段三：TTS 推理（Windows WSL2）                      │
│                                                                          │
│  tts_demo/test_sentences.txt  ──→ tts_infer.py ──→ outputs/generated_audio/
│  (10句中文测试文本)                 (Edge-TTS)         ├── edge_Xiaoxiao_001~010.wav
│                                                       └── edge_Yunxi_011~020.wav
│  音色: zh-CN-XiaoxiaoNeural (女声)                     inference_log.csv
│        zh-CN-YunxiNeural (男声)                                        │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       阶段四：MOS 主观评测（Mac）                           │
│                                                                          │
│  data/eval_data/eval_metadata.csv  ──→ mos_app.py ──→ mos_results.csv   │
│  outputs/generated_audio/*.wav         (Gradio页面)                      │
│                                                          │               │
│                                                          ▼               │
│                                                   analyze_mos.py ──→    │
│                                                    badcase_distribution.png
│                                                    low_score_samples.csv │
└──────────────────────────────────────────────────────────────────────────┘
```

### 各阶段输入输出对应表

| 阶段 | 执行脚本 | 输入 → 输出 |
|---|---|---|
| 1.1 格式转换 | `scripts/01_convert_audio.py` | `data/samples/raw_audio/*.flac` → `outputs/processed_dataset/wavs/*.wav` |
| 1.2 文本清洗 | `scripts/02_clean_text.py` | `data/samples/transcript.txt` → `outputs/processed_dataset/transcript_clean.txt` |
| 1.3 时长统计 | `scripts/03_duration_stat.py` | `outputs/processed_dataset/wavs/` → `duration_report.csv` + `duration_distribution.png` |
| 1.4 Mel 提取 | `scripts/04_extract_mel.py` | `outputs/processed_dataset/wavs/` → `outputs/processed_dataset/mels/*.npy` + `mel_example.png` |
| 1.5 元数据 | `scripts/05_generate_metadata.py` | wavs + transcript → `outputs/processed_dataset/metadata.csv` |
| 2.1 VAD 切分 | `scripts/06_vad_segment.py` | `data/raw_long_audio/my_long_audio.wav` → `segments/*.wav`（50段）+ `vad_result.csv` |
| 2.2 降噪 | `scripts/07_denoise.py` | `segments/*.wav` → `denoised/*.wav`（50段） |
| 3.1 TTS 推理 | `tts_demo/tts_infer.py` | 测试文本 → `outputs/generated_audio/*.wav`（20条） |
| 4.1 MOS 评测 | `evaluation/mos_app.py` | 合成音频 → `evaluation/mos_results.csv` |
| 4.2 结果分析 | `evaluation/analyze_mos.py` | `mos_results.csv` → `badcase_distribution.png` + 低分样本 |

### 一键运行完整流程

```bash
# 激活环境
conda activate speech_mac

# ===== 阶段一：音频预处理 =====
python scripts/01_convert_audio.py --config configs/preprocess.yaml
python scripts/02_clean_text.py --config configs/preprocess.yaml
python scripts/03_duration_stat.py --config configs/preprocess.yaml
python scripts/04_extract_mel.py --config configs/mel_config.yaml
python scripts/05_generate_metadata.py --config configs/preprocess.yaml

# ===== 阶段二：VAD + 降噪 =====
python scripts/06_vad_segment.py --config configs/vad_config.yaml
python scripts/07_denoise.py \
    --input_dir outputs/preprocess_output/segments \
    --output_dir outputs/preprocess_output/denoised

# ===== 阶段三：TTS 推理（需 Windows 端或本机有 edge-tts） =====
python tts_demo/tts_infer.py

# ===== 阶段四：MOS 评测 =====
python evaluation/mos_app.py --config configs/eval_config.yaml
# 浏览器打开 http://localhost:7860 完成评测后：
python evaluation/analyze_mos.py --config configs/eval_config.yaml
```

---

## 项目结构速览

```
speech_intern_toolkit/
├── configs/                # 4 个 YAML 配置文件
│   ├── preprocess.yaml     — 音频预处理参数
│   ├── mel_config.yaml     — Mel 频谱提取参数
│   ├── vad_config.yaml     — VAD 检测参数
│   └── eval_config.yaml    — MOS 评测配置
│
├── scripts/                # 7 个处理脚本
│   ├── 01_convert_audio.py     — 音频格式转换
│   ├── 02_clean_text.py        — 文本清洗
│   ├── 03_duration_stat.py     — 时长统计与分布图
│   ├── 04_extract_mel.py       — Mel 特征提取
│   ├── 05_generate_metadata.py — 元数据生成
│   ├── 06_vad_segment.py       — VAD 切分
│   └── 07_denoise.py           — 降噪处理
│
├── evaluation/             # MOS 评测模块
│   ├── mos_app.py              — Gradio 评测页面
│   ├── analyze_mos.py          — 结果分析脚本
│   ├── badcase_labels.json     — 8 类 Bad Case 标签
│   └── mos_results.csv         — 评测结果（25 条记录）
│
├── tts_demo/               # TTS 推理模块
│   ├── tts_infer.py            — Edge-TTS 批量推理
│   ├── inference_log.csv       — 推理日志
│   ├── ref_audio/              — 参考音频（5 条真人录音）
│   │   ├── ref_01.wav ~ ref_05.wav
│   ├── ref_sentences.txt       — 参考音频对应文本
│   └── test_sentences.txt      — TTS 测试文本（15 句）
│
├── data/                   # 数据目录
│   ├── samples/raw_audio/      — LibriSpeech 原始 flac（10 条）
│   ├── samples/transcript.txt  — LibriSpeech 转录文本
│   ├── raw_long_audio/         — 用户长音频
│   │   ├── my_long_audio.wav   — 160s 录音
│   │   └── reading_passage.txt — 朗读文本
│   └── eval_data/              — 评测元数据
│       └── eval_metadata.csv   — 20 条合成语音索引
│
├── outputs/                # 产出目录
│   ├── processed_dataset/      — 预处理结果
│   │   ├── wavs/               — 10 条标准 wav
│   │   ├── mels/               — 10 张 Mel 频谱 .npy
│   │   ├── metadata.csv        — 数据集元数据
│   │   └── duration_report.csv — 时长报告
│   ├── preprocess_output/      — VAD + 降噪结果
│   │   ├── segments/           — 50 个语音片段
│   │   ├── denoised/           — 50 个降噪片段
│   │   └── vad_result.csv      — VAD 检测明细
│   ├── generated_audio/        — 20 条 Edge-TTS 合成语音
│   └── evaluation_output/      — MOS 分析结果
│
└── docs/                   # 文档与图表
    ├── presentation.md         — 本文档
    ├── project_report.md       — 项目报告
    ├── test_plan.md            — 测试计划（24 项）
    ├── environment_setup.md    — 双机环境搭建指南
    ├── win端操作指南.md         — Windows 端操作指南
    ├── duration_distribution.png — 时长分布图
    ├── mel_example.png         — Mel 频谱示例
    ├── vad_result.png          — VAD 切分可视化
    └── badcase_distribution.png — Bad Case 分布图
```

---

## 模块一：音频数据处理

### 功能说明

将原始音频（mp3/m4a/flac）统一转换为 **24000Hz 单声道 PCM16 WAV**，清洗对应文本，统计时长分布，提取 Mel 频谱特征。

### 数据来源

从 LibriSpeech dev-clean 数据集中选取 **10 条音频**，覆盖 **4 位不同说话人**，时长范围 **4.5s ~ 8.4s**。

| 文件 | 说话人 | 时长 | 文本 |
|---|---|---|---|
| 174_14.wav | 174 | 4.83s | COSETTE WAS NO LONGER IN RAGS SHE WAS IN MOURNING |
| 1919_45.wav | 1919 | 6.11s | IF IT SHOULD BE IN AN UNSOUND STATE... |
| 2086_23.wav | 2086 | 7.37s | MOST OF MY LIKENESSES DO LOOK UNAMIABLE... |
| 2277_18.wav | 2277 | 4.54s | HIS FIRST IMPULSE WAS TO WRITE BUT FOUR WORDS... |
| 2412_13.wav | 2412 | 8.42s | THE FIRST EDITION OF EREWHON SOLD IN ABOUT THREE WEEKS... |
| 5338_10.wav | 5338 | 6.62s | HER COMPLEXION WAS NOT A DECIDED PINK... |
| 5536_2.wav | 5536 | 7.02s | THE MEN BLACKEN THEIR FACES AND WIDOWS... |
| 6313_8.wav | 6313 | 4.49s | MASTER TAD IS RIGHT DECIDED THE GUIDE... |
| 6345_23.wav | 6345 | 5.53s | I DIDN'T THINK A DECENT MAN COULD DO SUCH THINGS... |
| 7976_5.wav | 7976 | 5.56s | NO BATTERY IN THE WHOLE FOUR YEARS WAR... |

### 运行命令

```bash
# 逐一执行
python scripts/01_convert_audio.py --config configs/preprocess.yaml
python scripts/02_clean_text.py --config configs/preprocess.yaml
python scripts/03_duration_stat.py --config configs/preprocess.yaml
python scripts/04_extract_mel.py --config configs/mel_config.yaml
python scripts/05_generate_metadata.py --config configs/preprocess.yaml
```

### 输入文件

| 文件 | 路径 |
|---|---|
| 原始音频 | `data/samples/raw_audio/*.flac` |
| 转录文本 | `data/samples/transcript.txt` |
| 预处理配置 | `configs/preprocess.yaml` |
| Mel 配置 | `configs/mel_config.yaml` |

### 产出文件

| 文件 | 路径 |
|---|---|
| 标准化 wav | `outputs/processed_dataset/wavs/*.wav` |
| Mel 频谱 | `outputs/processed_dataset/mels/*.npy` |
| 数据集元数据 | `outputs/processed_dataset/metadata.csv` |
| 时长报告 | `outputs/processed_dataset/duration_report.csv` |
| 清洗后文本 | `outputs/processed_dataset/transcript_clean.txt` |
| 时长分布图 | `docs/duration_distribution.png` |
| Mel 示例图 | `docs/mel_example.png` |

### Mel 频谱参数

| 参数 | 值 |
|---|---|
| 采样率 | 24000 Hz |
| FFT 点数 | 1024 |
| 帧移 | 256 |
| Mel 通道数 | 80 |
| 频率范围 | 0 ~ 12000 Hz |

---

## 模块二：VAD 语音活动检测与降噪

### 功能说明

对长音频进行**基于能量的语音活动检测**，自动识别有声段起止时间，切分为独立短音频，并进行频谱减法降噪。

### 算法设计

1. **能量计算** — 帧长 25ms，帧移 12.5ms，逐帧计算 RMS 能量
2. **自适应阈值** — `mean(energy) × 0.3 + median(energy) × 0.35`，兼顾不同信噪比
3. **中值滤波** — 窗口 3 帧，消除孤立误检
4. **段合并** — 间隔 < 0.3s 的相邻语音段自动合并
5. **时长过滤** — 保留 1.0s ~ 15.0s 的片段，过长自动截断
6. **降噪处理** — noisereduce 频谱减法，保留 85% 语音能量

### 输入文件

| 文件 | 路径 |
|---|---|
| 长音频 | `data/raw_long_audio/my_long_audio.wav`（160 秒） |
| VAD 配置 | `configs/vad_config.yaml` |

### 产出文件

| 文件 | 路径 |
|---|---|
| 语音片段（原始） | `outputs/preprocess_output/segments/my_long_audio_seg_*.wav`（50 段） |
| 语音片段（降噪） | `outputs/preprocess_output/denoised/my_long_audio_seg_*.wav`（50 段） |
| VAD 检测明细 | `outputs/preprocess_output/vad_result.csv` |
| 切分可视化 | `docs/vad_result.png` |

### 切分结果（前 15 段）

| 片段 | 起始 | 结束 | 时长 |
|---|---|---|---|
| my_long_audio_seg_000.wav | 3.98s | 7.16s | 3.19s |
| my_long_audio_seg_001.wav | 8.09s | 10.24s | 2.15s |
| my_long_audio_seg_002.wav | 11.19s | 12.40s | 1.21s |
| my_long_audio_seg_003.wav | 12.96s | 14.29s | 1.32s |
| my_long_audio_seg_004.wav | 15.44s | 18.38s | 2.94s |
| my_long_audio_seg_005.wav | 19.28s | 20.75s | 1.48s |
| my_long_audio_seg_006.wav | 21.34s | 23.01s | 1.68s |
| my_long_audio_seg_007.wav | 23.33s | 25.88s | 2.55s |
| my_long_audio_seg_008.wav | 27.54s | 28.93s | 1.39s |
| my_long_audio_seg_009.wav | 29.50s | 30.89s | 1.39s |
| my_long_audio_seg_010.wav | 31.56s | 33.98s | 2.41s |
| my_long_audio_seg_011.wav | 34.63s | 36.10s | 1.48s |
| my_long_audio_seg_012.wav | 38.08s | 39.49s | 1.41s |
| my_long_audio_seg_013.wav | 41.26s | 42.34s | 1.07s |
| my_long_audio_seg_014.wav | 43.24s | 46.35s | 3.11s |

### 运行命令

```bash
# VAD 切分
python scripts/06_vad_segment.py --config configs/vad_config.yaml

# 降噪
python scripts/07_denoise.py \
    --input_dir outputs/preprocess_output/segments \
    --output_dir outputs/preprocess_output/denoised
```

---

## 模块三：TTS 文本转语音推理

### 功能说明

使用 Microsoft Edge-TTS 云端服务，将中文文本合成为自然语音。支持多音色，无需 GPU。

### 音色配置

| 音色 | 性别 | 样本数 | 示例路径 |
|---|---|---|---|
| zh-CN-XiaoxiaoNeural | 女声 | 10 条 | `outputs/generated_audio/edge_Xiaoxiao_001.wav` |
| zh-CN-YunxiNeural | 男声 | 10 条 | `outputs/generated_audio/edge_Yunxi_011.wav` |

### 测试文本

| 编号 | 文本 |
|---|---|
| 001 | 今天下午我去了趟图书馆，借了两本关于人工智能的书。 |
| 002 | 回来的时候路过咖啡店，点了杯拿铁，味道还挺不错的。 |
| 003 | 最近天气开始热起来了，街上的人都换上了短袖。 |
| 004 | 我觉得这个项目挺有意思的，如果能顺利跑通就太好了。 |
| 005 | 语音合成技术这几年进步很快，效果越来越自然了。 |
| 006 | 明天打算去公园跑步，顺便拍几张照片。 |
| 007 | 这本书讲的是深度学习在自然语言处理中的应用。 |
| 008 | 我喜欢在下雨天待在家里听音乐，感觉很放松。 |
| 009 | 周末约了朋友一起吃饭，好久没见了。 |
| 010 | 这道数学题有点难，需要花时间仔细想想。 |

> 完整测试文本见 `tts_demo/test_sentences.txt`

### 运行命令

```bash
python tts_demo/tts_infer.py
```

### 输入文件

| 文件 | 路径 |
|---|---|
| 推理脚本 | `tts_demo/tts_infer.py` |
| 测试文本 | `tts_demo/test_sentences.txt`（15 句中文） |
| 参考文本 | `tts_demo/ref_sentences.txt`（5 句长句） |
| 参考音频 | `tts_demo/ref_audio/ref_01.wav` ~ `ref_05.wav` |

### 产出文件

| 文件 | 路径 |
|---|---|
| 合成语音 | `outputs/generated_audio/edge_*.wav`（20 条） |
| 推理日志 | `tts_demo/inference_log.csv` |

---

## 模块四：MOS 主观听音评测

### 功能说明

基于 Gradio 构建的可视化听音评测页面，支持**双维度 MOS 评分**和 **8 类 Bad Case 标注**，结果自动持久化为 CSV。

### 评测页面

- **访问地址：** `http://localhost:7860`（本机）或 `http://<内网IP>:7860`（局域网）
- **页面路径：** `evaluation/mos_app.py`
- **截图：** 见下方启动命令

### 评分维度

| 维度 | 范围 | 步进 | 说明 |
|---|---|---|---|
| 自然度 MOS | 1 ~ 5 | 0.5 | 语音听感是否自然，有无机械感 |
| 音色相似度 MOS | 1 ~ 5 | 0.5 | 合成音色是否稳定一致 |

### Bad Case 标签（8 类）

`evaluation/badcase_labels.json`

| 标签 | 说明 |
|---|---|
| 破音/爆音 | 出现爆破、削波等失真 |
| 漏读 | 合成语音遗漏部分文字 |
| 错读/多读 | 多音字错误或多余内容 |
| 音色漂移 | 同一句中音色明显变化 |
| 机械感/不自然 | 韵律平淡、听感机械 |
| 语速异常 | 语速过快或过慢 |
| 停顿不当 | 句中断句位置错误 |
| 无问题 | 听感正常 |

### 评测结果

`evaluation/mos_results.csv`

| 指标 | 值 |
|---|---|
| 评测记录数 | 25 条 |
| 平均自然度 MOS | 5.00 |
| 平均音色相似度 MOS | 5.00 |
| Bad Case 数量 | 1 条（机械感/不自然） |

### 按音色分

| 音色 | 自然度均分 | 相似度均分 |
|---|---|---|
| XiaoxiaoNeural（女声） | 5.00 | 5.00 |
| YunxiNeural（男声） | 5.00 | 5.00 |

### 运行命令

```bash
# 启动评测页面
python evaluation/mos_app.py --config configs/eval_config.yaml

# 分析评测结果
python evaluation/analyze_mos.py --config configs/eval_config.yaml
```

### 输入文件

| 文件 | 路径 |
|---|---|
| 评测配置 | `configs/eval_config.yaml` |
| 评测元数据 | `data/eval_data/eval_metadata.csv` |
| Bad Case 标签 | `evaluation/badcase_labels.json` |
| 合成音频 | `outputs/generated_audio/edge_*.wav`（20 条） |

### 产出文件

| 文件 | 路径 |
|---|---|
| 评测结果 | `evaluation/mos_results.csv` |
| Bad Case 分布图 | `docs/badcase_distribution.png` |
| 低分样本 | `outputs/evaluation_output/low_score_samples.csv` |

---

## 可视化图表一览

| 图表 | 路径 | 说明 |
|---|---|---|
| 时长分布 | `docs/duration_distribution.png` | 10 条 LibriSpeech 时长直方图 |
| Mel 频谱示例 | `docs/mel_example.png` | 80 维 Mel 特征热力图 |
| VAD 切分 | `docs/vad_result.png` | 160s 波形 + 50 段语音高亮（绿色） |
| Bad Case 分布 | `docs/badcase_distribution.png` | MOS 评分分布直方图 + 问题标签统计 |

---

## 双机协同架构

```
┌─ Mac（主控/评测）─────┐     ┌─ Windows WSL2（训练/推理）─┐
│                        │     │                            │
│  • 代码开发 / Git      │←───→│  • GPU 批量处理              │
│  • 小样本数据测试       │ Git │  • VAD 切分                  │
│  • Mel 特征提取         │     │  • Edge-TTS 推理            │
│  • MOS 主观评测         │     │                            │
│  • 报告整理             │     │                            │
└────────────────────────┘     └────────────────────────────┘
```

---

## 展示路线建议

1. **开场** — 项目背景：双机协同 + 四个阶段全链路
2. **数据处理** — 展示时长分布图、Mel 频谱图、metadata.csv
3. **VAD 演示** — 展示 VAD 结果图，说明能量检测算法原理
4. **TTS 推理** — 播放几条合成音频（Xiaoxiao + Yunxi 对比）
5. **MOS 评测** — 打开 `http://localhost:7860` 现场演示评测流程
6. **结果分析** — 展示 Bad Case 分布图、MOS 得分汇总

---

## 环境信息

| 项目 | 版本/路径 |
|---|---|
| Python | 3.10 (conda: `speech_mac`) |
| 关键依赖 | librosa, soundfile, gradio 6.x, noisereduce, edge-tts |
| 依赖清单 | `requirements-mac.txt` |
| WSL 依赖 | `requirements-wsl.txt` |

```bash
# Mac 端激活环境
conda activate speech_mac

# 安装依赖
pip install -r requirements-mac.txt
```
