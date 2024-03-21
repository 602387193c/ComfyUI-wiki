# 📄项目简介
分享最好用、最实用的ComfyUI工作流（``workflow``），最新、最前沿的研究成果和相应的自定义节点（`custom nodes`），实用的视频、文字教程和知识等。

# 📊工作流分享
2024-3-18我把最实用的工作流（workflow）都给毫无保留地分享给：[点击此处查看pysssss-workflows文件夹](./pysssss-workflows)

| 序号  | 工作流名称                                                                                     | 工作流功能                            |
| --- | ----------------------------------------------------------------------------------------- | -------------------------------- |
| 1   | [1.0Cascade_Standard](pysssss-workflows/1.0Cascade_Standard.json)                         | 基本的cascade工作流                    |
| 2   | [1.1cascade-inpainting](pysssss-workflows/1.1cascade-inpainting.json)                     | cascade的inpainting功能             |
| 3   | [2.0放大supir](pysssss-workflows/2.0放大supir.json)                                           | 个人认为目前为止最好的放大模型                  |
| 4   | [3.0检测（简单）YoloWorld-EfficientSAM](pysssss-workflows/3.0检测（简单）YoloWorld-EfficientSAM.json) | 自动检测任何物体，真的很神奇！                  |
| 5   | [3.1检测+重绘YoloWorld-EfficientSAM](pysssss-workflows/3.1检测+重绘YoloWorld-EfficientSAM.json)   | 自动检测后重绘检测的部分，比如检测图片里面的猫，然后全部换成狗。 |
| 6   | [4.0修复手部](pysssss-workflows/4.0修复手部.json)                                                 | 修复手部很好用                          |
| 7   | [5.0扩图](pysssss-workflows/5.0扩图.json)                                                     | 用的fooocus的模型，所以效果很不错，功能也很像。      |
| 8   | [6.0移除背景BRIA](pysssss-workflows/6.0移除背景BRIA.json)                                         | 描述移除背景BRIA的功能                    |

# 👍用了都说好的`custom nodes`（自定义节点）

## 📈custom nodes排行榜
[nodecafe](https://www.nodecafe.org/)这个网站，由[comfyui-workspace-manager](https://github.com/11cafe/comfyui-workspace-manager)构建，一个类似于Pypi（用于发布、共享和安装Python包的官方第三方库）的comfyui自定义节点库wiki，根据开源`custom nodes`活动的stars⭐排名！

| 序号  | Custom Nodes                                                                      | 简介（最有用的功能）                                                                                                                     |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)                    | 安装、删除、禁用和启用 ComfyUI 各种自定义节点的管理功能。此外，该扩展还提供了一个中心功能和便利功能，以便访问 ComfyUI 内部的广泛信息。                                                   |
| 2   | [ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) | 图像源：[Image Feed](https://github.com/pythongosssss/ComfyUI-Custom-Scripts?tab=readme-ov-file#image-feed)<br>添加一个面板，显示当前会话中生成的图像 |

# 💡AIGC前沿技术
（图像、视频、音频、数字人、3D等生成）

| 序号  | 项目名称及网址                                             | 介绍                                | huggingface demo（在线生成）                                             |
| --- | --------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------ |
| 1   | [InstantID](https://github.com/InstantID/InstantID) | 可实现使用单张图片进行ID保持生成的最先进方法，支持各种下游任务。 | [InstantID demo](https://huggingface.co/spaces/InstantX/InstantID) |
| 2   | [AnyText](https://github.com/tyxsspa/AnyText)       | 多语言（包括汉字！）视觉文本生成与编辑               | [AnyText demo](https://huggingface.co/spaces/modelscope/AnyText)   |


# 🏆顶级开发者（他们贡献了最棒的custom nodes）

| 序号  | 开发者                                           | 简介（主要贡献）                                                                                                                                                                                                                  |
| --- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | [ZHO-ZHO-ZHO](https://github.com/ZHO-ZHO-ZHO) | [BRIA_RMBG 1.4 in ComfyUI](https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG)：BRIA 开发的目前最好的背景去除模型，已支持批量处理（可去除视频背景）<br>[ComfyUI InstantID](https://github.com/ZHO-ZHO-ZHO/ComfyUI-InstantID): 仅需一张图就可实现高质量的角色保持！多种风格随心变！ |
| 2   | [ltdrdata](https://github.com/ltdrdata)<br>   | [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)<br> [ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)                                                                                 |
| 3   | [lllyasviel](https://github.com/lllyasviel)   | [Fooocus](https://github.com/lllyasviel/Fooocus)<br>[stable-diffusion-webui-forge](https://github.com/lllyasviel/stable-diffusion-webui-forge)                                                                            |
|     |                                               |                                                                                                                                                                                                                           |

# 🌐工作流、模型、图片生成网站

| 类别           | 网址                                        | 说明                                 |
| ------------ | ----------------------------------------- | ---------------------------------- |
| 工作流分享        | - [OpenArt](https://openart.ai/workflows) | 很多大佬分享了海量的高质量工作流。                  |
| 模型分享（也有工作流等） | - [civitai](https://civitai.com/)         | 搜索、下载和分享各种 AI 绘画模型，最齐全的网站，好像没有之一？  |
| 图片生成         | - [ideogram](https://ideogram.ai/)        | 这个网站生成的图片质量不错，可以生成文字。他们的模型也在不断迭代中。 |
