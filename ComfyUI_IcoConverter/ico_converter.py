import os
import torch
import numpy as np
from PIL import Image
import folder_paths

class ImageToIcoConverter:
    """
    一个自定义节点，用于将输入的图像转换为Windows 11标准的多分辨率ICO文件。
    """
    # 节点是否为输出节点。True意味着工作流执行到此会停止，通常用于保存文件或预览图像。
    OUTPUT_NODE = True
    
    # 定义节点的输入参数
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),  # ComfyUI的图像张量
                "filename_prefix": ("STRING", {"default": "icon"}), # 文件名前缀
                "subfolder": ("STRING", {"default": "ICO_Exports"}), # 在output目录下的子文件夹
            }
        }

    # 声明此节点没有常规的输出，因为它直接保存文件
    RETURN_TYPES = ()

    # 节点执行的主函数
    FUNCTION = "convert_to_ico"

    # 节点在UI菜单中的分类
    CATEGORY = "Image/Export"

    def convert_to_ico(self, image, filename_prefix="icon", subfolder=""):
        # 获取ComfyUI的默认输出目录
        output_dir = folder_paths.get_output_directory()

        # 如果指定了子文件夹，则创建它
        if subfolder:
            full_output_folder = os.path.join(output_dir, subfolder)
            os.makedirs(full_output_folder, exist_ok=True)
        else:
            full_output_folder = output_dir

        # ComfyUI的IMAGE是批处理的张量(batch of tensors)，我们需要遍历它
        # 张量形状为 [批大小, 高度, 宽度, 通道数]
        for i, single_image_tensor in enumerate(image):
            # 将PyTorch张量转换为PIL图像
            # 1. 从GPU移到CPU
            # 2. 转换为Numpy数组
            # 3. 将像素值从[0, 1]浮点数范围转换到[0, 255]的8位整数范围
            img_array = 255. * single_image_tensor.cpu().numpy()
            pil_image = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

            # 构建完整的文件路径和名称
            file_name = f"{filename_prefix}_{i:03d}.ico"
            file_path = os.path.join(full_output_folder, file_name)

            # 定义Win11标准的ICO尺寸
            ico_sizes = [(256, 256), (48, 48), (32, 32), (24, 24), (16, 16)]

            # 使用Pillow保存为ICO格式，并指定所有需要的尺寸
            # Pillow会自动处理图像缩放
            try:
                pil_image.save(file_path, format='ICO', sizes=ico_sizes)
                print(f"成功将图像保存为ICO: {file_path}")
            except Exception as e:
                print(f"保存ICO文件时出错: {e}")

        # 返回UI界面显示的信息
        return { "ui": { "text": [f"成功导出 {len(image)} 个ICO文件到 {full_output_folder}."] } }