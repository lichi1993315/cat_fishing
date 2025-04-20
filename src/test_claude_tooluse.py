import base64
import anthropic
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
image_media_type = "image/jpeg"
image_data = base64.standard_b64encode(httpx.get(image_url).content).decode("utf-8")

# Use the API key from .env file
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Example instruction for reference
example_instruction = """
一个喜欢探索的宠物，会观察周围物品，如果看到感兴趣的物品，会去探索，如果看到其他宠物，会去互动。
"""

# User instruction to convert to behavior tree
user_instruction = """
一只好奇的猫，会在房间里巡逻，发现玩具时会去玩耍，发现食物时会去吃，困了会找个地方睡觉。
"""

# Example JSON output for reference
example_json = """
{
  "name": "BehaviorTree",
  "type": "Root",
  "children": [
    {
      "type": "Sequence",
      "name": "Sequence",
      "children": [
        {
          "type": "CustomAction",
          "name": "Sleep",
          "params": [
            0.9158622996289045
          ]
        },
        {
          "type": "WaitTime",
          "name": "WaitTime",
          "params": [
            2.5864573062009315
          ]
        },
        {
          "name": "Selector",
          "type": "Selector",
          "children": [
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomAction",
                  "name": "AgentDestination",
                },
                {
                  "type": "CustomAction",
                  "name": "Eat"
                }
              ]
            },
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomCondition",
                  "name": "IsHungry",
                },
                {
                  "type": "CustomAction",
                  "name": "AgentPatrol"
                },
                {
                  "type": "CustomAction",
                  "name": "Talk"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""

example_output = """
{
  "structure": {
    "name": "BehaviorTree",
    "type": "Root",
    "children": [
      {
        "name": "Selector",
        "type": "Selector", 
        "children": [
          {
            "name": "Sequence",
            "type": "Sequence",
            "children": [
              {
                "type": "CustomCondition",
                "name": "IsTired"
              },
              {
                "type": "CustomAction",
                "name": "Sleep"
              }
            ]
          },
          {
            "name": "Sequence",
            "type": "Sequence",
            "children": [
              {
                "type": "CustomCondition",
                "name": "IsHungry"
              },
              {
                "type": "CustomAction",
                "name": "AgentDestination"
              },
              {
                "type": "CustomAction",
                "name": "Eat"
              }
            ]
          },
          {
            "name": "Sequence",
            "type": "Sequence",
            "children": [
              {
                "type": "CustomCondition",
                "name": "IsBored"
              },
              {
                "type": "CustomAction",
                "name": "AgentDestination"
              },
              {
                "type": "CustomAction",
                "name": "Play"
              }
            ]
          },
          {
            "name": "Sequence",
            "type": "Sequence",
            "children": [
              {
                "type": "CustomAction",
                "name": "AgentPatrol"
              }
            ]
          }
        ]
      }
    ]
  },
  "allowed_custom_actions": [
    "AgentPatrol",
    "AgentDestination", 
    "Eat",
    "Sleep",
    "Play",
    "Talk",
    "Work",
    "SelectAction"
  ],
  "allowed_custom_conditions": [
    "IsTired",
    "IsHungry", 
    "IsBored",
    "IsLonely",
    "HaveNextAction"
  ],
  "nodes": [
    {
      "name": "BehaviorTree",
      "type": "Root",
      "children": [
        {
          "name": "Selector",
          "type": "Selector",
          "children": [
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomCondition",
                  "name": "IsTired"
                },
                {
                  "type": "CustomAction",
                  "name": "Sleep"
                }
              ]
            },
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomCondition",
                  "name": "IsHungry"
                },
                {
                  "type": "CustomAction",
                  "name": "AgentDestination"
                },
                {
                  "type": "CustomAction",
                  "name": "Eat"
                }
              ]
            },
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomCondition",
                  "name": "IsBored"
                },
                {
                  "type": "CustomAction",
                  "name": "AgentDestination"
                },
                {
                  "type": "CustomAction",
                  "name": "Play"
                }
              ]
            },
            {
              "name": "Sequence",
              "type": "Sequence",
              "children": [
                {
                  "type": "CustomAction",
                  "name": "AgentPatrol"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""

# Available Action nodes:
# - AgentPatrol(bool RandomRoute = false): Makes the agent patrol an area, with optional random route
# - AgentDestination(): Makes the agent move to a specific destination
# - Eat(): Makes the agent eat
# - Sleep(): Makes the agent sleep
# - Play(): Makes the agent play
# - Talk(): Makes the agent talk
# - Work(): Makes the agent work
# - SelectAction(): Makes the agent select an action based on conditions

# Available Condition nodes:
# - IsTired: Checks if the agent is tired
# - IsHungry: Checks if the agent is hungry
# - IsBored: Checks if the agent is bored
# - IsLonely: Checks if the agent is lonely
# - HaveNextAction: Checks if the agent has a next action

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=2048,
    tools=[
        {
            "name": "Text2BehaviorTree",
            "description": "Based on the user's instruction, generate a well-structured JSON for a behavior tree.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Type of node (Must be one of: Root, Sequence, Selector, Action, Condition, WaitTime, CustomAction, CustomCondition)"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "If type is CustomAction or CustomCondition, this is the name of the node. Otherwise, it is the same as the type."
                                },
                                "children": {
                                    "type": "array",
                                    "description": "Child nodes, if applicable"
                                },
                                "params": {
                                    "type": "array",
                                    "description": "Parameters for the node, if applicable"
                                }
                            },
                            "required": ["name", "type"]
                        },
                        "description": "All nodes in the behavior tree"
                    },
                    "structure": {
                        "type": "object",
                        "description": "The full JSON structure of the behavior tree"
                    },
                    "allowed_custom_actions": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["AgentPatrol", "AgentDestination", "Eat", "Sleep", "Play", "Talk", "Work", "SelectAction"]
                        },
                        "description": "Only these action types are allowed: AgentPatrol, AgentDestination, Eat, Sleep, Play, Talk, Work, SelectAction"
                    },
                    "allowed_custom_conditions": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["IsTired", "IsHungry", "IsBored", "IsLonely", "HaveNextAction"]
                        },
                        "description": "Only these condition types are allowed: IsTired, IsHungry, IsBored, IsLonely, HaveNextAction"
                    }
                },
                "required": ["structure"]
            }
        }
    ],
    tool_choice={"type": "tool", "name": "Text2BehaviorTree"},
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Based on this instruction, modify original behavior tree JSON: {user_instruction}. Only use these action nodes: AgentPatrol, AgentDestination, Eat, Sleep, Play, Talk, Work, SelectAction. And only use these condition nodes: IsTired, IsHungry, IsBored, IsLonely, HaveNextAction. Previous Behavior Tree JSON: {example_json}"}
            ]
        }
    ]
)

print(message)

