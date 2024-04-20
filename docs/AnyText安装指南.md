# [AnyText](https://github.com/tyxsspa/AnyText)安装指南

# 安装完成后一键启动

```
D: && cd D:\AnyText
conda activate anytext
et CUDA_VISIBLE_DEVICES=0
python demo.py
```

# 安装过程：

```
git clone https://github.com/tyxsspa/AnyText.git
```

```
d: && cd D:\AnyText
```

到自己的阿里云盘下载字体Arial_Unicode.ttf放到这里
字体下载地址：Arial_Unicode.ttf https://www.alipan.com/s/fiJwYE8xHxg 点击链接保存。

```
D:\AnyText\font\Arial_Unicode.ttf
```

```
conda create -n anytext python=3.10.6
```

```
conda activate anytext
```

这里是自己探索的，也许不用这样，按照官方的来就行。主要问题还是后面2个issues解决了才行吧！

到这里去查：[https://pytorch.org/get-started/previous-versions/](https://pytorch.org/get-started/previous-versions/)得到到这个命令，这样才和`environment.yaml`的环境一致。

```
conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.7 -c pytorch -c nvidia
```

新建一个`requirements.txt`输入`environment.yaml`pip后面的内容

```
Pillow==9.5.0
gradio==3.50.0
albumentations==0.4.3
opencv-python==4.7.0.72
imageio==2.9.0
imageio-ffmpeg==0.4.2
pytorch-lightning==1.5.0
omegaconf==2.2.3
test-tube==0.7.5
streamlit==1.20.0
einops==0.4.1
transformers==4.30.2
webdataset==0.2.5
kornia==0.6.7
open_clip_torch==2.7.0
torchmetrics==0.11.4
timm==0.6.7
addict==2.4.0
yapf==0.32.0
safetensors==0.4.0
basicsr==1.4.2
jieba==0.42.1
modelscope==1.10.0
tensorflow==2.13.0
torch==2.0.1
torchvision==0.15.2
easydict==1.10
xformers==0.0.20
subword-nmt==0.3.8
sacremoses==0.0.53
sentencepiece==0.1.99
fsspec
diffusers==0.10.2
ujson
```

安装依赖

```
pip install -r requirements.txt
```

运行`python` `inference.py`会报错。

# 从项目源网址找到2个issues，相应解决应该就行了

第一个：[https://github.com/google/tangent/issues/11#issuecomment-455910041](https://github.com/google/tangent/issues/11#issuecomment-455910041)

> 对于使用中文操作系统语言的用户，如果您遇到了由于系统区域设置导致的编码问题或某些程序安装问题，可以尝试以下步骤来更改系统区域设置，并启用 Unicode UTF-8 支持：

> 打开控制面板：

- 您可以通过点击“开始”菜单，然后选择“控制面板”来打开它。

> 访问区域设置：

- 在控制面板中，找到并点击“区域”或“时钟、语言和区域”（取决于您的 Windows 版本，这可能有所不同）。

> 更改系统区域设置：

- 在“区域”窗口中，点击“管理”标签页。
- 在“管理”标签页中，找到“非 Unicode 程序的语言”部分，点击“更改系统区域设置”按钮。

> 勾选 Beta 版选项：

- 在弹出的“系统区域设置”窗口中，勾选“Beta版：使用 Unicode UTF-8 提供全球语言支持(U)”选项。

> 重启电脑：

- 应用更改并重启您的电脑以使设置生效。

> 请注意，启用“使用 Unicode UTF-8 提供全球语言支持”的选项可能会影响系统显示和其他非 Unicode 应用程序的语言支持。这个选项主要是为了支持那些需要 UTF-8 编码的应用程序，但并不是所有的应用程序都能正确地与之兼容。

> 在进行这些更改之前，请确保您了解它们可能带来的影响，并且已经保存了所有重要的工作。如果您不确定，可以考虑先在一台不常用的电脑上尝试这些更改，或者在虚拟机中进行测试。

> 此外，如果您在更改设置后遇到问题，可以返回到“系统区域设置”窗口，取消勾选该选项，并重启电脑以恢复到之前的设置。

第二个：[https://github.com/modelscope/modelscope/pull/712/files](https://github.com/modelscope/modelscope/pull/712/files)

找到虚拟环境的这个文件：

```
"C:\anaconda3\envs\anytext\Lib\site-packages\modelscope\pipelines\nlp\translation_pipeline.py"
```

修改第55，60，84行。

# 最后就可以运行了

```
set CUDA_VISIBLE_DEVICES=0 && python demo.py
```

