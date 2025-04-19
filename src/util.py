import pygame
import os
import sys

# 确保pygame初始化
if not pygame.get_init():
    pygame.init()

def load_chinese_font(size=24):
    """加载中文字体，尝试多种方法"""
    font = None
    
    # 方法1: 尝试查找系统中所有可用字体
    try:
        all_fonts = pygame.font.get_fonts()
        print(f"发现系统字体数量: {len(all_fonts)}")
    except Exception as e:
        print(f"无法获取系统字体列表: {e}")
        all_fonts = []
    
    # 方法2: 尝试使用系统字体
    # 中文字体优先级列表
    system_fonts = [
        'simhei', 'simsun', 'nsimsun', 'fangsong', 'kaiti', 'microsoftyahei', 
        'microsoftyaheimicrosoftyaheiui', 'dengxian', 'stkaiti', 'stheiti',
        'stxihei', 'stfangsong', 'fzshuti', 'fzyaoti', 'youyuan', 'stliti',
        'arialunicodems', 'msjh', 'msjhbd', 'msgothic', 'malgun', 'gulim'
    ]
    
    # 将所有可用字体转换为小写，用于比较
    all_fonts_lower = [f.lower() for f in all_fonts]
    
    # 直接尝试加载系统字体
    for font_name in system_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试是否能渲染中文
            if test_font_chinese(font):
                print(f"成功加载中文字体: {font_name}")
                return font
        except Exception as e:
            print(f"尝试加载系统字体 {font_name} 失败")
    
    # 尝试模糊匹配中文字体
    for font_name in all_fonts:
        lower_name = font_name.lower()
        if any(keyword in lower_name for keyword in ['sim', 'hei', 'song', 'yuan', 'kai', 'ming', 'han', 'gothic', 'yahei']):
            try:
                font = pygame.font.SysFont(font_name, size)
                if test_font_chinese(font):
                    print(f"成功加载模糊匹配字体: {font_name}")
                    return font
            except:
                continue
    
    # 方法3：尝试加载默认黑体、楷体等非特定名称
    generic_fonts = ["sans", "serif", "monospace"]
    for font_name in generic_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            if test_font_chinese(font):
                print(f"成功加载通用字体: {font_name}")
                return font
        except:
            continue
    
    # 方法4: 使用系统默认字体（可能无法显示中文）
    print("警告: 未找到能显示中文的字体，使用默认字体")
    return pygame.font.Font(None, size)

def test_font_chinese(font):
    """测试字体是否能够渲染中文"""
    try:
        test_text = "测试中文"
        font.render(test_text, True, (255, 255, 255))
        return True
    except:
        return False

def load_ascii_font(size=24):
    """加载用于ASCII字符的字体"""
    # 尝试加载常见的等宽字体，这些字体对ASCII符号的支持较好
    ascii_system_fonts = ['courier', 'couriernew', 'consolas', 'lucidaconsole', 'dejavusansmono', 'monospace']
    
    # 获取系统可用字体
    try:
        all_fonts = pygame.font.get_fonts()
        all_fonts_lower = [f.lower() for f in all_fonts]
    except:
        all_fonts = []
        all_fonts_lower = []
    
    # 尝试完全匹配的等宽字体
    for font_name in ascii_system_fonts:
        if font_name.lower() in all_fonts_lower:
            try:
                font = pygame.font.SysFont(font_name, size)
                return font
            except:
                pass
    
    # 尝试部分匹配的等宽字体
    for font_name in all_fonts:
        lower_name = font_name.lower()
        if any(keyword in lower_name for keyword in ['mono', 'courier', 'console', 'terminal', 'fixed']):
            try:
                font = pygame.font.SysFont(font_name, size)
                return font
            except:
                pass
    
    # 如果找不到合适的等宽字体，使用Pygame默认字体
    print("使用默认ASCII字体")
    return pygame.font.Font(None, size)

# 创建字体缓存字典
font_cache = {}

def get_font(is_ascii=False, size=24):
    """根据需要获取适当的字体，使用缓存避免重复加载"""
    global font_cache
    
    # 创建缓存键
    cache_key = f"{'ascii' if is_ascii else 'chinese'}_{size}"
    
    # 检查缓存中是否已有此字体
    if cache_key not in font_cache:
        if is_ascii:
            font_cache[cache_key] = load_ascii_font(size)
        else:
            font_cache[cache_key] = load_chinese_font(size)
    
    return font_cache[cache_key]

def debug_fonts():
    """打印系统中所有可用字体，用于调试"""
    try:
        fonts = pygame.font.get_fonts()
        print(f"系统字体总数: {len(fonts)}")
        print("系统可用字体列表:")
        for i, font in enumerate(sorted(fonts)):
            print(f"{i+1}. {font}")
    except Exception as e:
        print(f"无法获取系统字体列表: {e}")

# 添加新的函数，用于从fonts目录加载字体
def load_font_from_directory(directory, font_file):
    font_path = os.path.join(directory, font_file)
    if os.path.exists(font_path):
        try:
            font = pygame.font.Font(font_path, 24)
            print(f"加载字体文件: {font_path}")
            return font
        except Exception as e:
            print(f"尝试加载 {font_path} 失败: {e}")
    return None 