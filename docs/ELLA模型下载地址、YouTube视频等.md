# ELLA模型下载地址、YouTube视频等
YouTube视频指南: [https://youtu.be/_Pr7aFkkAvY](https://youtu.be/_Pr7aFkkAvY)
ELLA:为扩散模型配备大型语言模型，以增强语义对齐
CLIP总是出错！如果你要求一个蓝熊戴红帽，很可能得到一个红熊戴蓝帽。使用ELLA就不会这样了！现在你可以提供长而详细的提示，并确实得到你所要求的内容。只是别指望得到完美的手部
# ComfyUI指南:
使用ComfyUI管理器安装 [https://github.com/ExponentialML/ComfyUI_ELLA](https://github.com/ExponentialML/ComfyUI_ELLA)
模型应保存在您的`ComfyUI/models`目录下

首先下载的模型是ELLA模型，您应将其保存在ComfyUI/models/ella
[https://huggingface.co/QQGYLab/ELLA/blob/main/ella-sd1.5-tsc-t5xl.safetensors](https://huggingface.co/QQGYLab/ELLA/blob/main/ella-sd1.5-tsc-t5xl.safetensors)

第二个下载的是flan-t5-xl，应保存在ComfyUI/models/t5_model/flan-t5-xl
原始t5 = [https://huggingface.co/google/flan-t5-xl/tree/main](https://huggingface.co/google/flan-t5-xl/tree/main)
较小的t5 = [https://huggingface.co/Kijai/flan-t5-xl-encoder-only-bf16/tree/main](https://huggingface.co/Kijai/flan-t5-xl-encoder-only-bf16/tree/main)

下载所有文件的命令:

```
git clone https://huggingface.co/google/flan-t5-xl
```

（可选地将该目录重命名为flan-t5-xl）

推荐下载软件，免费且强大！如果你网络不稳定，需要一个一个地下载模型。
[neatdownloadmanager](https://www.neatdownloadmanager.com/index.php/en/)
# 原始仓库指南:

URL: [https://github.com/TencentQQGYLab/ELLA](https://github.com/TencentQQGYLab/ELLA)

```
conda create --name ella python=3.10
```

```
conda activate ella
```

```
git clone https://github.com/TencentQQGYLab/ELLA.git
```

```
cd ELLA
```

```
pip install fire gradio==3.50.2 torch torchvision diffusers transformers accelerate sentencepiece
```

```
python inference.py test test ./ella-sd1.5-tsc-t5xl.safetensors
```

注意：Gradio 4.26.0 不适用，因为它的功能已经被弃用

链接:

⬇️[https://ella-diffusion.github.io/](https://ella-diffusion.github.io/)

⬇️[https://github.com/TencentQQGYLab/ELLA](https://github.com/TencentQQGYLab/ELLA)

⬇️[https://github.com/ExponentialML/ComfyUI_ELLA](https://github.com/ExponentialML/ComfyUI_ELLA)

⬇️[https://huggingface.co/QQGYLab/ELLA/blob/main/ella-sd1.5-tsc-t5xl.safetensors](https://huggingface.co/QQGYLab/ELLA/blob/main/ella-sd1.5-tsc-t5xl.safetensors)

⬇️[https://huggingface.co/google/flan-t5-xl/tree/main](https://huggingface.co/google/flan-t5-xl/tree/main)

⬇️[https://huggingface.co/Kijai/flan-t5-xl-encoder-only-bf16/tree/main](https://huggingface.co/Kijai/flan-t5-xl-encoder-only-bf16/tree/main)

[ELLA_compare_v1.json](https://www.patreon.com/file?h=102141703&i=18466260)

