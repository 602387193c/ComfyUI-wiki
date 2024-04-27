# Hyper-SD in ComfyUI!
# 模型选项
基本上你有三种选择：
1. 他们的1-step SDXL UNET
2. 任何SD1.5模型，但配备他们的LORA
3. 任何SDXL模型，但配备他们的LORA
# 安装
https://huggingface.co/ByteDance/Hyper-SD
1. 下载` ComfyUI-HyperSDXL1StepUnetScheduler `到 `ComfyUI/custom_nodes`
2. 下载 `Hyper-SDXL-1step-Unet-Comfyui.fp16.safetensors `到 `ComfyUI/models/checkpoints`
3. 下载 `LoRAs `到` ComfyUI/models/loras`
# 工作流程
对于 LoRA 选项，无论是 SD1.5 还是 SDXL，采用相同的工作流程 - 只需选择与您的模型匹配的 LoRA。

