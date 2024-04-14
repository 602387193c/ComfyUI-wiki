# ComfyUI如何共享模型文件

ComfyUI提供了一种方便的方式来共享和管理模型文件,即通过`extra_model_paths.yaml`配置文件来指定外部模型路径。下面是具体的操作步骤:

1. 在ComfyUI的安装目录下,找到`extra_model_paths.yaml.example`文件,将其重命名为`extra_model_paths.yaml`。

   > [!NOTE]
   > 请确保您的操作系统设置为显示文件扩展名,以便您能看到完整的文件名。

2. 使用文本编辑器(如记事本、VSCode等)打开`extra_model_paths.yaml`文件。该文件中包含了详细的说明和示例,您可以参照这些内容来配置您的模型路径。

3. 在配置文件中,您可以看到预定义的一些常用模型类型,如`checkpoints`、`clip`、`vae`等。您也可以根据需要添加其他的模型类型,例如我在这里添加了一个用于运行Cascade模型的`unet`文件夹。

4. 如果您想让新安装的ComfyUI和现有的另一个ComfyUI共享同一组模型文件,可以参考以下示例:

   > [!ATTENTION请特别注意]
   > - 如果您不需要共享某个UI的模型(如a1111),请在对应的配置块前添加`#`号将其注释掉,或者直接删除该配置块。而对于您需要共享的UI模型(如ComfyUI),请确保移除配置块前的`#`号。
   > - 在配置文件中,每个配置项前面必须有**4个空格**的缩进。

```
comfyui:
    base_path: C:\AI\ComfyUI_windows_portable\ComfyUI
    checkpoints: C:\AI\ComfyUI_windows_portable\ComfyUI\models\checkpoints
    clip: C:\AI\ComfyUI_windows_portable\ComfyUI\models\clip 
    clip_vision: C:\AI\ComfyUI_windows_portable\ComfyUI\models\clip_vision
    configs: C:\AI\ComfyUI_windows_portable\ComfyUI\models\configs
    controlnet: C:\AI\ComfyUI_windows_portable\ComfyUI\models\controlnet
    embeddings: C:\AI\ComfyUI_windows_portable\ComfyUI\models\embeddings
    loras: C:\AI\ComfyUI_windows_portable\ComfyUI\models\loras
    upscale_models: C:\AI\ComfyUI_windows_portable\ComfyUI\models\upscale_models
    vae: C:\AI\ComfyUI_windows_portable\ComfyUI\models\vae
    unet: C:\AI\ComfyUI_windows_portable\ComfyUI\models\unet
```

5. 配置完成后,保存`extra_model_paths.yaml`文件。ComfyUI启动时会自动加载这个配置文件,并根据其中的设置来查找模型文件。

通过使用`extra_model_paths.yaml`配置文件,您可以灵活地管理ComfyUI的模型文件,并方便地与其他ComfyUI实例共享这些模型。这不仅可以节省磁盘空间,也使得模型的升级和维护更加简单。
