import base64
import anthropic
import httpx
import os
import json
from openai import AzureOpenAI
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

def generate_behavior_tree_with_azure(instruction, api_version="2024-02-01"):
    """
    Generate a behavior tree from a natural language instruction using Azure OpenAI.
    
    Args:
        instruction (str): Natural language instruction describing desired behavior
        api_version (str): Azure OpenAI API version
        
    Returns:
        str: JSON string representation of the behavior tree
    """
    # Create Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version=api_version,
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    # Example base behavior tree (same as used for Claude)
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
    
    # Define the Text2BehaviorTree tool for Azure OpenAI
    text2_behavior_tree_tool = {
        "type": "function",
        "function": {
            "name": "Text2BehaviorTree",
            "description": "Based on the user's instruction, generate a well-structured JSON for a behavior tree.",
            "parameters": {
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
    }
    
    # Create the message with Azure OpenAI
    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your deployment name
        messages=[
            {
                "role": "user",
                "content": f"Based on this instruction, modify original behavior tree JSON: {instruction}. Only use these action nodes: AgentPatrol, AgentDestination, Eat, Sleep, Play, Talk, Work, SelectAction. And only use these condition nodes: IsTired, IsHungry, IsBored, IsLonely, HaveNextAction. Previous Behavior Tree JSON: {example_json}"
            }
        ],
        tools=[text2_behavior_tree_tool],
        tool_choice={"type": "function", "function": {"name": "Text2BehaviorTree"}}
    )
    
    print(response)
    
    # Extract the behavior tree from the response
    if response.choices and response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "Text2BehaviorTree":
            try:
                # First, get the raw arguments string
                args_str = tool_call.function.arguments
                
                # Try to parse it as JSON (it should be properly formatted JSON)
                args_json = json.loads(args_str)
                
                # If there's a 'structure' field, that's the full behavior tree
                if 'structure' in args_json:
                    # Return a properly formatted JSON string
                    return json.dumps(args_json, indent=2, ensure_ascii=False)
                return args_str
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in tool call response")
                return args_str
    
    # If no tool result found, return None
    return None

def parse_claude_response(message):
    """
    Parse different formats of Claude API responses to extract the behavior tree.
    
    Args:
        message: Response from Claude API
        
    Returns:
        str: JSON string of the behavior tree or None if not found
    """
    print(f"Parsing Claude response: {type(message)}")
    
    # Handle different response formats
    if hasattr(message, 'content'):
        for content in message.content:
            print(f"Parsing Claude response: {content}")
            # Check for tool_result format
            if hasattr(content, 'type') and content.type == "tool_result" and hasattr(content, 'tool_name') and content.tool_name == "Text2BehaviorTree":
                return content.text
            
            # Check for ToolUseBlock format
            if hasattr(content, 'type') and content.type == "tool_use" and hasattr(content, 'name') and content.name == "Text2BehaviorTree":
                # Extract from input field which contains the behavior tree structure
                if hasattr(content, 'input') and isinstance(content.input, dict):
                    # Format the structure as JSON
                    return json.dumps(content.input, indent=2, ensure_ascii=False)
    
    # Try direct access to response content for newer API versions
    if isinstance(message, dict) and 'content' in message:
        for content in message['content']:
            if content.get('type') == 'tool_use' and content.get('name') == 'Text2BehaviorTree':
                return json.dumps(content.get('input', {}), indent=2, ensure_ascii=False)
    
    # If no tool result found, return None
    print("Warning: Could not extract behavior tree from Claude response")
    return None

def generate_behavior_tree(instruction, provider="claude"):
    """
    Generate a behavior tree from a natural language instruction.
    
    Args:
        instruction (str): Natural language instruction describing desired behavior
        provider (str): The AI provider to use ('claude' or 'azure')
        
    Returns:
        str: JSON string representation of the behavior tree
    """
    if provider.lower() == "azure":
        return generate_behavior_tree_with_azure(instruction)
    else:  # Use Claude by default
        # Use the API key from .env file
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Example base behavior tree
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
                        {"type": "text", "text": f"Based on this instruction, modify original behavior tree JSON: {instruction}. Only use these action nodes: AgentPatrol, AgentDestination, Eat, Sleep, Play, Talk, Work, SelectAction. And only use these condition nodes: IsTired, IsHungry, IsBored, IsLonely, HaveNextAction. Previous Behavior Tree JSON: {example_json}"}
                    ]
                }
            ]
        )

        print(message)
        
        # Use the dedicated parser function to extract the behavior tree
        return parse_claude_response(message)

def format_azure_response(azure_response):
    """
    Format the Azure OpenAI response to match the Claude response format.
    
    Args:
        azure_response (str): JSON string from Azure OpenAI function call
        
    Returns:
        str: Formatted JSON string
    """
    try:
        # Parse the JSON string into a Python object
        response_obj = json.loads(azure_response)
        
        # Format it with proper indentation
        return json.dumps(response_obj, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from Azure OpenAI")
        return azure_response

# Example of how to call the function
if __name__ == "__main__":
    print("=" * 50)
    print("Behavior Tree Generation Test")
    print("=" * 50)
    print(f"User instruction: {user_instruction}")
    print("-" * 50)
    
    # Use Claude (default)
    try:
        print("Generating behavior tree using Claude...")
        result_claude = generate_behavior_tree(user_instruction)
        if result_claude:
            print("Successfully generated behavior tree with Claude:")
            print(result_claude)
            # Save to file for reference
            with open("claude_behavior_tree.json", "w", encoding="utf-8") as f:
                f.write(result_claude)
            print(f"Saved to claude_behavior_tree.json")
        else:
            print("Failed to generate behavior tree with Claude.")
    except Exception as e:
        print(f"Error using Claude: {str(e)}")
    
    print("-" * 50)
    
    # Use Azure OpenAI
    try:
        print("Generating behavior tree using Azure OpenAI...")
        # Check if Azure OpenAI credentials are available
        if not os.environ.get("AZURE_OPENAI_API_KEY") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
            print("Azure OpenAI credentials not found in .env file. Skipping Azure test.")
        else:
            result_azure = generate_behavior_tree(user_instruction, provider="azure")
            if result_azure:
                result_azure = format_azure_response(result_azure)
                print("Successfully generated behavior tree with Azure OpenAI:")
                print(result_azure)
                # Save to file for reference
                with open("azure_behavior_tree.json", "w", encoding="utf-8") as f:
                    f.write(result_azure)
                print(f"Saved to azure_behavior_tree.json")
            else:
                print("Failed to generate behavior tree with Azure OpenAI.")
    except Exception as e:
        print(f"Error using Azure OpenAI: {str(e)}")
    
    print("=" * 50)

