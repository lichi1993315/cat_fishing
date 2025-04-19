from behavior_tree.node import NodeStatus
from behavior_tree.composite import Sequence, Selector
from behavior_tree.actions import (
    Sleep, Wander, Play, ObserveItems, RandomWait,
    MoveToTarget, Interact, ObserveAndWait, Explore
)

class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "idle"
        # 行为倾向权重初始化
        self.behavior_weights = {
            "sleep": 1.0,
            "play": 1.0,
            "wander": 1.0,
            "explore": 1.0,
            "observe": 1.0,
            "interact": 1.0
        }
        self.setup_behavior_tree()
        
    def setup_behavior_tree(self):
        # 创建所有行为节点
        self.observe_items_node = ObserveItems("观察并检索周围物品", self)
        self.random_wait_node = RandomWait("随机等待", self)
        self.move_to_target_node = MoveToTarget("移动到目标点", self)
        self.interact_node_1 = Interact("互动", self)
        self.observe_and_wait_node = ObserveAndWait("观望等待", self)
        self.explore_node = Explore("探索", self)
        self.interact_node_2 = Interact("互动", self)
        
        # 保留原来的基础行为以供命令切换
        self.sleep_node = Sleep("sleep", self)
        self.wander_node = Wander("wander", self)
        self.play_node = Play("play", self)
        
        # 重新创建完整行为树
        self.create_behavior_tree()
        
    def create_behavior_tree(self):
        """根据当前行为倾向创建行为树"""
        # 基于权重创建复合行为节点
        # 睡眠行为树
        self.sleep_tree = Sequence("sleep_tree", [
            RandomWait("sleep_wait", self),
            self.sleep_node
        ])
        
        # 玩耍行为树
        self.play_tree = Sequence("play_tree", [
            RandomWait("play_wait", self),
            self.play_node
        ])
        
        # 游荡行为树
        self.wander_tree = Sequence("wander_tree", [
            RandomWait("wander_wait", self),
            self.wander_node
        ])
        
        # 创建左侧序列：移动到目标点 + 互动
        self.left_sequence = Sequence("Sequence", [
            self.move_to_target_node,
            self.interact_node_1
        ])
        
        # 创建右侧序列：观望等待 + 探索 + 互动
        self.right_sequence = Sequence("Sequence", [
            self.observe_and_wait_node,
            self.explore_node,
            self.interact_node_2
        ])
        
        # 创建选择器：左序列 or 右序列
        self.action_selector = Selector("Selector", [
            self.left_sequence,
            self.right_sequence
        ])
        
        # 创建标准行为序列：观察物品 + 随机等待 + 行为选择器
        self.standard_behavior = Sequence("Sequence", [
            self.observe_items_node,
            self.random_wait_node,
            self.action_selector
        ])
        
        # 根据行为树图表结构，默认使用标准行为作为根节点
        self.root = self.standard_behavior
        
        # 如果有任何特殊指令或高优先级行为，再使用选择器进行判断
        if any(weight > 1.5 for weight in self.behavior_weights.values()):
            # 根据当前行为倾向权重创建行为选择器
            behavior_nodes = []
            
            # 按权重降序添加行为，确保高权重行为优先执行
            behaviors = sorted(
                self.behavior_weights.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for behavior, weight in behaviors:
                if weight > 1.5:  # 只有权重显著高的行为才会被优先考虑
                    if behavior == "sleep":
                        behavior_nodes.append(self.sleep_tree)
                    elif behavior == "play":
                        behavior_nodes.append(self.play_tree)
                    elif behavior == "wander":
                        behavior_nodes.append(self.wander_tree)
            
            # 添加标准行为作为备选行为
            behavior_nodes.append(self.standard_behavior)
            
            # 创建最终的行为树根节点为选择器
            self.root = Selector("root", behavior_nodes)
        
    def update(self):
        self.root.tick()
        
    def move(self, dx, dy):
        self.x = max(0, min(79, self.x + dx))  # Assuming 80x24 terminal
        self.y = max(0, min(23, self.y + dy))
        
    def get_display_char(self):
        if self.state == "sleeping":
            return "z"
        elif self.state == "playing":
            return "!"
        elif self.state == "wandering":
            return "o"
        elif self.state == "observing":
            return "?"
        elif self.state == "waiting":
            return "."
        elif self.state == "moving":
            return ">"
        elif self.state == "interacting":
            return "*"
        elif self.state == "observing_wait":
            return "^"
        elif self.state == "exploring":
            return "#"
        return "@"
        
    def modify_behavior(self, command):
        """根据用户命令修改行为树"""
        if command == "sleep":
            # 增加睡眠倾向
            self.behavior_weights["sleep"] += 1.0
            # 降低其他行为倾向
            self.behavior_weights["play"] *= 0.8
            self.behavior_weights["wander"] *= 0.8
        elif command == "play":
            # 增加玩耍倾向
            self.behavior_weights["play"] += 1.0
            # 降低其他行为倾向
            self.behavior_weights["sleep"] *= 0.8
        elif command == "wander":
            # 增加游荡倾向
            self.behavior_weights["wander"] += 1.0
        elif command == "explore":
            # 增加探索倾向
            self.behavior_weights["explore"] += 1.0
            # 调整标准行为中探索相关节点
            self.right_sequence.children = [
                RandomWait("explore_wait", self),
                self.explore_node
            ]
        elif command == "interact":
            # 增加互动倾向
            self.behavior_weights["interact"] += 1.0
            # 调整标准行为中互动相关节点
            both_sequences = [self.left_sequence, self.right_sequence]
            for seq in both_sequences:
                if len(seq.children) > 0 and seq.children[-1].__class__.__name__ != "Interact":
                    seq.children.append(Interact(f"interact_{id(seq)}", self))
        elif command == "observe":
            # 增加观察倾向
            self.behavior_weights["observe"] += 1.0
            # 调整标准行为中观察相关节点
            self.observe_items_node.observe_duration *= 1.5
        elif command == "default":
            # 重置所有行为倾向为默认值
            self.behavior_weights = {
                "sleep": 1.0,
                "play": 1.0,
                "wander": 1.0,
                "explore": 1.0,
                "observe": 1.0,
                "interact": 1.0
            }
            self.setup_behavior_tree()
            return
            
        # 创建新的行为树
        self.create_behavior_tree() 