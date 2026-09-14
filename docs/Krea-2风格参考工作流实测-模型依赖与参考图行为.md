# Krea-2 图像风格参考工作流实测（krea2_turbo_int8_image_style_reference）

实测环境：ComfyUI 0.35.0 / 前端 1.52.7 / PyTorch 2.11.0+cu130 / RTX PRO 6000 96GB / Python 3.13.12。

对应工作流：`ComfyUI/user/default/workflows/krea2_turbo_int8_image_style_reference.json`（模板包里叫
`image_krea2_turbo_int8_image_style_reference.json`）。

## 一、这个工作流在做什么

它是一条**参考图条件生成**通路，不是普通的文生图。结构分两段：

1. 参考图 `LoadImage` → `TextEncodeQwenImageEditPlus`（Qwen3-VL 文本编码器，同时吃图）→
   `FluxKontextMultiReferenceLatentMethod`（`index_timestep_zero`）→ 参考 latent 拼进注意力的 token 序列。
2. 主干：`krea2_turbo_int8_convrot` UNet + `krea2_style_reference` LoRA，8 步 euler/simple，
   `ModelSamplingFlux`（max_shift 1.15 / base_shift 0.5），CFG=1。

另外带了一个可选的提示词增强分支：`TextGenerate`（用同一个 Qwen3-VL 做文本生成）+
`StringConcatenate` + `ComfySwitchNode`。**默认是关的**（Boolean 节点为 false），此时走原始提示词。
注意这条分支虽然不生效，`TextGenerate` 仍会被执行一次，会多花一两秒。

## 二、模型清单——照文档下就行，但有两点要注意

工作流里的 MarkdownNote 给了 4 个文件，路径与实际存放位置完全对得上：

| 目录 | 文件 | 大小 |
| --- | --- | --- |
| `diffusion_models` | `krea2_turbo_int8_convrot.safetensors` | 12.57 GB |
| `text_encoders` | `qwen3vl_4b_fp8_scaled.safetensors` | 4.88 GB |
| `vae` | `qwen_image_vae.safetensors` | 0.24 GB |
| `loras` | `krea2_style_reference.safetensors` | 0.43 GB |

**注意 1：LoRA 是必需组件，不是画风微调。**
这一点最容易踩。参考图那条通路如果缺了 `krea2_style_reference` LoRA，输出会出现大面积块状马赛克损坏。
实测对照（同种子、同提示词、同参考图，只切 LoRA）：

- 无 LoRA：`_krea2/results/v3_char_identity/` —— 满屏方块噪点，背景几乎糊掉。
- 有 LoRA：`_krea2/final/z5_char_identity/` —— 干净赛璐璐上色，线条清晰。

LoRA 不是"效果更好一点"，而是这条通路的必需件。换上 int8 模型后即使喂未裁切的原始参考图，
带 LoRA 也不再出现乱码字幕。**不要为了省 0.43 GB 跳过它。**

**注意 2：`krea2_turbo_fp8_scaled` 不能直接顶替 int8 版本。**
本地已有 fp8 版时很容易想省下 12.57 GB 的下载，但两者不是等价替换：

- fp8 模型在**完全不带参考图**的文生图路径上是干净的。
- fp8 模型一旦走参考图路径，即使挂了 LoRA，画面仍保留明显的块状噪点（可自行对比
  `_krea2/final/` 与早期 fp8 结果）。
- 官方模板把 int8 写成默认值是有原因的，用 int8。

## 三、参考图会连构图一起搬过来

这个行为必须提前知道：**模型是照着参考图的版式重画，而不是只借画风。**

实测：喂 `source_board.png`（3×2 分格拼版，末格空白），输出就是 3×2 分格拼版、末格留白；
喂 Paprika 的角色设定拼图，输出就是同款六格拼图，连里面的人物和场景都跟着复现。

四个 `reference_latents_method` 都试过（`offset` / `index` / `uxo/uno` / `index_timestep_zero`），
**全都照搬版式**，没有哪个能只借风格不借构图。把参考图缩到 512px 也一样。

