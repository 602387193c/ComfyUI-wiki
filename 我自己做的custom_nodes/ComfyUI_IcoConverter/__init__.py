# 从我们的.py文件中导入节点类
from .ico_converter import ImageToIcoConverter

# 这是一个字典，将节点的内部名称映射到它的类
NODE_CLASS_MAPPINGS = {
    "ImageToIcoConverter_dj": ImageToIcoConverter
}

# 这是一个字典，将节点的内部名称映射到它在UI中显示的友好名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToIcoConverter_dj": "Convert to ICO (Win11)"
}

# 告诉Python这个包需要导出哪些变量
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']