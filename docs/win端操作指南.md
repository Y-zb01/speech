# Windows 端操作指南

> 你需要**依次**完成下面每个步骤，把每步的**输出文件**传回给我，我再继续下一步。

---

## 步骤一：环境搭建

### 1.1 安装 WSL2

在 Windows PowerShell（管理员）中：

```bash
wsl --install
```

重启电脑，进入 Ubuntu。

### 1.2 配置 Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl build-essential ffmpeg sox libsndfile1
```

### 1.3 安装 Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

关闭终端重开。

### 1.4 创建环境

```bash
conda create -n speech_train python=3.10 -y
conda activate speech_train
pip install torch torchaudio librosa soundfile numpy pandas matplotlib scipy gradio pydub noisereduce pyyaml
```

### 1.5 验证 GPU

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### 输出文件

| 文件 | 内容 |
|------|------|
| `docs/win_gpu_check.txt` | 把上面命令的输出保存进去：`python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))" > docs/win_gpu_check.txt` |

---

## 步骤二：拉取代码 + 放置数据

### 2.1 克隆仓库

```bash
git clone https://github.com/Y-zb01/speech.git
cd speech
```

**不要放在 `/mnt/c/` 下**，放在 `/home/你的用户名/speech`。

### 2.2 放置数据

把你准备好的音频文件放入对应目录：

| 目录 | 放什么 | 要求 |
|------|--------|------|
| `data/train_audio/` | 短音频文件 | wav/flac/mp3 均可，时长 1-15s |
| `data/raw_long_audio/` | 长音频文件 | 连续说话几分钟以上，VAD 切分用 |

### 2.3 修改配置

编辑 `configs/preprocess.yaml`，把 `data_dir` 改为 `data/train_audio`：

```yaml
data_dir: data/train_audio
transcript_path: data/samples/transcript.txt
```

> 如果你没有 `transcript.txt`，新建一个放在 `data/train_audio/transcript.txt`，格式为每行 `文件名|文本内容`。

### 输出文件

| 文件 | 内容 |
|------|------|
| `docs/win_data_list.txt` | `ls -R data/train_audio/ data/raw_long_audio/ > docs/win_data_list.txt` |

---

## 步骤三：批量数据处理

```bash
conda activate speech_train
python scripts/01_convert_audio.py --config configs/preprocess.yaml
python scripts/03_duration_stat.py --config configs/preprocess.yaml
python scripts/04_extract_mel.py --config configs/mel_config.yaml
python scripts/05_generate_metadata.py --config configs/preprocess.yaml
```

### 输出文件

| 文件 | 说明 |
|------|------|
| `outputs/processed_dataset/wavs/` | 转换后的 wav 文件 |
| `outputs/processed_dataset/mels/` | Mel 特征 .npy 文件 |
| `outputs/processed_dataset/metadata.csv` | 音频元数据表 |
| `outputs/processed_dataset/duration_report.csv` | 时长统计 |
| `docs/duration_distribution.png` | 时长分布图 |
| `docs/mel_example.png` | Mel 频谱图 |

---

## 步骤四：VAD 切分

### 前置

确认 `configs/vad_config.yaml` 中 `input_audio` 指向你的长音频文件：

```yaml
input_audio: data/raw_long_audio/你的文件名.wav
```

### 运行

```bash
conda activate speech_train
python scripts/06_vad_segment.py --config configs/vad_config.yaml
python scripts/07_denoise.py --input_dir outputs/preprocess_output/segments --output_dir outputs/preprocess_output/denoised
```

> 注意：这两个脚本我还没写，等你前面步骤完成后告诉我，我写好你 pull 下来再跑。

### 输出文件

| 文件 | 说明 |
|------|------|
| `outputs/preprocess_output/vad_result.csv` | VAD 检测时间戳 |
| `outputs/preprocess_output/segments/` | 切出的短音频片段 |
| `outputs/preprocess_output/denoised/` | 降噪后的音频 |
| `docs/vad_result.png` | VAD 切分结果图 |

---

## 步骤五：TTS 推理

选择一个开源模型（推荐 GPT-SoVITS 或 CosyVoice），按官方文档安装配置：

1. 准备**你自己录音的**参考音频（几十秒清晰语音，放 `tts_demo/ref_audio/`）
2. 准备 `tts_demo/test_sentences.txt`（每行一句测试文本，10-20 条）
3. 批量生成合成语音到 `outputs/generated_audio/`
4. 记录推理参数到 `tts_demo/inference_log.csv`

### `inference_log.csv` 格式

```csv
id,model_name,text,reference_audio,generated_audio,inference_time,ref_duration,remark
001,gpt_sovits,今天天气真好,tts_demo/ref_audio/me.wav,outputs/generated_audio/001.wav,2.3,5.0,
```

### 输出文件

| 文件 | 说明 |
|------|------|
| `outputs/generated_audio/*.wav` | 合成语音（最重要，传给 Mac 做 MOS 评测） |
| `tts_demo/inference_log.csv` | 推理参数记录 |
| `tts_demo/test_sentences.txt` | 测试文本 |

---

## 传回 Mac 的文件清单（最终汇总）

```
outputs/generated_audio/*.wav      → 放到 Mac 的 data/eval_data/
tts_demo/inference_log.csv          → MOS 评测参考
outputs/preprocess_output/vad_result.csv
outputs/preprocess_output/segments/
docs/vad_result.png
docs/duration_distribution.png
docs/mel_example.png
```

---

## PS：日常代码同步流程

```
Mac 改代码 → git push
     ↓
Win 拉代码 → git pull
     ↓
Win 跑训练/推理 → 输出结果文件
     ↓
Win 传结果给 Mac → 评测和写报告
```
