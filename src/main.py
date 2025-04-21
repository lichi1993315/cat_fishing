import pygame
import sys
import json
from renderer import ASCIIRenderer
from cat import Cat
from tree_visualizer import TreeVisualizer
from util import get_font, debug_fonts

# Import the behavior tree generation function
from test_claude_tooluse import generate_behavior_tree

class Game:
    def __init__(self):
        # 调整窗口大小以适应行为树可视化
        self.width = 70
        self.height = 24
        self.screen_width = 1280
        self.screen_height = 720
        
        # 保存初始/默认窗口大小
        self.windowed_width = self.screen_width
        self.windowed_height = self.screen_height
        
        # 创建自定义的屏幕
        pygame.init()
        
        # 全屏模式设置 - 默认启用窗口模式以允许用户调整大小
        self.fullscreen = False
        self.screen = self._create_screen()
        pygame.display.set_caption("ASCII Cat Game - 行为树演示")
        
        # 区域划分
        self.update_layout()
        
        # 创建子表面
        self.game_surface = pygame.Surface((self.game_area.width, self.game_area.height))
        self.tree_surface = pygame.Surface((self.tree_area.width, self.tree_area.height))
        self.info_surface = pygame.Surface((self.info_area.width, self.info_area.height))
        
        # 计算渲染器单元格大小
        base_width = 1280
        scale_factor = self.screen_width / base_width
        renderer_cell_size = max(int(19 * scale_factor), 14)
        
        # 创建ASCIIRenderer
        self.renderer = ASCIIRenderer(self.width, self.height, renderer_cell_size)
        self.renderer.screen = self.game_surface  # 指定渲染到游戏区域表面
        
        # 猫和其他游戏元素
        self.cat = Cat(self.width // 2, self.height // 2)
        self.command_buffer = ""
        self.running = True
        self.clock = pygame.time.Clock()
        self.show_help = True
        self.debug_mode = False
        
        # 文本光标相关
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.cursor_blink_rate = 500  # 光标闪烁频率（毫秒）
        
        # 创建行为树可视化器
        self.tree_visualizer = TreeVisualizer(
            self.tree_area.width, 
            self.tree_area.height
        )
        
        # 确保加载可用字体
        self.load_fonts()
        
        # 记录当前活动节点
        self.active_node = None
        
        # 记录被点击的节点和时间
        self.clicked_node = None
        self.clicked_node_time = 0
        self.clicked_node_display_time = 5000  # 显示5秒
        
        # 命令历史记录
        self.command_history = []
        self.max_history = 5
        
        # 界面颜色
        self.colors = {
            'background': (40, 44, 52),
            'panel_bg': (30, 34, 42),
            'panel_border': (70, 80, 90),
            'title': (255, 255, 255),
            'text': (200, 200, 200),
            'highlight': (97, 175, 239),
            'success': (152, 195, 121),
            'running': (229, 192, 123),
            'failure': (224, 108, 117),
            'command': (190, 132, 255)
        }
        
        # 预定义的命令列表
        self.predefined_commands = [
            "default", "sleep", "play", "wander", "explore", "interact", 
            "observe", "debug", "fullscreen", "json"
        ]
        
    def _create_screen(self):
        """创建屏幕（全屏或窗口模式）"""
        if self.fullscreen:
            # 使用当前设备的分辨率创建全屏窗口
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            return pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN
            )
        else:
            # 窗口模式，允许调整窗口大小
            return pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE  # 添加可调整大小标志
            )
            
    def update_layout(self):
        """根据屏幕大小更新布局"""
        # 上半部分放行为树，下半部分放游戏视图和信息
        self.tree_area = pygame.Rect(
            int(self.screen_width * 0.02),
            int(self.screen_height * 0.03),
            int(self.screen_width * 0.96),
            int(self.screen_height * 0.45)
        )
        
        # 游戏视图放在左下角
        self.game_area = pygame.Rect(
            int(self.screen_width * 0.02),
            int(self.screen_height * 0.51),
            int(self.screen_width * 0.63),
            int(self.screen_height * 0.46)
        )
        
        # 信息区域放在右下角
        self.info_area = pygame.Rect(
            int(self.screen_width * 0.67),
            int(self.screen_height * 0.51),
            int(self.screen_width * 0.31),
            int(self.screen_height * 0.46)
        )
        
        # 根据窗口大小调整字体大小
        self._update_font_sizes()
        
    def _update_font_sizes(self):
        """根据窗口大小动态调整字体大小"""
        # 计算基于窗口大小的缩放因子
        base_width = 1280
        base_height = 720
        width_factor = self.screen_width / base_width
        height_factor = self.screen_height / base_height
        scale_factor = min(width_factor, height_factor)
        
        # 设置动态字体大小
        title_size = max(int(26 * scale_factor), 18)
        info_size = max(int(18 * scale_factor), 14)
        chinese_size = max(int(22 * scale_factor), 16)
        
        # 更新字体
        self.title_font = pygame.font.SysFont('Arial', title_size, bold=True)
        self.info_font = pygame.font.SysFont('Arial', info_size)
        
        # 更新中文字体
        try:
            new_chinese_font = get_font(False, chinese_size)
            if self.chinese_support:
                new_chinese_font.render("测试", True, (255, 255, 255))
                self.chinese_font = new_chinese_font
        except:
            pass
        
        # 调整渲染器单元格大小
        if hasattr(self, 'renderer'):
            cell_size = max(int(19 * scale_factor), 14)
            self.renderer.cell_size = cell_size
        
    def handle_resize(self, size):
        """处理窗口大小调整事件"""
        if not self.fullscreen:  # 全屏模式下不处理调整大小
            # 设置最小窗口尺寸，防止窗口过小导致UI问题
            min_width = 800
            min_height = 600
            
            # 确保新尺寸不小于最小限制
            new_width = max(size[0], min_width)
            new_height = max(size[1], min_height)
            
            # 如果尺寸被限制了，重新设置窗口大小
            if new_width != size[0] or new_height != size[1]:
                size = (new_width, new_height)
                self.screen = pygame.display.set_mode(
                    size,
                    pygame.RESIZABLE
                )
            
            self.screen_width, self.screen_height = size
            
            # 保存当前窗口尺寸，用于从全屏切换回窗口时恢复
            self.windowed_width = self.screen_width
            self.windowed_height = self.screen_height
            
            # 更新布局
            self.update_layout()
            
            # 重新创建子表面
            self.game_surface = pygame.Surface((self.game_area.width, self.game_area.height))
            self.tree_surface = pygame.Surface((self.tree_area.width, self.tree_area.height))
            self.info_surface = pygame.Surface((self.info_area.width, self.info_area.height))
            
            # 计算渲染器单元格大小
            base_width = 1280
            scale_factor = self.screen_width / base_width
            cell_size = max(int(19 * scale_factor), 14)
            
            # 重新创建渲染器或更新现有渲染器
            if hasattr(self, 'renderer'):
                # 如果单元格大小变化过大，完全重新创建渲染器，否则只更新属性
                if abs(self.renderer.cell_size - cell_size) > 2:
                    self.renderer = ASCIIRenderer(self.width, self.height, cell_size)
                    self.renderer.screen = self.game_surface
                else:
                    self.renderer.cell_size = cell_size
                    self.renderer.screen = self.game_surface
            
            # 更新行为树可视化器
            self.tree_visualizer.screen_width = self.tree_area.width
            self.tree_visualizer.screen_height = self.tree_area.height
            self.tree_visualizer.needs_recalculation = True
            
    def toggle_fullscreen(self):
        """切换全屏/窗口模式"""
        self.fullscreen = not self.fullscreen
        
        # 保存当前窗口大小以便从全屏切换回窗口时恢复
        if self.fullscreen:
            self.windowed_width = self.screen_width
            self.windowed_height = self.screen_height
        else:
            # 从全屏切换到窗口时，使用合理的窗口尺寸
            self.screen_width = self.windowed_width if hasattr(self, 'windowed_width') else 1280
            self.screen_height = self.windowed_height if hasattr(self, 'windowed_height') else 720
        
        # 重新创建屏幕
        self.screen = self._create_screen()
        
        # 更新布局
        self.update_layout()
        
        # 重新创建子表面
        self.game_surface = pygame.Surface((self.game_area.width, self.game_area.height))
        self.tree_surface = pygame.Surface((self.tree_area.width, self.tree_area.height))
        self.info_surface = pygame.Surface((self.info_area.width, self.info_area.height))
        
        # 更新渲染器屏幕
        self.renderer.screen = self.game_surface
        
        # 更新行为树可视化器
        self.tree_visualizer.screen_width = self.tree_area.width
        self.tree_visualizer.screen_height = self.tree_area.height
        self.tree_visualizer.needs_recalculation = True
        
    def load_fonts(self):
        """加载字体并进行测试"""
        # 打印系统可用字体信息，有助于调试
        debug_fonts()
        
        # 初始化字体大小（会在_update_font_sizes中根据窗口大小动态调整）
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 18)
        
        # 测试中文渲染 - 如果系统找不到合适的中文字体，则使用fallback方案
        chinese_font = get_font(False, 22)  # 初始中文字体大小
        try:
            chinese_font.render("测试中文渲染", True, (255, 255, 255))
            self.chinese_support = True
            self.chinese_font = chinese_font  # 保存中文字体引用
        except:
            print("警告: 中文渲染测试失败，将使用备用方案")
            self.chinese_support = False
            
        # 根据窗口大小更新字体
        self._update_font_sizes()
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 处理窗口大小调整事件
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.size)
                
            elif event.type == pygame.KEYDOWN:
                # 重置光标状态 - 确保在键盘输入时光标立即可见
                self.cursor_visible = True
                self.cursor_blink_time = pygame.time.get_ticks()
                
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Ctrl+R: 重置窗口到默认大小
                    if not self.fullscreen:
                        default_size = (1280, 720)
                        self.screen = pygame.display.set_mode(
                            default_size,
                            pygame.RESIZABLE
                        )
                        self.handle_resize(default_size)
                    
                elif event.key == pygame.K_RETURN:
                    if self.command_buffer:
                        command = self.command_buffer.lower().strip()
                        if command == "debug":
                            self.debug_mode = not self.debug_mode
                        elif command == "fullscreen":
                            # 切换全屏/窗口模式
                            self.toggle_fullscreen()
                        elif command == "json":
                            # 使用新的导出方法生成简化的行为树JSON
                            json_data = self.cat.export_behavior_tree("behavior_tree.json")
                            print("行为树JSON结构:")
                            print(json_data)
                        elif command in self.predefined_commands:
                            # 添加到命令历史
                            self.add_to_history(command)
                            # 修改猫的行为
                            self.cat.modify_behavior(command)
                            # 强制行为树可视化器重新计算布局
                            self.tree_visualizer.needs_recalculation = True
                        else:
                            # 处理自然语言命令
                            self.process_natural_language_command(command)
                            
                        self.command_buffer = ""
                        
                elif event.key == pygame.K_BACKSPACE:
                    self.command_buffer = self.command_buffer[:-1]
                    
                elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                    # 切换全屏/窗口模式
                    self.toggle_fullscreen()
                    
                else:
                    if len(self.command_buffer) < 20:  # Limit command length
                        self.command_buffer += event.unicode
            
            # 处理鼠标点击事件            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_x, mouse_y = event.pos
                    
                    # 检查是否点击在行为树区域内
                    if self.tree_area.collidepoint(mouse_x, mouse_y):
                        # 转换为行为树表面的坐标
                        tree_x = mouse_x - self.tree_area.x
                        tree_y = mouse_y - self.tree_area.y
                        
                        # 处理点击事件
                        clicked_node = self.tree_visualizer.handle_click(
                            tree_x, tree_y, self.cat.root, self.cat)
                        
                        if clicked_node:
                            print(f"点击了节点: {clicked_node.name}")
                            
                            # 在信息区域显示点击的节点信息
                            self.clicked_node = clicked_node
                            self.clicked_node_time = pygame.time.get_ticks()  # 记录点击时间，用于临时显示
    
    def process_natural_language_command(self, command):
        """处理自然语言命令，生成行为树"""
        self.add_to_history(command)
        
        print(f"处理自然语言命令: {command}")
        
        try:
            # 使用Claude生成行为树JSON
            behavior_tree_json = generate_behavior_tree(command)
            
            if behavior_tree_json:
                print("生成的行为树JSON:")
                print(behavior_tree_json)
                
                # 将JSON字符串转换为Python对象
                tree_data = json.loads(behavior_tree_json)
                
                # 从behavior_tree.json格式提取structure部分
                if "structure" in tree_data:
                    # 保存为临时文件并应用
                    with open("behavior_tree_temp.json", "w", encoding="utf-8") as f:
                        json.dump(tree_data["structure"], f, ensure_ascii=False, indent=2)
                    
                    # 使用猫的方法加载这个行为树
                    self.cat.load_behavior_tree("behavior_tree_temp.json")
                    
                    # 强制行为树可视化器重新计算布局
                    self.tree_visualizer.needs_recalculation = True
                    
                    print("成功应用新的行为树")
                else:
                    print("生成的JSON格式不正确，缺少structure字段")
            else:
                print("无法生成行为树JSON")
                
        except Exception as e:
            print(f"处理自然语言命令时出错: {e}")
    
    def add_to_history(self, command):
        """添加命令到历史记录"""
        if command in self.command_history:
            self.command_history.remove(command)
        self.command_history.insert(0, command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop()
                        
    def update(self):
        # 更新猫的行为
        self.cat.update()
        
        # 更新活动节点（用于行为树可视化）
        active_nodes = self.tree_visualizer.find_active_nodes(self.cat.root)
        
        # 特殊处理：检查特定状态并确保对应节点被标记为活动
        if self.cat.state == "sleeping" and hasattr(self.cat, 'sleep_node'):
            # 确保sleep_node在活动节点列表中
            if self.cat.sleep_node not in active_nodes:
                active_nodes.append(self.cat.sleep_node)
        
        # 同样处理其他核心行为
        if self.cat.state == "playing" and hasattr(self.cat, 'play_node'):
            if self.cat.play_node not in active_nodes:
                active_nodes.append(self.cat.play_node)
                
        if self.cat.state == "wandering" and hasattr(self.cat, 'wander_node'):
            if self.cat.wander_node not in active_nodes:
                active_nodes.append(self.cat.wander_node)
        
        # 设置活动节点
        self.active_node = active_nodes[0] if active_nodes else None
        
        # 更新光标闪烁
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_blink_time > self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = current_time
        
    def render(self):
        # 清除主屏幕
        self.screen.fill(self.colors['background'])
        
        # 清除各子表面
        self.game_surface.fill(self.colors['panel_bg'])
        self.tree_surface.fill(self.colors['panel_bg'])
        self.info_surface.fill(self.colors['panel_bg'])
        
        # 绘制行为树区域 (先渲染行为树，因为它在上方)
        self.render_tree_view()
        
        # 绘制游戏区域
        self.render_game_view()
        
        # 绘制信息区域
        self.render_info_view()
        
        # 将子表面绘制到主屏幕上
        self.screen.blit(self.tree_surface, self.tree_area)
        self.screen.blit(self.game_surface, self.game_area)
        self.screen.blit(self.info_surface, self.info_area)
        
        # 绘制区域边框和标题
        self.draw_panel(self.tree_area, "行为树可视化 (上方)")
        self.draw_panel(self.game_area, "游戏视图 (左下)")
        self.draw_panel(self.info_area, "状态与信息 (右下)")
        
        # 更新屏幕
        pygame.display.flip()
    
    def draw_panel(self, rect, title):
        """绘制面板边框和标题"""
        # 绘制边框
        pygame.draw.rect(self.screen, self.colors['panel_border'], rect, 2, border_radius=3)
        
        # 根据中文支持情况选择如何渲染标题
        if self.chinese_support:
            # 绘制标题背景
            title_rect = pygame.Rect(rect.x + 10, rect.y - 15, len(title) * 14 + 20, 30)
            pygame.draw.rect(self.screen, self.colors['panel_bg'], title_rect, border_radius=3)
            pygame.draw.rect(self.screen, self.colors['panel_border'], title_rect, 2, border_radius=3)
            
            # 使用中文字体渲染标题
            try:
                title_font = get_font(False, 20)
                title_text = title_font.render(title, True, self.colors['title'])
                self.screen.blit(title_text, (rect.x + 20, rect.y - 10))
            except:
                # 备选方案：使用默认字体
                title_text = self.title_font.render(title, True, self.colors['title'])
                self.screen.blit(title_text, (rect.x + 20, rect.y - 10))
        else:
            # 使用ASCII字体
            title_rect = pygame.Rect(rect.x + 10, rect.y - 15, len(title) * 12 + 20, 30)
            pygame.draw.rect(self.screen, self.colors['panel_bg'], title_rect, border_radius=3)
            pygame.draw.rect(self.screen, self.colors['panel_border'], title_rect, 2, border_radius=3)
            title_text = self.title_font.render(title, True, self.colors['title'])
            self.screen.blit(title_text, (rect.x + 20, rect.y - 10))
    
    def render_game_view(self):
        """渲染游戏视图"""
        # 清除渲染器屏幕
        self.renderer.clear()
        
        # 绘制猫
        cat_char = self.cat.get_display_char()
        self.renderer.draw_char(self.cat.x, self.cat.y, cat_char, self.get_state_color())
        
        # 创建明显的命令输入区域
        input_y = self.height - 10
        
        # 绘制命令输入框边框 - 使用双线边框增强可见性
        border_color = (130, 180, 255)  # 更亮的蓝色边框
        for x in range(self.width):
            self.renderer.draw_char(x, input_y - 1, "═", border_color)  # 上边框，使用双线
            self.renderer.draw_char(x, input_y + 1, "═", border_color)  # 下边框，使用双线
        self.renderer.draw_char(0, input_y - 1, "╔", border_color)
        self.renderer.draw_char(0, input_y, "║", border_color)
        self.renderer.draw_char(0, input_y + 1, "╚", border_color)
        self.renderer.draw_char(self.width - 1, input_y - 1, "╗", border_color)
        self.renderer.draw_char(self.width - 1, input_y, "║", border_color)
        self.renderer.draw_char(self.width - 1, input_y + 1, "╝", border_color)
        
        # 清空输入区背景并用点填充来突出显示输入区
        bg_color = (120, 120, 160)  # 使用灰紫色作为输入区指示
        for x in range(1, self.width - 1):
            if x % 2 == 0:  # 每隔一个字符画一个点，形成点状背景
                self.renderer.draw_char(x, input_y, "·", bg_color)
            else:
                self.renderer.draw_char(x, input_y, " ", bg_color)
        
        # 绘制命令行提示符和文本
        input_prefix = "输入命令 ➤ " if self.chinese_support else "Command ➤ "  # 使用箭头增强可见性
        text_color = (255, 255, 255)  # 使用白色文字提高可读性
        self.renderer.draw_text(2, input_y, f"{input_prefix}{self.command_buffer}", text_color)
        
        # 绘制光标
        if self.cursor_visible:
            # 计算光标位置：前缀长度 + 当前输入文本长度 + 2（边距）
            prefix_len = len(input_prefix)
            cursor_pos = 2 + prefix_len + len(self.command_buffer)
            # 绘制闪烁的光标
            cursor_color = (255, 255, 0)  # 明亮的黄色光标
            self.renderer.draw_char(cursor_pos, input_y, "█", cursor_color)
            
        # 绘制命令历史标题
        history_title = "最近命令:" if self.chinese_support else "Recent commands:"
        title_color = (190, 132, 255)  # 使用紫色突出显示标题
        self.renderer.draw_text(2, input_y - 3, history_title, title_color)
        
        # 绘制命令历史
        history_color = (180, 180, 200)
        for i, cmd in enumerate(self.command_history[:3]):
            line = f"[{i+1}] {cmd}"
            self.renderer.draw_text(2, input_y - 5 + i, line, history_color)
        
        # 更新渲染器
        self.renderer.update()
        
    def render_tree_view(self):
        """渲染行为树可视化"""
        # 使用树可视化器渲染行为树
        self.tree_visualizer.render(self.tree_surface, self.cat.root, self.active_node)
        
    def render_info_view(self):
        """渲染信息区域"""
        y_offset = 20
        line_height = 25
        
        # 检查中文渲染支持
        if self.chinese_support:
            # 使用中文字体
            chinese_font = get_font(False, 18)
            
            try:
                # 渲染猫的状态信息
                status_text = f"猫的状态: {self.cat.state}"
                status_surface = chinese_font.render(status_text, True, self.get_state_color())
                self.info_surface.blit(status_surface, (20, y_offset))
                y_offset += line_height
                
                # 渲染位置信息
                position_text = f"位置: ({self.cat.x}, {self.cat.y})"
                position_surface = chinese_font.render(position_text, True, self.colors['text'])
                self.info_surface.blit(position_surface, (20, y_offset))
                y_offset += line_height
                
                # 渲染行为树信息
                tree_info_text = f"行为树根节点: {self.cat.root.name}"
                tree_info_surface = chinese_font.render(tree_info_text, True, self.colors['highlight'])
                self.info_surface.blit(tree_info_surface, (20, y_offset))
                y_offset += line_height
                
                # 如果有活动节点，显示活动节点信息
                if self.active_node:
                    active_text = f"当前活动节点: {self.active_node.name}"
                    active_surface = chinese_font.render(active_text, True, self.colors['success'])
                    self.info_surface.blit(active_surface, (20, y_offset))
                    y_offset += line_height
                
                # 如果有被点击的节点且在显示时间内，显示节点信息
                current_time = pygame.time.get_ticks()
                if self.clicked_node and (current_time - self.clicked_node_time < self.clicked_node_display_time):
                    # 显示点击节点信息
                    clicked_text = f"点击节点: {self.clicked_node.name}"
                    clicked_surface = chinese_font.render(clicked_text, True, self.colors['command'])
                    self.info_surface.blit(clicked_surface, (20, y_offset))
                    y_offset += line_height
                    
                    # 显示节点类型
                    node_type = self.clicked_node.__class__.__name__
                    type_text = f"节点类型: {node_type}"
                    type_surface = chinese_font.render(type_text, True, self.colors['command'])
                    self.info_surface.blit(type_surface, (20, y_offset))
                    y_offset += line_height
                    
                    # 如果是复合节点，显示子节点数量
                    if hasattr(self.clicked_node, 'children') and self.clicked_node.children:
                        children_text = f"子节点数量: {len(self.clicked_node.children)}"
                        children_surface = chinese_font.render(children_text, True, self.colors['command'])
                        self.info_surface.blit(children_surface, (20, y_offset))
                        y_offset += line_height
                
                # 显示行为倾向
                y_offset += 10
                behavior_title = chinese_font.render("行为倾向:", True, self.colors['highlight'])
                self.info_surface.blit(behavior_title, (20, y_offset))
                y_offset += line_height
                
                # 显示各行为权重
                for behavior, weight in sorted(self.cat.behavior_weights.items(), key=lambda x: x[1], reverse=True):
                    # 计算权重条长度
                    bar_length = int(weight * 100)
                    bar_width = min(bar_length, 200)  # 限制最大长度
                    
                    # 显示行为名称和权重
                    behavior_text = f"{behavior}: {weight:.1f}"
                    behavior_surface = chinese_font.render(behavior_text, True, self.colors['text'])
                    self.info_surface.blit(behavior_surface, (20, y_offset))
                    
                    # 绘制权重条
                    bar_color = self.get_behavior_color(behavior)
                    pygame.draw.rect(self.info_surface, bar_color, 
                                    (150, y_offset + 5, bar_width, 10))
                    
                    y_offset += line_height
                
                # 添加窗口调整提示
                resize_help = chinese_font.render("✓ 可以自由调整窗口大小", True, self.colors['success'])
                self.info_surface.blit(resize_help, (20, y_offset + 290))
                
                # 添加快捷键提示
                shortcut_help = chinese_font.render("Ctrl+R: 重置窗口大小", True, self.colors['text'])
                self.info_surface.blit(shortcut_help, (20, y_offset + 315))
                
                fullscreen_help = chinese_font.render("F11/F: 切换全屏模式", True, self.colors['text'])
                self.info_surface.blit(fullscreen_help, (20, y_offset + 340))
                
            except Exception as e:
                print(f"中文渲染错误: {e}")
                # 如果中文渲染失败，回退到备选方案
                self.chinese_support = False
                return self.render_info_view()  # 重新尝试渲染
                
        else:
            # 使用默认英文字体（备选方案）
            # 渲染猫的状态信息
            status_text = f"Cat State: {self.cat.state}"
            status_surface = self.info_font.render(status_text, True, self.get_state_color())
            self.info_surface.blit(status_surface, (20, y_offset))
            y_offset += line_height
            
            # 渲染位置信息
            position_text = f"Position: ({self.cat.x}, {self.cat.y})"
            position_surface = self.info_font.render(position_text, True, self.colors['text'])
            self.info_surface.blit(position_surface, (20, y_offset))
            y_offset += line_height
            
            # 渲染行为树信息
            tree_info_text = f"Root Node: {self.cat.root.name}"
            tree_info_surface = self.info_font.render(tree_info_text, True, self.colors['highlight'])
            self.info_surface.blit(tree_info_surface, (20, y_offset))
            y_offset += line_height
            
            # 如果有活动节点，显示活动节点信息
            if self.active_node:
                active_text = f"Active Node: {self.active_node.name}"
                active_surface = self.info_font.render(active_text, True, self.colors['success'])
                self.info_surface.blit(active_surface, (20, y_offset))
                y_offset += line_height
            
            # 如果有被点击的节点且在显示时间内，显示节点信息
            current_time = pygame.time.get_ticks()
            if self.clicked_node and (current_time - self.clicked_node_time < self.clicked_node_display_time):
                # 显示点击节点信息
                clicked_text = f"Clicked Node: {self.clicked_node.name}"
                clicked_surface = self.info_font.render(clicked_text, True, self.colors['command'])
                self.info_surface.blit(clicked_surface, (20, y_offset))
                y_offset += line_height
                
                # 显示节点类型
                node_type = self.clicked_node.__class__.__name__
                type_text = f"Node Type: {node_type}"
                type_surface = self.info_font.render(type_text, True, self.colors['command'])
                self.info_surface.blit(type_surface, (20, y_offset))
                y_offset += line_height
                
                # 如果是复合节点，显示子节点数量
                if hasattr(self.clicked_node, 'children') and self.clicked_node.children:
                    children_text = f"Children Count: {len(self.clicked_node.children)}"
                    children_surface = self.info_font.render(children_text, True, self.colors['command'])
                    self.info_surface.blit(children_surface, (20, y_offset))
                    y_offset += line_height
                
            # 显示行为倾向
            y_offset += 10
            behavior_title = self.info_font.render("Behavior Weights:", True, self.colors['highlight'])
            self.info_surface.blit(behavior_title, (20, y_offset))
            y_offset += line_height
            
            # 显示各行为权重
            for behavior, weight in sorted(self.cat.behavior_weights.items(), key=lambda x: x[1], reverse=True):
                # 计算权重条长度
                bar_length = int(weight * 100)
                bar_width = min(bar_length, 200)  # 限制最大长度
                
                # 显示行为名称和权重
                behavior_text = f"{behavior}: {weight:.1f}"
                behavior_surface = self.info_font.render(behavior_text, True, self.colors['text'])
                self.info_surface.blit(behavior_surface, (20, y_offset))
                
                # 绘制权重条
                bar_color = self.get_behavior_color(behavior)
                pygame.draw.rect(self.info_surface, bar_color, 
                                (150, y_offset + 5, bar_width, 10))
                
                y_offset += line_height
        
        # 添加命令列表
        self.render_command_list()
            
    def render_command_list(self):
        """渲染命令列表"""
        # 在右侧渲染命令列表
        x_offset = 350
        y_offset = 20
        
        # 渲染命令帮助
        if self.chinese_support:
            try:
                chinese_font = get_font(False, 18)
                help_title = chinese_font.render("可用命令:", True, self.colors['highlight'])
                self.info_surface.blit(help_title, (x_offset, y_offset))
                
                # 添加自然语言说明
                nl_help = chinese_font.render("也可以直接输入自然语言描述:", True, self.colors['success'])
                self.info_surface.blit(nl_help, (x_offset, y_offset + 240))
                
                nl_example = chinese_font.render("例如: 一只饥饿的猫，会寻找食物", True, self.colors['text'])
                self.info_surface.blit(nl_example, (x_offset, y_offset + 265))
                
                # 添加窗口调整提示
                resize_help = chinese_font.render("✓ 可以自由调整窗口大小", True, self.colors['success'])
                self.info_surface.blit(resize_help, (x_offset, y_offset + 290))
                
                # 添加快捷键提示
                shortcut_help = chinese_font.render("Ctrl+R: 重置窗口大小", True, self.colors['text'])
                self.info_surface.blit(shortcut_help, (x_offset, y_offset + 315))
                
                fullscreen_help = chinese_font.render("F11/F: 切换全屏模式", True, self.colors['text'])
                self.info_surface.blit(fullscreen_help, (x_offset, y_offset + 340))
                
            except:
                help_title = self.info_font.render("Commands:", True, self.colors['highlight'])
                self.info_surface.blit(help_title, (x_offset, y_offset))
                
                # 添加自然语言说明（英文）
                nl_help = self.info_font.render("Or type natural language:", True, self.colors['success'])
                self.info_surface.blit(nl_help, (x_offset, y_offset + 240))
                
                nl_example = self.info_font.render("Example: A hungry cat looking for food", True, self.colors['text'])
                self.info_surface.blit(nl_example, (x_offset, y_offset + 265))
                
                # 添加窗口调整提示（英文）
                resize_help = self.info_font.render("✓ Window is freely resizable", True, self.colors['success'])
                self.info_surface.blit(resize_help, (x_offset, y_offset + 290))
                
                # 添加快捷键提示（英文）
                shortcut_help = self.info_font.render("Ctrl+R: Reset window size", True, self.colors['text'])
                self.info_surface.blit(shortcut_help, (x_offset, y_offset + 315))
                
                fullscreen_help = self.info_font.render("F11/F: Toggle fullscreen", True, self.colors['text'])
                self.info_surface.blit(fullscreen_help, (x_offset, y_offset + 340))
        else:
            help_title = self.info_font.render("Commands:", True, self.colors['highlight'])
            self.info_surface.blit(help_title, (x_offset, y_offset))
            
            # 添加自然语言说明（英文）
            nl_help = self.info_font.render("Or type natural language:", True, self.colors['success'])
            self.info_surface.blit(nl_help, (x_offset, y_offset + 240))
            
            nl_example = self.info_font.render("Example: A hungry cat looking for food", True, self.colors['text'])
            self.info_surface.blit(nl_example, (x_offset, y_offset + 265))
            
            # 添加窗口调整提示（英文）
            resize_help = self.info_font.render("✓ Window is freely resizable", True, self.colors['success'])
            self.info_surface.blit(resize_help, (x_offset, y_offset + 290))
            
            # 添加快捷键提示（英文）
            shortcut_help = self.info_font.render("Ctrl+R: Reset window size", True, self.colors['text'])
            self.info_surface.blit(shortcut_help, (x_offset, y_offset + 315))
            
            fullscreen_help = self.info_font.render("F11/F: Toggle fullscreen", True, self.colors['text'])
            self.info_surface.blit(fullscreen_help, (x_offset, y_offset + 340))
            
        y_offset += 25
        
        # 命令列表
        commands = [
            ("default", "重置为默认行为树" if self.chinese_support else "Reset to default"),
            ("sleep", "睡觉" if self.chinese_support else "Sleep"), 
            ("play", "玩耍" if self.chinese_support else "Play"),
            ("wander", "游荡" if self.chinese_support else "Wander"),
            ("explore", "探索" if self.chinese_support else "Explore"),
            ("interact", "互动" if self.chinese_support else "Interact"),
            ("observe", "观察" if self.chinese_support else "Observe"),
            ("debug", "切换调试模式" if self.chinese_support else "Toggle debug"),
            ("fullscreen", "切换全屏模式" if self.chinese_support else "Toggle fullscreen"),
            ("json", "保存行为树JSON结构" if self.chinese_support else "Save behavior tree JSON")
        ]
        
        line_height = 18
        for i, (cmd, desc) in enumerate(commands):
            cmd_text = f"{cmd}: {desc}"
            color = self.colors['command']
            
            # 如果命令在历史记录中，使用高亮颜色
            if cmd in self.command_history:
                color = self.colors['success']
            
            if self.chinese_support:
                try:
                    chinese_font = get_font(False, 16)
                    cmd_surface = chinese_font.render(cmd_text, True, color)
                    self.info_surface.blit(cmd_surface, (x_offset, y_offset + i * line_height))
                except:
                    cmd_surface = self.info_font.render(cmd_text, True, color)
                    self.info_surface.blit(cmd_surface, (x_offset, y_offset + i * line_height))
            else:
                cmd_surface = self.info_font.render(cmd_text, True, color)
                self.info_surface.blit(cmd_surface, (x_offset, y_offset + i * line_height))
    
    def get_behavior_color(self, behavior):
        """获取特定行为对应的颜色"""
        colors = {
            "sleep": (160, 160, 255),  # 蓝色
            "play": (255, 255, 0),     # 黄色
            "wander": (0, 255, 0),     # 绿色
            "explore": (255, 128, 0),  # 橙色
            "observe": (255, 165, 0),  # 橙色
            "interact": (255, 0, 0)    # 红色
        }
        return colors.get(behavior, (200, 200, 200))
    
    def get_state_color(self):
        """根据猫的状态返回对应的颜色"""
        if self.cat.state == "sleeping":
            return (160, 160, 255)  # 蓝色
        elif self.cat.state == "playing":
            return (255, 255, 0)    # 黄色
        elif self.cat.state == "wandering":
            return (0, 255, 0)      # 绿色
        elif self.cat.state == "observing":
            return (255, 165, 0)    # 橙色
        elif self.cat.state == "waiting":
            return (200, 200, 200)  # 淡灰色
        elif self.cat.state == "moving":
            return (255, 0, 255)    # 紫色
        elif self.cat.state == "interacting":
            return (255, 0, 0)      # 红色
        elif self.cat.state == "observing_wait":
            return (0, 255, 255)    # 青色
        elif self.cat.state == "exploring":
            return (255, 128, 0)    # 橙红色
        return (255, 255, 255)      # 白色
        
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(30)
            
        pygame.quit()
        
if __name__ == "__main__":
    game = Game()
    game.run() 