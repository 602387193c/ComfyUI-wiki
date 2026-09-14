# ComfyUI 多参考图接入方式（以 Qwen-Image / Krea-2 系为例）

做风格迁移类工作时经常需要"人物参考图 + 画风参考图"同时喂给模型。这里记录踩过的坑和正确接法。

## 一、节点本身支持多图，但工作流通常只接了一张

`TextEncodeQwenImageEditPlus` 实际有 3 个图像输入：

```
required : clip, prompt
optional : vae, image1, image2, image3
```

所以"多参考图"不需要改节点类型，把 `image2` / `image3` 接上就行。
但要注意：**Krea-2 那个风格参考工作流只接了 `image1`**（`LoadImage` → `image1`），
`image2` / `image3` 是空的。想加第二张参考图，得自己在 API prompt 里补连线。

## 二、最容易踩的坑：IMAGE 输入不能传文件名字符串

`image2` / `image3` 是 **IMAGE 类型**，必须给**上游节点连线**，形如 `[节点ID, 输出槽位]`。
直接塞 `"myimage.png"` 这种字符串，节点会拿字符串当张量用，报：

```
AttributeError: 'str' object has no attribute 'movedim'
  File ".../comfy_extras/nodes_qwen.py", line 82, in execute
    samples = image.movedim(-1, 1)
```

这个报错不直观，容易误判成模型或显存问题。正确做法是**补一个独立的 `LoadImage` 节点**，
再把它连到 `image2`：

```python
prompt["900"] = {                      # 新的 LoadImage 节点
    "class_type": "LoadImage",
    "inputs": {"image": "style_ref.png"},
    "_meta": {"title": "LoadImage (style_ref.png)"},
}
prompt["90"]["inputs"]["image2"] = ["900", 0]   # 连到 TextEncode 的 image2
```

注意 `LoadImage` 的 `image` 只认**文件名**，且文件必须已经躺在 `ComfyUI/input/` 下；
给绝对路径不行，要先复制进去。

## 三、多参考图的实际效果

实测（Krea-2 int8 + style-reference LoRA，20 步，1.5MP）：

| 接法 | 结果 |
| --- | --- |
| 只接 `image1`（角色源图） | 版式和构图跟源图，画风靠提示词描述 |
| `image1`（角色源图）+ `image2`（画风图） | 保住了角色特征，画风也向 `image2` 靠 |
| 只接 `image1`（画风多视角图） | 整张多视角版式被照搬，角色被画成参考图里的角色 |

也就是说 `image1` 依然强势主导版式，`image2` 起到补充风格/特征的作用，**不是等权融合**。

## 四、多视角设定图当风格参考的注意事项

"多视角设定图"（一张图里几格不同角度）当风格参考时会遇到两个问题：

1. **版式会被照搬**：参考图是几格拼版，输出就是几格拼版。
   想要单张出图，就别直接喂整张拼版。
2. **角色年龄/性别特征会被带偏**：实测拿一张成人女性角色的多视角图当风格参考去画一个男童，
   输出会给男童加上胡子、鬓角和成人化脸型——模型把参考图的人物特征一起搬了过来。

**解法：从多视角图里裁出"只是一个头像"的那一格当风格参考。**
画面里没有人脸拼版，模型就没法照搬版式，也不会把成人特征带过去。实测裁成头像后，
胡子消失、角色正确回到孩童脸，画风仍然是参考图的日式 TV 动画赛璐璐。

裁剪时记得把尺寸对齐到 8 的倍数（VAE 要求）：

```python
from PIL import Image

def crop_face_panel(src, dst):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    face = im.crop((0, 0, int(w * 0.33), h))   # 左格头像
    face = face.crop((0, 0, face.width - face.width % 8, face.height - face.height % 8))
    face.save(dst)
```

## 五、步数：风格参考这条路 8 步不够

同一个提示词、同一张参考图，只改步数（Krea-2 Turbo）：

| 步数 | 结果 |
| --- | --- |
| 8 步 | 线条糊、块状伪影明显，细节丢失 |
| 12 步 | 明显改善 |
| 20 步 | 干净、线条锐利、可交付 |

风格参考这条路因为要同时满足参考图条件，比纯文生图更吃步数。**建议 20 步起步**，
不要用 Turbo 的默认 8 步。
