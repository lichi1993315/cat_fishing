from enum import Enum

class NodeStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"

class Node:
    def __init__(self, name):
        self.name = name
        self.status = NodeStatus.RUNNING
        
    def tick(self):
        """Execute the node's logic"""
        raise NotImplementedError
        
    def reset(self):
        """Reset the node's state"""
        self.status = NodeStatus.RUNNING 