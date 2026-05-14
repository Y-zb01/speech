# 环境配置指南

## Mac 端

```bash
# 系统工具
brew install ffmpeg git miniconda

# 初始化 conda
conda init zsh
# 重开终端

# 创建环境
conda create -n speech_mac python=3.10 -y
conda activate speech_mac

# 安装依赖
pip install librosa soundfile numpy pandas matplotlib scipy gradio pydub noisereduce pyyaml
```

## Windows WSL2 端

### 安装 WSL2

在 Windows PowerShell（管理员）中：

```bash
wsl --install
```

重启后进入 Ubuntu。

### 配置 Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl build-essential ffmpeg sox libsndfile1
```

### 安装 Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# 重开终端
```

### 创建训练环境

```bash
conda create -n speech_train python=3.10 -y
conda activate speech_train
pip install torch torchaudio numpy pandas matplotlib scipy librosa soundfile pydub noisereduce gradio pyyaml
```

### 验证 GPU

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

期望输出 `True` 和显卡型号。

## 拉取项目代码

```bash
git clone https://github.com/Y-zb01/speech.git
cd speech
```
