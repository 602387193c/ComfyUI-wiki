# MiniMax H3 本地加速实测

这次测试起因很简单。MiniMax H3 在 ComfyUI 里已经能原生生成视频和声音，但十来秒的片段如果每次都要等四五十分钟，很难用于长视频生产。我在一张 RTX PRO 6000 Blackwell Workstation Edition 96GB 上依次测试了 SageAttention 2.2.0 和 MiniMax H3 专用的 Spectrum 节点，并保留了同条件 A/B、画质指标、显存监控和失败样本。

本文附带一个可直接拖入 ComfyUI 的 Ref2VA 编辑器工作流。它以 ComfyUI 官方 Ref2VA 模板为基础，只增加 Spectrum 节点，并保留开关供关键镜头切回原生路径。

[下载 MiniMax H3 Ref2VA、SageAttention、Spectrum 工作流](workflows/MiniMax-H3-Ref2VA-SageAttention-Spectrum.json)

## 测试环境

| 项目 | 本次配置 |
| --- | --- |
| 系统 | Windows 11 |
| 显卡 | NVIDIA RTX PRO 6000 Blackwell Workstation Edition 96GB |
| 驱动 | 596.36 |
| ComfyUI | 0.30.0，提交 `b1693ecba9f5b65f8c80ab36b195ab963ec92413` |
| Python | 3.13.12 |
| PyTorch | 2.11.0+cu130 |
| CUDA | PyTorch 运行时 13.0，本机工具链 13.3 |
| SageAttention | 2.2.0，本机为 `sm_120` 编译 |
| Spectrum 节点 | 0.1.4，提交 `8bfc235cb3910c73964277e0316ec875f4b2c011` |
| H3 主模型 | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| 文本编码器 | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| 输出规格 | 1344×768，24fps，20 步，RES multistep |

模型精度、片长、参考图数量和参考模式都会改变速度与显存。下面的数字适合帮助判断量级，不能脱离配置单独比较。

## 第一层加速 SageAttention

SageAttention 替换注意力计算内核。它的官方项目要求 Python 3.9 以上、PyTorch 2.3 以上。Blackwell 与 SageAttention2++ 路径要求 CUDA 12.8 以上。RTX PRO 6000 的计算能力是 `sm_120`，Windows 用户要让 Python、PyTorch、CUDA、编译器和目标架构完全对应。装进环境并不代表已经启用，ComfyUI 的启动日志里还要确认 SageAttention 被选中。

本次启动参数如下。

```text
--highvram --use-sage-attention
```

我先跑了一个 BF16 注意力微基准，输入形状为 `1×56×2048×128`。PyTorch SDPA 平均耗时 0.842 毫秒，SageAttention 平均耗时 0.333 毫秒，内核速度约为 2.525 倍。平均绝对误差为 0.00111，最大绝对误差为 0.0146484，没有 NaN。

完整 H3 测试更接近日常生产。目标视频为 207 帧，普通流程耗时 2111.8 秒，启用 SageAttention 后耗时 1278.8 秒。端到端速度为原来的 1.651 倍，时间减少 39.4%。加速输出的全帧 SSIM 为 0.923278，平均 PSNR 为 25.340586dB，黑场与静音检查均通过。

内核快 2.5 倍以后，完整视频没有跟着快 2.5 倍。参考输入、文本编码、其他网络层、视频与音频 VAE、文件编码仍然要花时间。对生产有用的数字始终是从任务提交到文件落盘的总时长。

## 第二层加速 Spectrum

Spectrum 用历史真实步骤的特征预测后续步骤。MiniMax H3 节点会在实际步骤记录最后一个 Transformer Block 后的隐藏特征，在预测步骤跳过 Transformer Blocks，随后继续执行 H3 自己的输出头、视频重建、音频重建和 sigma 映射。它不需要重新训练模型。

节点应放在模型加载、LoRA 等模型补丁和 H3 sigma shift 之后，再连接 guider 与 sampler。本文工作流没有额外 sigma shift 节点，所以它直接放在模型加载器与调度器、guider 之间。

本次保守参数如下。

| 参数 | 数值 |
| --- | --- |
| `enabled` | `true` |
| `blend_weight` | 0.50 |
| `degree` | 4 |
| `ridge_lambda` | 0.10 |
| `window_size` | 2.0 |
| `flex_window` | 0.75 |
| `warmup_steps` | 5 |
| `tail_actual_steps` | 1 |
| `max_history` | 8 |
| `history_storage` | `system_ram` |

RES multistep 会保证最后三步走真实计算。20 步采样最终记录到 14 次真实计算和 6 次预测，Transformer 计算次数减少 30%。

严格 A/B 使用同一素材、提示词、参考图、seed、模型、采样器和输出规格。两边都已经启用 SageAttention，唯一变量是 Spectrum。

| 路径 | 端到端耗时 |
| --- | --- |
| Native + SageAttention | 611.0 秒 |
| Spectrum + SageAttention | 400.8 秒 |
| 时间减少 | 34.4% |
| 吞吐提升 | 1.524 倍 |

