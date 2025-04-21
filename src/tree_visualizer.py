import pygame
from behavior_tree.node import NodeStatus
from util import get_font

class TreeVisualizer:
    """行为树可视化器，用于在游戏中展示行为树结构"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.node_width = 160  # 减小基础节点宽度
        self.node_height = 36  # 减小节点高度
        self.horizontal_spacing = 40  # 减小水平间距
        self.vertical_spacing = 70  # 减小垂直间距
        self.scale_factor = 1.0  # 添加缩放因子
        
        # 测试中文字体支持
        self.init_fonts()
        
        # 样式和颜色
        self.colors = {
            'background': (30, 30, 40),  # 稍微调整背景色，使其更暗一点
            'node': (70, 70, 80),  # 深灰色节点背景
            'sequence': (80, 160, 80),  # 绿色序列节点
            'selector': (160, 80, 80),  # 红色选择器节点
            'active': (100, 200, 100),  # 明亮的绿色活动节点
            'inactive': (70, 70, 80),  # 深灰色非活动节点
            'running': (100, 190, 100),  # 绿色运行状态
            'success': (100, 200, 100),  # 绿色成功状态
            'failure': (200, 80, 80),  # 红色失败状态
            'connection': (200, 200, 200),  # 亮灰色连接线
            'text': (240, 240, 240)  # 更亮的白色文字，增加对比度
        }
        
        # 初始化变量
        self.needs_recalculation = True
        self.last_tree_hash = None
        
    def init_fonts(self):
        """初始化字体并测试中文支持"""
        self.font_size = 14  # 减小字体大小以适应更多文本
        
        # 尝试加载中文字体
        try:
            chinese_font = get_font(False, self.font_size)
            # 测试渲染中文字符
            test_surface = chinese_font.render("测试", True, (255, 255, 255))
            # 检查渲染后的表面是否有效
            if test_surface.get_width() > 0:
                self.chinese_support = True
                self.font = chinese_font
                print("成功加载中文字体用于行为树可视化")
            else:
                raise Exception("中文渲染测试失败")
        except Exception as e:
            # 如果中文字体测试失败，使用ASCII字体
            self.chinese_support = False
            self.font = pygame.font.SysFont('Arial', self.font_size)
            print(f"行为树可视化器中文支持失败: {e}")
            
        print(f"行为树可视化器中文支持: {self.chinese_support}")
        
        # 确保树结构信息字体也使用中文字体
        if self.chinese_support:
            self.info_font = self.font
        else:
            self.info_font = pygame.font.SysFont('Arial', 14)
    
    def tree_hash(self, root_node):
        """计算行为树的哈希值，用于检测变化"""
        if not root_node:
            return 0
            
        result = hash(root_node.__class__.__name__ + root_node.name)
        
        if hasattr(root_node, 'children') and root_node.children:
            for child in root_node.children:
                result ^= self.tree_hash(child)
                
        return result
        
    def calculate_layout(self, root_node):
        """计算行为树节点的位置和大小"""
        self.nodes_info = {}
        
        # 执行递归布局算法
        self._calculate_subtree_width(root_node)
        available_width = self.screen_width
        self._assign_positions(root_node, 0, available_width, 0)
        
        # 计算树的总高度和宽度
        max_width = 0
        max_height = 0
        for info in self.nodes_info.values():
            max_width = max(max_width, info['x'] + info['width'])
            max_height = max(max_height, info['y'] + info['height'])
            
        # 计算缩放因子，确保树完全适应屏幕
        # 留出小边距以避免贴边显示
        width_scale = (self.screen_width - 20) / max(max_width, 1)
        height_scale = (self.screen_height - 40) / max(max_height, 1)
        
        # 使用较小的缩放因子，确保在两个维度上都适应
        self.scale_factor = min(width_scale, height_scale, 1.0)  # 不超过1.0以避免过大
        
        # 如果缩放因子小于1，应用缩放
        if self.scale_factor < 1.0:
            self._apply_scaling()
        
        # 计算树哈希值，用于检测变化
        self.last_tree_hash = self.tree_hash(root_node)
        self.needs_recalculation = False
        
        return self.nodes_info
        
    def _apply_scaling(self):
        """应用缩放因子到所有节点"""
        for node, info in self.nodes_info.items():
            # 缩放节点位置和大小
            info['x'] = int(info['x'] * self.scale_factor)
            info['y'] = int(info['y'] * self.scale_factor)
            info['width'] = int(info['width'] * self.scale_factor)
            info['height'] = int(info['height'] * self.scale_factor)
            info['center_x'] = int(info['center_x'] * self.scale_factor)
            info['center_y'] = int(info['center_y'] * self.scale_factor)
        
    def _calculate_subtree_width(self, node):
        """计算节点及其子树的宽度"""
        if not hasattr(node, 'children') or not node.children:
            # 叶子节点宽度
            min_width = self.node_width + self.horizontal_spacing // 2  # 给叶子节点额外空间
            node.subtree_width = min_width
            return min_width
            
        # 计算所有子节点的总宽度
        total_width = 0
        
        # 优化：如果子节点太多，考虑压缩宽度
        compression_factor = 1.0
        if len(node.children) > 3:
            compression_factor = 0.9  # 适当压缩过多子节点的间距
            
        for child in node.children:
            child_width = self._calculate_subtree_width(child)
            # 给每个子节点添加额外的间距，防止节点过于拥挤
            total_width += child_width * compression_factor + self.horizontal_spacing * compression_factor
            
        # 减去最后一个节点之后的额外间距
        if total_width > 0:
            total_width -= self.horizontal_spacing * compression_factor
            
        # 节点宽度至少要等于自己的宽度，或者比子节点总宽度稍大
        min_node_width = self.node_width + self.horizontal_spacing  # 给节点本身留出额外空间
        
        # 如果只有一个子节点，确保父节点比子节点宽
        if len(node.children) == 1:
            min_node_width = max(min_node_width, node.children[0].subtree_width + self.horizontal_spacing // 2)
            
        node.subtree_width = max(total_width, min_node_width)
        return node.subtree_width
        
    def _assign_positions(self, node, x_start, x_end, level):
        """为节点分配位置"""
        x_center = (x_start + x_end) // 2
        # 增加起始垂直位置，并根据层级计算节点位置
        y = level * (self.node_height + self.vertical_spacing) + 60
        
        # 保存节点信息
        self.nodes_info[node] = {
            'x': x_center - self.node_width // 2,
            'y': y,
            'width': self.node_width,
            'height': self.node_height,
            'level': level,
            'center_x': x_center,
            'center_y': y + self.node_height // 2
        }
        
        if hasattr(node, 'children') and node.children:
            available_width = x_end - x_start
            current_x = x_start
            
            # 如果子节点总宽度小于可用宽度，则在每个子节点之间添加额外的间距
            total_subtree_width = sum(child.subtree_width for child in node.children)
            extra_spacing = 0
            
            if total_subtree_width < available_width:
                extra_spacing = (available_width - total_subtree_width) / max(1, len(node.children) - 1)
            
            for child in node.children:
                # 计算子节点所需宽度占比，同时考虑额外间距
                child_width = child.subtree_width
                
                # 为子节点分配位置
                self._assign_positions(child, current_x, current_x + child_width, level + 1)
                current_x += child_width + self.horizontal_spacing + extra_spacing
        
    def render(self, surface, root_node, active_node=None):
        """渲染行为树"""
        # 检测树结构是否发生变化，如果变化则重新计算布局
        current_hash = self.tree_hash(root_node)
        if current_hash != self.last_tree_hash:
            self.needs_recalculation = True
        
        # 确保节点布局已计算
        if self.needs_recalculation or not hasattr(self, 'nodes_info') or not self.nodes_info:
            self.calculate_layout(root_node)
            
        # 根据缩放因子更新字体大小
        if self.scale_factor < 1.0:
            scaled_font_size = max(int(self.font_size * (0.8 + self.scale_factor * 0.2)), 10)
            try:
                if self.chinese_support:
                    self.font = get_font(False, scaled_font_size)
                else:
                    self.font = pygame.font.SysFont('Arial', scaled_font_size)
                self.info_font = self.font
            except Exception as e:
                print(f"调整字体大小失败: {e}")
            
        # 清除表面
        surface.fill(self.colors['background'])
        
        # 渲染连接线
        self._render_connections(surface, root_node)
        
        # 渲染节点
        self._render_nodes(surface, root_node, active_node)
        
        # 渲染树结构信息
        self._render_tree_info(surface, root_node)
        
    def handle_click(self, x, y, root_node, cat_instance=None):
        """处理点击事件，检查是否点击到节点，如果是则返回该节点"""
        if not hasattr(self, 'nodes_info') or not self.nodes_info:
            return None
            
        # 查找被点击的节点
        clicked_node = None
        for node, info in self.nodes_info.items():
            node_rect = pygame.Rect(info['x'], info['y'], info['width'], info['height'])
            if node_rect.collidepoint(x, y):
                clicked_node = node
                break
                
        if clicked_node and cat_instance:
            # 如果提供了猫实例，则显示点击节点的JSON结构
            try:
                # 使用简化的JSON格式
                node_json = cat_instance.behavior_tree_to_json(clicked_node)
                print(f"\n点击节点: {clicked_node.name}")
                print(node_json)
                
                # 打印节点路径（从根节点到点击节点）
                node_path = self._find_node_path(root_node, clicked_node)
                if node_path:
                    path_str = " -> ".join([n.name for n in node_path])
                    print(f"节点路径: {path_str}")
            except Exception as e:
                print(f"无法生成节点JSON: {e}")
                
        return clicked_node
        
    def _find_node_path(self, root, target, current_path=None):
        """查找从根节点到目标节点的路径"""
        if current_path is None:
            current_path = []
            
        # 添加当前节点到路径
        path = current_path + [root]
        
        # 如果找到目标节点，返回路径
        if root == target:
            return path
            
        # 递归检查子节点
        if hasattr(root, 'children') and root.children:
            for child in root.children:
                result = self._find_node_path(child, target, path)
                if result:
                    return result
                    
        # 没有找到目标节点
        return None
        
    def _render_tree_info(self, surface, root_node):
        """渲染树结构信息"""
        y = 10
        x = 10
        
        # 计算缩放后应调整的位置信息
        if self.scale_factor < 1.0:
            # 小型化信息并移到右上角以节省空间
            x = self.screen_width - 150
        
        # 显示树结构信息标题
        info_title = "行为树结构" if self.chinese_support else "Tree Structure"
        if self.chinese_support:
            title_surface = self.font.render(info_title, True, self.colors['text'])
        else:
            title_font = pygame.font.SysFont('Arial', 16, bold=True)
            title_surface = title_font.render(info_title, True, self.colors['text'])
            
        surface.blit(title_surface, (x, y))
        y += 25
        
        # 计算行为树统计信息
        node_count = self._count_nodes(root_node)
        depth = self._calculate_tree_depth(root_node)
        
        # 在缩放因子较小时简化显示信息
        if self.scale_factor < 0.7:
            # 简化显示，仅显示节点数
            info_text = f"N:{node_count} D:{depth}"
            info_surface = self.info_font.render(info_text, True, self.colors['text'])
            surface.blit(info_surface, (x, y))
            return
        
        # 显示统计信息
        info_lines = [
            f"{'节点数量' if self.chinese_support else 'Node Count'}: {node_count}",
            f"{'树深度' if self.chinese_support else 'Tree Depth'}: {depth}"
        ]
        
        for line in info_lines:
            info_surface = self.info_font.render(line, True, self.colors['text'])
            surface.blit(info_surface, (x, y))
            y += 20
    
    def _count_nodes(self, node):
        """计算树中的节点数量"""
        if not node:
            return 0
            
        count = 1  # 当前节点
        
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                count += self._count_nodes(child)
                
        return count
    
    def _calculate_tree_depth(self, node, current_depth=1):
        """计算树的深度"""
        if not node or not hasattr(node, 'children') or not node.children:
            return current_depth
            
        child_depths = [self._calculate_tree_depth(child, current_depth + 1) 
                       for child in node.children]
        return max(child_depths) if child_depths else current_depth
        
    def _render_connections(self, surface, node):
        """渲染节点之间的连接线"""
        if not hasattr(node, 'children') or not node.children:
            return
        
        # 确保节点在布局信息中
        if node not in self.nodes_info:
            return
            
        node_info = self.nodes_info[node]
        parent_x = node_info['center_x']
        parent_y = node_info['center_y']
        
        # 根据缩放因子调整线宽
        line_width = 3 if self.scale_factor > 0.85 else 2
        
        # 计算所有子节点的垂直线终点的Y坐标
        vertical_end_y = 0
        for child in node.children:
            if child in self.nodes_info:
                child_info = self.nodes_info[child]
                vertical_end_y = max(vertical_end_y, child_info['y'] - 15 * self.scale_factor)  # 垂直线向下延伸，留一些间距
                
        if vertical_end_y > 0 and len(node.children) > 1:
            # 先绘制从父节点向下的垂直线段
            pygame.draw.line(
                surface,
                self.colors['connection'],
                (parent_x, parent_y),
                (parent_x, vertical_end_y),
                line_width
            )
        
        for child in node.children:
            # 确保子节点在布局信息中
            if child not in self.nodes_info:
                continue
                
            child_info = self.nodes_info[child]
            child_x = child_info['center_x']
            child_y = child_info['y']
            
            if len(node.children) > 1:
                # 对于多个子节点，绘制水平线段连接垂直线和子节点垂直线
                pygame.draw.line(
                    surface,
                    self.colors['connection'],
                    (parent_x, vertical_end_y),
                    (child_x, vertical_end_y),
                    line_width
                )
                
                # 然后绘制从水平线到子节点的垂直线段
                pygame.draw.line(
                    surface,
                    self.colors['connection'],
                    (child_x, vertical_end_y),
                    (child_x, child_y),
                    line_width
                )
            else:
                # 对于单个子节点，直接绘制从父节点到子节点的连接线
                pygame.draw.line(
                    surface,
                    self.colors['connection'],
                    (parent_x, parent_y),
                    (child_x, child_y),
                    line_width
                )
            
            # 递归处理子节点
            self._render_connections(surface, child)
            
    def _render_nodes(self, surface, node, active_node=None):
        """渲染节点"""
        if node not in self.nodes_info:
            return
            
        node_info = self.nodes_info[node]
        x, y = node_info['x'], node_info['y']
        width, height = node_info['width'], node_info['height']
        
        # 确定是否是活动节点 - 不仅检查当前节点，还要递归查找到叶节点
        is_active_node = False
        if active_node is not None:
            is_active_node = node == active_node
            
            # 如果当前节点是sleep_node且猫处于sleeping状态，强制高亮
            if hasattr(node, 'name') and node.name == "sleep" and hasattr(node, 'cat'):
                if node.cat.state == "sleeping":
                    is_active_node = True
            
            # 同样对于其他叶节点也检查对应状态
            if hasattr(node, 'name') and hasattr(node, 'cat'):
                if node.name == "play" and node.cat.state == "playing":
                    is_active_node = True
                elif node.name == "wander" and node.cat.state == "wandering":
                    is_active_node = True
        
        # 根据节点类型确定基础颜色
        base_color = self.colors['inactive']  # 默认为灰色
        if node.__class__.__name__ == 'Sequence':
            base_color = self.colors['sequence']
        elif node.__class__.__name__ == 'Selector':
            base_color = self.colors['selector']
            
        # 确定节点颜色 - 根据用户要求修改颜色逻辑
        if is_active_node:
            # 当前活动节点使用特定颜色高亮显示
            if hasattr(node, 'status'):
                if node.status == NodeStatus.RUNNING:
                    color = self.colors['running']
                elif node.status == NodeStatus.SUCCESS:
                    color = self.colors['success']
                elif node.status == NodeStatus.FAILURE:
                    color = self.colors['failure']
                else:
                    color = self.colors['active']
            else:
                color = self.colors['active']
        else:
            # 非活动节点使用基础颜色
            color = base_color
        
        # 根据节点类型绘制不同形状的节点
        if node.__class__.__name__ == 'Sequence' or node.__class__.__name__ == 'Selector':
            # 复合节点使用圆角矩形
            pygame.draw.rect(surface, color, (x, y, width, height), 0, border_radius=15)
            pygame.draw.rect(surface, self.colors['text'], (x, y, width, height), 2, border_radius=15)
        else:
            # 叶节点使用矩形
            pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(surface, self.colors['text'], (x, y, width, height), 2)
        
        # 绘制节点名称
        name = node.name if hasattr(node, 'name') else node.__class__.__name__
        
        # 根据中文支持情况选择字体渲染方式
        try:
            # 根据缩放因子确定字符长度限制
            max_chars = 14
            if self.scale_factor < 0.85:
                max_chars = int(max_chars * self.scale_factor * 1.2)
                
            if self.chinese_support:
                # 对于中文名称，截断较长的名称
                if len(name) > max_chars:
                    name = name[:max_chars-2] + ".."
                    
                # 检查名称是否包含过长的单词，根据缩放因子决定是否换行
                if len(name) > 7 and " " in name and self.scale_factor > 0.7:
                    # 尝试在空格处添加换行符
                    words = name.split(" ")
                    name = "\n".join([" ".join(words[:len(words)//2]), 
                                     " ".join(words[len(words)//2:])])
                    
                # 如果有换行符，分行渲染
                if "\n" in name:
                    lines = name.split("\n")
                    line_height = self.font.get_height()
                    # 渲染第一行
                    text1 = self.font.render(lines[0], True, self.colors['text'])
                    text1_rect = text1.get_rect(centerx=x + width//2, 
                                              centery=y + height//2 - line_height//2)
                    surface.blit(text1, text1_rect)
                    # 渲染第二行
                    text2 = self.font.render(lines[1], True, self.colors['text'])
                    text2_rect = text2.get_rect(centerx=x + width//2, 
                                              centery=y + height//2 + line_height//2)
                    surface.blit(text2, text2_rect)
                else:
                    # 单行渲染
                    text = self.font.render(name, True, self.colors['text'])
                    text_rect = text.get_rect(center=(x + width//2, y + height//2))
                    surface.blit(text, text_rect)
            else:
                # 如果不支持中文，使用简化的英文替代
                if name == "观察并检索周围物品":
                    name = "Observe Items"
                elif name == "随机等待":
                    name = "Random Wait"
                elif name == "移动到目标点":
                    name = "Move to Target"
                elif name == "互动":
                    name = "Interact"
                elif name == "观望等待":
                    name = "Observe & Wait"
                elif name == "探索":
                    name = "Explore"
                
                # 节点名称过长时截断
                if len(name) > max_chars:
                    name = name[:max_chars-2] + ".."
                
                text = pygame.font.SysFont('Arial', self.font_size).render(name, True, self.colors['text'])
                text_rect = text.get_rect(center=(x + width//2, y + height//2))
                surface.blit(text, text_rect)
        except Exception as e:
            print(f"节点名称渲染错误 '{name}': {e}")
            # 错误情况下，回退到简单的文本渲染
            fallback_name = name[:8] + ".." if len(name) > 10 else name
            fallback_text = pygame.font.SysFont('Arial', self.font_size).render(
                fallback_name, True, self.colors['text'])
            fallback_rect = fallback_text.get_rect(center=(x + width//2, y + height//2))
            surface.blit(fallback_text, fallback_rect)
        
        # 递归渲染子节点
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                if child in self.nodes_info:  # 确保子节点在布局信息中
                    self._render_nodes(surface, child, active_node)
                
    def find_active_nodes(self, node):
        """查找当前活动的节点（状态为RUNNING的节点）"""
        active_nodes = []
        
        # 添加当前节点如果它是RUNNING状态
        if hasattr(node, 'status') and node.status == NodeStatus.RUNNING:
            active_nodes.append(node)
            
        # 检查是否为复合节点，如果是则递归查找
        if hasattr(node, 'children') and node.children:
            # 首先检查和添加复合节点本身
            if hasattr(node, 'status') and node.status == NodeStatus.RUNNING:
                if node not in active_nodes:  # 避免重复添加
                    active_nodes.append(node)
            
            # 对于Sequence和Selector，找到当前正在执行的子节点
            if hasattr(node, 'current_child') and 0 <= node.current_child < len(node.children):
                active_child = node.children[node.current_child]
                
                # 如果当前子节点处于RUNNING状态，添加它及其所有父节点
                if hasattr(active_child, 'status') and active_child.status == NodeStatus.RUNNING:
                    active_nodes.append(active_child)
                
                # 递归搜索当前活动子节点
                active_nodes.extend(self.find_active_nodes(active_child))
            
            # 对于其他类型的节点或者确保全面检查，遍历所有子节点
            else:
                for child in node.children:
                    if hasattr(child, 'status') and child.status == NodeStatus.RUNNING:
                        active_nodes.append(child)
                    active_nodes.extend(self.find_active_nodes(child))
        
        # 确保没有重复节点
        unique_active_nodes = []
        for n in active_nodes:
            if n not in unique_active_nodes:
                unique_active_nodes.append(n)
                
        return unique_active_nodes 