import pygame
import sys
from renderer import ASCIIRenderer
from cat import Cat
from tree_visualizer import TreeVisualizer
from util import get_font, debug_fonts

class Game:
    def __init__(self):
        # 调整窗口大小以适应行为树可视化
        self.width = 80
        self.height = 24
        self.screen_width = 1280
        self.screen_height = 720
        
        # 创建自定义的屏幕
        pygame.init()
        
        # 全屏模式设置
        self.fullscreen = True  # 默认启用全屏
        self.screen = self._create_screen()
        pygame.display.set_caption("ASCII Cat Game - 行为树演示")
        
        # 区域划分
        self.update_layout()
        
        # 创建子表面
        self.game_surface = pygame.Surface((self.game_area.width, self.game_area.height))
        self.tree_surface = pygame.Surface((self.tree_area.width, self.tree_area.height))
        self.info_surface = pygame.Surface((self.info_area.width, self.info_area.height))
        
        # 调整ASCIIRenderer创建方式
        renderer_cell_size = 16  # 减小字符大小以适应新布局
        self.renderer = ASCIIRenderer(self.width, self.height, renderer_cell_size)
        self.renderer.screen = self.game_surface  # 指定渲染到游戏区域表面
        
        # 猫和其他游戏元素
        self.cat = Cat(self.width // 2, self.height // 2)
        self.command_buffer = ""
        self.running = True
        self.clock = pygame.time.Clock()
        self.show_help = True
        self.debug_mode = False
        
        # 创建行为树可视化器
        self.tree_visualizer = TreeVisualizer(
            self.tree_area.width, 
            self.tree_area.height
        )
        
        # 确保加载可用字体
        self.load_fonts()
        
        # 记录当前活动节点
        self.active_node = None
        
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
            # 窗口模式
            return pygame.display.set_mode((self.screen_width, self.screen_height))
            
    def update_layout(self):
        """根据屏幕大小更新布局"""
        # 根据屏幕大小计算比例
        self.game_area = pygame.Rect(
            int(self.screen_width * 0.02),
            int(self.screen_height * 0.03), 
            int(self.screen_width * 0.5), 
            int(self.screen_height * 0.65)
        )
        
        self.tree_area = pygame.Rect(
            int(self.screen_width * 0.54),
            int(self.screen_height * 0.03),
            int(self.screen_width * 0.44),
            int(self.screen_height * 0.94)
        )
        
        self.info_area = pygame.Rect(
            int(self.screen_width * 0.02),
            int(self.screen_height * 0.7),
            int(self.screen_width * 0.5),
            int(self.screen_height * 0.27)
        )
        
    def toggle_fullscreen(self):
        """切换全屏/窗口模式"""
        self.fullscreen = not self.fullscreen
        
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
        
        # 字体大小设置
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 18)
        
        # 测试中文渲染 - 如果系统找不到合适的中文字体，则使用fallback方案
        chinese_font = get_font(False, 20)
        try:
            chinese_font.render("测试中文渲染", True, (255, 255, 255))
            self.chinese_support = True
        except:
            print("警告: 中文渲染测试失败，将使用备用方案")
            self.chinese_support = False
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                elif event.key == pygame.K_RETURN:
                    if self.command_buffer:
                        command = self.command_buffer.lower().strip()
                        if command == "debug":
                            self.debug_mode = not self.debug_mode
                        elif command == "fullscreen":
                            # 切换全屏/窗口模式
                            self.toggle_fullscreen()
                        else:
                            # 添加到命令历史
                            self.add_to_history(command)
                            # 修改猫的行为
                            self.cat.modify_behavior(command)
                            # 强制行为树可视化器重新计算布局
                            self.tree_visualizer.needs_recalculation = True
                        self.command_buffer = ""
                        
                elif event.key == pygame.K_BACKSPACE:
                    self.command_buffer = self.command_buffer[:-1]
                    
                elif event.key == pygame.K_h:
                    # 切换帮助显示
                    self.show_help = not self.show_help
                
                elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                    # 切换全屏/窗口模式
                    self.toggle_fullscreen()
                    
                else:
                    if len(self.command_buffer) < 20:  # Limit command length
                        self.command_buffer += event.unicode
    
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
        
    def render(self):
        # 清除主屏幕
        self.screen.fill(self.colors['background'])
        
        # 清除各子表面
        self.game_surface.fill(self.colors['panel_bg'])
        self.tree_surface.fill(self.colors['panel_bg'])
        self.info_surface.fill(self.colors['panel_bg'])
        
        # 绘制游戏区域
        self.render_game_view()
        
        # 绘制行为树区域
        self.render_tree_view()
        
        # 绘制信息区域
        self.render_info_view()
        
        # 将子表面绘制到主屏幕上
        self.screen.blit(self.game_surface, self.game_area)
        self.screen.blit(self.tree_surface, self.tree_area)
        self.screen.blit(self.info_surface, self.info_area)
        
        # 绘制区域边框和标题
        self.draw_panel(self.game_area, "游戏视图")
        self.draw_panel(self.tree_area, "行为树可视化")
        self.draw_panel(self.info_area, "状态与信息")
        
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
        
        # 绘制命令行
        self.renderer.draw_text(0, self.height - 2, f"> {self.command_buffer}")
        
        # 绘制命令历史
        for i, cmd in enumerate(self.command_history[:3]):
            line = f"[{i+1}] {cmd}"
            self.renderer.draw_text(0, self.height - 5 + i, line, (150, 150, 150))
        
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
            except:
                help_title = self.info_font.render("Commands:", True, self.colors['highlight'])
                self.info_surface.blit(help_title, (x_offset, y_offset))
        else:
            help_title = self.info_font.render("Commands:", True, self.colors['highlight'])
            self.info_surface.blit(help_title, (x_offset, y_offset))
            
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
            ("fullscreen", "切换全屏模式" if self.chinese_support else "Toggle fullscreen")
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