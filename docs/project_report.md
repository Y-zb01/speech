# 语音算法工具箱 — 项目报告

## 项目背景

面向语音算法实习生岗位的综合型项目，采用 Mac 主控端 + Windows 高性能主机（WSL2 Ubuntu）双机协同的开发方式，完成语音数据处理、VAD 前处理、TTS 推理和 MOS 主观评测的一条龙链路。

## 双机分工

| 端 | 角色 | 职责 |
|---|---|---|
| Mac | 主控端 | 代码开发、小样本测试、MOS 评测、报告整理 |
| Windows (WSL2) | 训练端 | Edge-TTS 推理、批量音频处理 |

## 技术栈

- **语言/环境**：Python 3.10, Conda
- **音频处理**：librosa, soundfile, noisereduce
- **VAD**：能量阈值 + 中值滤波平滑
- **可视化**：matplotlib（PingFang SC 中文字体）
- **TTS 推理**：Microsoft Edge-TTS（2 个中文音色）
- **评测页面**：Gradio 6.x
- **数据源**：LibriSpeech dev-clean（10 条，4 位不同说话人）

## 项目流程

```
音频数据 → 格式转换(24kHz/mono) → 文本清洗 → 时长统计 → Mel 特征提取
    ↓
长音频 → VAD 检测 → 切分片段 → 降噪
    ↓
测试文本 → TTS 推理 → 合成语音（Xiaoxiao + Yunxi）
    ↓
MOS 听音评测 → Bad Case 标注 → 分析报告
```

## 功能模块

### 模块一：语音数据处理与 Mel 特征提取

- 音频格式统一（mp3/m4a/flac → wav 24000Hz mono PCM16）
- 文本清洗（标点规范化、多余空白去除）
- 时长统计与分布图
- Mel 频谱特征提取（n_mels=80, n_fft=1024, hop_length=256），保存为 .npy
- metadata.csv 生成

### 模块二：VAD 语音活动检测

- 基于能量的 VAD 检测算法
- 中值滤波去噪 + 相邻段合并
- 时长过滤（1.0s - 15.0s）
- my_long_audio.wav（160s）→ 50 个语音段
- 结果可视化 + 降噪后处理

### 模块三：TTS 推理

- Edge-TTS 双音色：XiaoxiaoNeural（女声）+ YunxiNeural（男声）
- 10 句测试文本 × 2 音色 = 20 条合成语音
- 推理日志记录（文本、音色、耗时）

### 模块四：MOS 评测与 Bad Case 分析

- Gradio 听音评测页面
- 自然度/音色相似度双维度打分（1-5，0.5 步进）
- Bad Case 多标签标注（破音、漏读、机械感等 8 类）
- 结果分析：平均 MOS、分布直方图、Bad Case 统计

## 评测结果

**评测样本：** 20 条（Xiaoxiao × 10 + Yunxi × 10）

| 指标 | 值 |
|---|---|
| 评测记录数 | 25 |
| 平均自然度 MOS | 5.00 |
| 平均音色相似度 MOS | 5.00 |
| Bad Case | 1 条（机械感/不自然） |

### 音色对比

| 音色 | 平均自然度 | 平均相似度 |
|---|---|---|
| XiaoxiaoNeural（女声） | 5.00 | 5.00 |
| YunxiNeural（男声） | 5.00 | 5.00 |

## 项目产出

- 数据处理脚本 5 个（YAML 配置驱动）：`scripts/01-05_*.py`
- VAD 切分脚本 + 降噪脚本：`scripts/06_vad_segment.py`、`scripts/07_denoise.py`
- TTS 推理脚本：`tts_demo/tts_infer.py`
- MOS 评测 Gradio 页面：`evaluation/mos_app.py`
- 结果分析脚本：`evaluation/analyze_mos.py`
- 可视化图表 4 张：Mel 频谱、时长分布、VAD 检测、Bad Case 分布
- 完整项目文档：`docs/` 目录

## 关键技术细节

### VAD 算法
- 能量计算：帧长 25ms，帧移 12.5ms
- 自适应阈值：`mean(energy) × 0.3 + median(energy) × 0.35`
- 中值滤波窗口：3 帧
- 段合并间隔：< 0.3s 的静音段合并

### Mel 特征参数
- 采样率：24000Hz
- FFT 点数：1024
- 跳步：256
- Mel 通道数：80
- 频率范围：0-12000Hz

### MOS 评测设计
- 双维度：自然度（独立听感）+ 音色相似度（与参考对比）
- 8 类 Bad Case 标签覆盖常见 TTS 缺陷
- 结果自动持久化为 CSV，支持断点续评

## 改进方向

1. 在 Windows 端接入 GPT-SoVITS/CosyVoice 实现零样本语音克隆
2. 扩展 Bad Case 分析维度（语速分析、频谱对比）
3. 评测端支持 AB 盲测模式
4. 接入更大规模数据集（LibriSpeech 全量、AISHELL-3 中文）
