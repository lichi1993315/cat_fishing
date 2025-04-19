from .node import Node, NodeStatus

class Sequence(Node):
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []
        self.current_child = 0
        
    def tick(self):
        if not self.children:
            return NodeStatus.SUCCESS
            
        current = self.children[self.current_child]
        status = current.tick()
        
        if status == NodeStatus.FAILURE:
            self.reset()
            return NodeStatus.FAILURE
            
        if status == NodeStatus.RUNNING:
            return NodeStatus.RUNNING
            
        self.current_child += 1
        if self.current_child >= len(self.children):
            self.reset()
            return NodeStatus.SUCCESS
            
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset()

class Selector(Node):
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []
        self.current_child = 0
        
    def tick(self):
        if not self.children:
            return NodeStatus.FAILURE
            
        current = self.children[self.current_child]
        status = current.tick()
        
        if status == NodeStatus.SUCCESS:
            self.reset()
            return NodeStatus.SUCCESS
            
        if status == NodeStatus.RUNNING:
            return NodeStatus.RUNNING
            
        self.current_child += 1
        if self.current_child >= len(self.children):
            self.reset()
            return NodeStatus.FAILURE
            
        return NodeStatus.RUNNING
        
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset() 