两段输出的全帧 SSIM 为 0.961343，平均 PSNR 为 31.904424dB。InsightFace 在两边都检测到 11 个主要人脸样本，身份匹配率都是 1.0。MOSS 转写识别到相同的三句台词，第二句结束时间相差 0.07 秒。

## 两个倍数不能直接相乘

SageAttention 的 1.651 倍和 Spectrum 的 1.524 倍来自两轮不同片段、不同基准的测试。第二轮的两条路径已经共同启用 SageAttention。把它们相乘只能得到一个数学结果，不能称作本次组合实测。

目前可以确认 SageAttention 在第一轮节省 39.4% 的端到端时间。Spectrum 在已开启 SageAttention 的第二轮又节省 34.4%。若要得到组合方案相对最初状态的严格倍数，还要用同一片段跑普通注意力、单独 SageAttention、单独 Spectrum、两者同时启用四组完整对照。

## 画质风险与失败样本

Spectrum 是近似加速，不保证逐位一致。快速或短暂动作可能改变姿态、视线、动作轨迹和时机。眼睛、手指、指甲等小结构在快速运动时也可能变形。人物特写、高速打斗、手部、眼神和口型要求高的镜头，建议同 seed 跑一次原生复核，或者直接关闭 Spectrum。

测试期间还出现过整段糊成灰色纹理的视频。原生路径和 Spectrum 路径在相同长序列条件下都发生过，更换 seed 只能救回短测试。按照真实场景边界把条件拆成两个较长片段以后，问题消失。长序列条件、参考图冲突、人物数量、切镜和 seed 都可能参与其中。看到坏片时，不能仅凭是否挂了加速节点判断原因。

另一个容易误判的是预热任务。1 步、5 帧输出只负责让模型提前加载，画面自然会是一团模糊。预热文件不能用来判断模型画质。

## 显存历史放系统内存还是显存

Spectrum 会保留真实步骤的特征历史。官方节点提供 `system_ram` 与 `vram` 两种位置。在 1344×768、124 帧示例中，八份条件与无条件历史可能接近 6.1GiB。

本次 340 帧长片段的峰值显存约为 74758MiB，平均 GPU 利用率 95.96%，平均功耗 582.47W，最高温度 90 摄氏度。96GB 卡仍然选择了 `system_ram`，因为留下二十多 GB 余量比追求不稳定的几个百分点更有用。节点作者提供的三组约 0.5MP 测试中，显存历史平均只快约 2.6%，单组结果有快有慢。

显存较小的用户应先选 `system_ram`，并考虑缩短片长、降低分辨率或减少参考图。`max_history` 不能低于 `degree + 1`。本次 degree 为 4，所以至少需要 5 份历史。

## 推荐复现顺序

1. 固定一段五秒左右的素材，同时固定提示词、参考图、seed、分辨率、帧数、步数、采样器和模型权重。
2. 先测原生 ComfyUI，记录总时长、采样时长、峰值显存、GPU 利用率、温度与功耗。
3. 只开启 SageAttention。启动日志确认生效以后再计入结果。
4. 在两边都启用 SageAttention的条件下，对 Spectrum 做同 seed A/B。
5. 查看 Spectrum 日志。RES multistep 的保守配置应记录 14 次真实计算与 6 次预测，频繁 fallback 的结果没有速度参考价值。
6. 比较 SSIM、PSNR、人脸身份和台词转写，再人工检查快速动作、眼睛、手、口型与切镜。
7. 至少覆盖静态对话、人物特写、快速动作和复杂多人场面，再决定是否批量生产。

这轮没有继续叠加 EasyCache、torch compile 或更多缓存节点。一次只增加一个变量，出错时才知道该查哪一层。生产工作流里应始终保留关闭 Spectrum 和移除 `--use-sage-attention` 的原生回退路径。

## 安装地址与资料

- [ComfyUI 官方仓库](https://github.com/Comfy-Org/ComfyUI)
- [ComfyUI MiniMax H3 Day 0 官方文章](https://blog.comfy.org/p/minimax-h3-day-0-support-in-comfyui)
- [ComfyUI 官方 MiniMax H3 模型库](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [SageAttention 官方仓库](https://github.com/thu-ml/SageAttention)
- [SageAttention 论文](https://arxiv.org/abs/2410.02367)
- [SageAttention2 论文](https://arxiv.org/abs/2411.10958)
- [Spectrum 论文](https://arxiv.org/abs/2603.01623)
- [Spectrum 官方研究代码](https://github.com/hanjq17/Spectrum)
- [MiniMax H3 的 ComfyUI Spectrum 节点](https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3)
- [NVIDIA RTX PRO 6000 官方规格](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf)

SageAttention 的启动参数属于全局配置，不会保存在工作流 JSON 里。下载工作流以后，先安装 Spectrum 自定义节点，再按自己的 Python、PyTorch、CUDA 与显卡架构安装 SageAttention。关键镜头随时可以把 Spectrum 节点的 `enabled` 改为 `false`，保留同一套工作流走原生计算。
