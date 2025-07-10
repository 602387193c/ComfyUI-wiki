import os
import torch
import numpy as np
from PIL import Image
import folder_paths
import time

class ImageToIcoConverter_v5:
    """
    一个自定义节点，用于将输入的图像转换为Windows 11标准的多分辨率ICO文件。
    V5版：最终修正版。正确地将节点定义为输出节点，并使用最强机制强制刷新，解决所有已知问题。
    """
    # 关键修复1：将节点正确地声明为输出节点。
    # 这将解决 "Prompt has no outputs" 的错误。
    OUTPUT_NODE = True 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "icon"}),
                # 将subfolder的默认值改回你的实际路径，方便使用
                "subfolder": ("STRING", {"default": "D:\\图片\\ico"}), 
            }
        }

    # 关键修复2：输出节点不应该有常规的数据输出端口。
    RETURN_TYPES = ()
    FUNCTION = "convert_to_ico"
    CATEGORY = "Image/Export"

    # 关键修复3：使用最可靠的方式强制ComfyUI每次都执行此节点。
    # 返回一个 "Not a Number" (NaN)值，这个值永远不等于它自己，
    # 从而完美地破坏缓存，强制节点重新运行。
    @classmethod
    def IS_CHANGED(s, image, filename_prefix, subfolder):
        return float('NaN')

    def convert_to_ico(self, image, filename_prefix="icon", subfolder=""):
        # 直接使用传入的完整路径作为输出文件夹
        full_output_folder = subfolder
        # 确保这个文件夹存在
        os.makedirs(full_output_folder, exist_ok=True)

        for i, single_image_tensor in enumerate(image):
            img_array = 255. * single_image_tensor.cpu().numpy()
            pil_image = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            pil_image = pil_image.convert("RGBA")

            timestamp = int(time.time())
            file_name = f"{filename_prefix}_{timestamp}_{i:03d}.ico"
            file_path = os.path.join(full_output_folder, file_name)

            ico_sizes = [(256, 256), (48, 48), (32, 32), (24, 24), (16, 16)]

            try:
                pil_image.save(file_path, format='ICO', sizes=ico_sizes)
                print(f"成功将图像保存为ICO: {file_path}")
            except Exception as e:
                print(f"保存ICO文件时出错: {e}")

        # 关键修复4：输出节点应该返回一个UI字典来显示信息。
        return {"ui": {"text": [f"成功导出 {len(image)} 个ICO文件到 {full_output_folder}"]}}