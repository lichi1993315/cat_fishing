import pygame
from util import get_font

class ASCIIRenderer:
    def __init__(self, width, height, cell_size=20):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen_width = width * cell_size
        self.screen_height = height * cell_size
        
        # 确保pygame已初始化
        if not pygame.get_init():
            pygame.init()
            
        # 默认情况下创建自己的屏幕，但可以被外部替换
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        
        # 字体大小设置 - 适当调整以适应不同的字符
        self.ascii_font_size = cell_size
        self.chinese_font_size = int(cell_size * 0.9)  # 中文字体略小以适应单元格
        
        # 预加载常用字体以避免渲染时延迟
        self._preload_fonts()
        
    def _preload_fonts(self):
        """预加载常用字体"""
        get_font(True, self.ascii_font_size)  # 预加载ASCII字体
        get_font(False, self.chinese_font_size)  # 预加载中文字体
        
    def clear(self):
        self.screen.fill((0, 0, 0))
        
    def draw_char(self, x, y, char, color=(255, 255, 255)):
        # 检查坐标是否在范围内
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
            
        # 判断是ASCII字符还是中文字符
        is_ascii = ord(char) < 128
        
        # 获取适当的字体
        try:
            font = get_font(is_ascii, 
                         self.ascii_font_size if is_ascii else self.chinese_font_size)
            
            # 渲染文本
            text = font.render(char, True, color)
            
            # 计算文本位置以居中显示在单元格中
            text_rect = text.get_rect()
            cell_x = x * self.cell_size
            cell_y = y * self.cell_size
            
            # ASCII字符居中显示
            if is_ascii:
                pos_x = cell_x + (self.cell_size - text_rect.width) // 2
                pos_y = cell_y + (self.cell_size - text_rect.height) // 2
            # 中文字符可能需要调整
            else:
                pos_x = cell_x
                pos_y = cell_y + (self.cell_size - text_rect.height) // 2
                
            self.screen.blit(text, (pos_x, pos_y))
        except Exception as e:
            # 如果渲染失败，使用备用方案（简单矩形）
            print(f"字符渲染错误: {e}")
            pygame.draw.rect(self.screen, color, 
                            (x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size), 1)
        
    def draw_text(self, x, y, text, color=(255, 255, 255)):
        pos_x = x
        for i, char in enumerate(text):
            # 中文字符占用两个ASCII字符的宽度
            if ord(char) > 127:
                char_width = 2  # 中文字符宽度是ASCII的两倍
            else:
                char_width = 1
                
            if pos_x < self.width:  # 确保不超出屏幕范围
                self.draw_char(pos_x, y, char, color)
            pos_x += char_width
    
    def draw_multiline_text(self, x, y, text_lines, color=(255, 255, 255)):
        """绘制多行文本，每行可以是字符串"""
        for i, line in enumerate(text_lines):
            if y + i < self.height:  # 确保不超出屏幕范围
                self.draw_text(x, y + i, line, color)
            
    def update(self):
        """更新屏幕，如果使用外部Surface则不需要刷新显示"""
        pass
        
    def cleanup(self):
        """清理资源，对于共享的屏幕不进行退出"""
        pass 