实际用法上这意味着：想控制出图版式，就从参考图的版式下手；
如果只想要单张图，参考图也应该是单张，别喂拼版。

## 四、参考图里的烧录字幕会被抄进成品

源图每格底部带中文字幕时，模型会把它们原样抄过去，并且抄成乱码（"做右字字孚大璽靌"这类）。
加 "no text, no watermark" 压不住，模型反而更容易在对应位置生成文字。

**解法：先把参考图每格底部约 18% 裁掉再喂进去。** 裁掉之后乱码字幕直接消失。

裁切函数（3×2 拼版、去掉每格底部 18%，并把尺寸对齐到 8 的倍数）：

```python
from PIL import Image

def crop_subtitle_band(src, dst, keep=0.82):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    ph, pw = h // 2, w // 3
    keep_h = int(ph * keep)
    out = Image.new("RGB", (pw * 3, keep_h * 2))
    for r in range(2):
        for c in range(3):
            out.paste(im.crop((c * pw, r * ph, (c + 1) * pw, r * ph + keep_h)),
                      (c * pw, r * keep_h))
    out = out.crop((0, 0, out.width - out.width % 8, out.height - out.height % 8))
    out.save(dst)
```

如果用的是 int8 + LoRA，这一步的影响会小很多（不再出乱码），但仍建议做，能少一类干扰。

## 五、实测性能

RTX PRO 6000 96GB 上，模型常驻显存后：

| 配置 | 单张耗时 |
| --- | --- |
| 1024×1024，8 步 | 约 6～9 秒 |
| 1928×1088（2.0MP），8 步 | 约 9～10 秒 |
| 1928×1088（2.0MP），20 步 | 约 22 秒 |

首次加载 int8 模型需要一两分钟。步数给足明显更干净：同条件 20 步比 8 步线条和面部都稳，
追求质量时值得从 8 步提到 20 步。

分辨率由 `ResolutionSelector` 算：`aspect_ratio` + `megapixels` + `multiple`（对齐 8）。
1.0MP 约等于 1024×1024。

## 六、辅助脚本

放在 `C:\AI\ComfyUI_windows_portable\_krea2\`：

- `ui2api.py` —— 把 UI 格式工作流转成 API 格式并直接提交。会拿服务端 `/api/object_info`
  校验每个节点类型和输入名，支持 `--set 节点.输入=值`、`--drop 节点ID`（带旁路透传，等价于 UI 的
  bypass）、`--unset 节点.输入`。返回头是 `definitions.subgraphs` 折叠形式的模板也能用。
- `run_prompt.py` —— 提交 API prompt，走 WebSocket 跟进度，超时回落到 `/history` 轮询。
- `final_suite.py` —— 终验用例集。
- `diag*.py` —— 前面几节结论对应的对照实验脚本。

批量测试时注意一个坑：ComfyUI 的缓存键只看节点输入。两个用例如果提示词、种子、尺寸全一样、
只有参考图不同，容易被判成命中缓存而不出图。**每个用例给不同种子**，并确认输出文件真的落盘。

## 七、网络

外网被限得很死，实测：HF 直连单流 0.01～1.3 MB/s，hf-mirror 基本为零，
ModelScope 0.2～0.3 MB/s，Cloudflare 测速也只有 0.32 MB/s——是全局约 0.3 MB/s 的天花板，
不是选错源的问题。12.57 GB 的 UNet 无论走哪个源都要数小时，建议手动下载或挂代理。
模型在 ModelScope 上有同源镜像：`Comfy-Org/Krea-2`，文件与 HF 完全对应。

## 八、结论

按文档下齐 4 个模型（**含 LoRA**）后，工作流可以直接跑通，产出质量相当好：干净的二维赛璐璐上色、
角色身份一致、能按参考图版式组织多格分镜。用于"3D 源片 → 2D 分镜"这类流水线是可行的。

需要注意的就三条：LoRA 必须装、参考图决定版式、参考图别带烧录字幕（或先裁掉）。
