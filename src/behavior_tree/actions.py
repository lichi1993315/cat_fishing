from .node import Node, NodeStatus
import random

class Sleep(Node):
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.sleep_duration = random.randint(3, 8)
        self.sleep_time = 0
        
    def tick(self):
        if self.sleep_time >= self.sleep_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        self.cat.state = "sleeping"
        self.sleep_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.sleep_time = 0
        self.sleep_duration = random.randint(3, 8)

class Wander(Node):
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.move_cooldown = 0
        
    def tick(self):
        if self.move_cooldown <= 0:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.cat.move(dx, dy)
            self.move_cooldown = random.uniform(0.5, 2.0)
            
        self.move_cooldown -= 0.1
        self.cat.state = "wandering"
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.move_cooldown = 0

class Play(Node):
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.play_duration = random.randint(2, 5)
        self.play_time = 0
        
    def tick(self):
        if self.play_time >= self.play_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        if random.random() < 0.3:
            dx = random.choice([-2, -1, 1, 2])
            dy = random.choice([-2, -1, 1, 2])
            self.cat.move(dx, dy)
            
        self.cat.state = "playing"
        self.play_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.play_time = 0
        self.play_duration = random.randint(2, 5)

class ObserveItems(Node):
    """观察并检索周围物品"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.observe_time = 0
        self.observe_duration = random.uniform(0.5, 1.5)
        
    def tick(self):
        if self.observe_time >= self.observe_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        self.cat.state = "observing"
        self.observe_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.observe_time = 0
        self.observe_duration = random.uniform(0.5, 1.5)

class RandomWait(Node):
    """随机等待"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.wait_time = 0
        self.wait_duration = random.uniform(1.0, 3.0)
        
    def tick(self):
        if self.wait_time >= self.wait_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        self.cat.state = "waiting"
        self.wait_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.wait_time = 0
        self.wait_duration = random.uniform(1.0, 3.0)

class MoveToTarget(Node):
    """移动到目标点"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.target_x = None
        self.target_y = None
        self.move_steps = 0
        self.max_steps = random.randint(5, 15)
        
    def tick(self):
        if self.target_x is None or self.move_steps >= self.max_steps:
            # 设置新的随机目标
            self.target_x = random.randint(5, 75)
            self.target_y = random.randint(5, 20)
            self.move_steps = 0
            
        dx = 1 if self.target_x > self.cat.x else -1 if self.target_x < self.cat.x else 0
        dy = 1 if self.target_y > self.cat.y else -1 if self.target_y < self.cat.y else 0
        
        self.cat.move(dx, dy)
        self.cat.state = "moving"
        self.move_steps += 1
        
        # 检查是否到达目标点附近
        if abs(self.cat.x - self.target_x) <= 1 and abs(self.cat.y - self.target_y) <= 1:
            self.reset()
            return NodeStatus.SUCCESS
            
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.target_x = None
        self.target_y = None
        self.move_steps = 0
        self.max_steps = random.randint(5, 15)

class Interact(Node):
    """互动"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.interact_time = 0
        self.interact_duration = random.uniform(1.0, 2.0)
        
    def tick(self):
        if self.interact_time >= self.interact_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        if random.random() < 0.2:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.cat.move(dx, dy)
            
        self.cat.state = "interacting"
        self.interact_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.interact_time = 0
        self.interact_duration = random.uniform(1.0, 2.0)

class ObserveAndWait(Node):
    """观望等待"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.observe_time = 0
        self.observe_duration = random.uniform(2.0, 4.0)
        
    def tick(self):
        if self.observe_time >= self.observe_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        self.cat.state = "observing_wait"
        self.observe_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.observe_time = 0
        self.observe_duration = random.uniform(2.0, 4.0)

class Explore(Node):
    """探索"""
    def __init__(self, name, cat):
        super().__init__(name)
        self.cat = cat
        self.explore_time = 0
        self.explore_duration = random.uniform(3.0, 6.0)
        self.move_cooldown = 0
        
    def tick(self):
        if self.explore_time >= self.explore_duration:
            self.reset()
            return NodeStatus.SUCCESS
            
        if self.move_cooldown <= 0:
            dx = random.choice([-1, -1, 0, 1, 1])  # 更倾向于水平移动
            dy = random.choice([-1, 0, 0, 1])  # 更倾向于原地或小幅度垂直移动
            self.cat.move(dx, dy)
            self.move_cooldown = random.uniform(0.3, 0.8)
            
        self.move_cooldown -= 0.1
        self.cat.state = "exploring"
        self.explore_time += 0.1
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.explore_time = 0
        self.explore_duration = random.uniform(3.0, 6.0)
        self.move_cooldown = 0 