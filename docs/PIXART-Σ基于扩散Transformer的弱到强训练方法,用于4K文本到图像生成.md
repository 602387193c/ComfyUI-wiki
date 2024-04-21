
# 书呆子老鼠的PIXART-Σ-comfyui安装指南

Pixart Sigma - https://pixart-alpha.github.io/PixArt-sigma-project/

我们看到更多的模型使用 T5 条件而不是 CLIP，通常能够更好地遵循提示。这次介绍的是最近发布的 "Pixart Sigma"。

## 命令总结

使用你自己的工作空间和 Python 环境，我的ComfyUI在：`C:\AI\ComfyUI_windows_portable\ComfyUI`
### 激活自己的ComfyUI的虚拟环境，我的虚拟环境名字就叫ComfyUI
```
conda activate ComfyUI
```
### 安装ComfyUI_ExtraModels这个自定义节点及环境包
```
cd C:\AI\ComfyUI_windows_portable\ComfyUI\custom_nodes
```

```
git clone https://github.com/city96/ComfyUI_ExtraModels custom_nodes/ComfyUI_ExtraModels
```

```
cd custom_nodes/ComfyUI_ExtraModels
```

```bash
pip install -r requirements.txt
```
### 克隆PixArt-sigma这个项目到本地（为了安装requirements.txt的环境包）
```
cd C:\AI
```

```
git clone https://github.com/PixArt-alpha/PixArt-sigma.git
```

```
cd PixArt-sigma
```
#### 激活自己的ComfyUI虚拟环境
```
conda activate ComfyUI
```

```
pip install -r requirements.txt
```

```
pip install evaluate
```

```
git lfs install
```

```
python tools/download.py
```

## 下载模型
可以用`PixArt-sigma`这个项目提供的方法下载模型
也可以通过其他方式，浏览器、下载器、git clone等下载模型（我的方式）：

🗃️[模型下载PixArt-Sigma-XL-2-1024-MS](https://huggingface.co/PixArt-alpha/PixArt-Sigma/blob/main/PixArt-Sigma-XL-2-1024-MS.pth)
🗃️[pixart_sigma_sdxlvae_T5_diffusers](https://huggingface.co/PixArt-alpha/pixart_sigma_sdxlvae_T5_diffusers)。网络好的话，可以用`git clone https://huggingface.co/PixArt-alpha/pixart_sigma_sdxlvae_T5_diffusers`下载模型，下载完了是36GB，我不知道要不要下载这么多东西！
🗃️sd-vae-ft-ema这个模型用comfyui自带的sdxl的vae就行了。

## 下载完成后，将模型移动到以下位置：

```
ComfyUI/models/checkpoints/PixArt-Sigma-XL-2-1024-MS.pth
ComfyUI/models/t5/pixart_sigma_sdxlvae_T5_diffusers
ComfyUI/models/VAE/sd-vae-ft-ema
```
