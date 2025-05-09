# ASCII Cat Game

一个基于ASCII的猫咪模拟游戏，猫咪通过复杂的行为树系统行动。玩家可以通过文本命令修改猫的行为模式。游戏界面包含实时可视化的行为树展示。

## 系统要求
- Python 3.8+
- Pygame 2.5.2

## 如何运行
1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行游戏:
```bash
python src/main.py
```

## 中文字体支持
游戏使用以下方法尝试加载中文字体:
1. 尝试使用系统中安装的中文字体
2. 如果找不到合适的中文字体，会回退到默认字体(可能无法显示中文)

## 游戏界面
游戏界面分为三个主要区域：
- **游戏视图**：显示猫咪和游戏环境的ASCII视图
- **行为树可视化**：实时显示行为树结构和当前活动节点
- **状态与信息**：显示猫咪状态、位置信息和可用命令

## 游戏控制
- 使用键盘输入命令
- 回车键提交命令
- H键显示/隐藏帮助
- ESC键退出游戏

## 行为树可视化
游戏实现了一个行为树可视化功能，用于直观展示猫咪的行为逻辑：
- 活动节点以绿色突出显示
- 不同类型节点以不同颜色表示：
  - 序列节点(Sequence): 绿色
  - 选择节点(Selector): 红色
  - 运行中的节点: 黄色
  - 成功的节点: 绿色
  - 失败的节点: 红色

## 猫咪行为树结构
游戏实现了一个复杂的行为树结构:
- 主序列(Sequence)
  - 观察并检索周围物品
  - 随机等待
  - 行为选择器(Selector)
    - 路径1序列:
      - 移动到目标点
      - 互动
    - 路径2序列:
      - 观望等待
      - 探索
      - 互动

## 行为树生成
系统支持使用两种AI提供商来根据自然语言指令生成行为树：

### Claude AI
默认使用Anthropic的Claude 3.7 Sonnet模型生成行为树。需要在`.env`文件中设置：
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Azure OpenAI
也支持使用Azure OpenAI服务生成行为树。需要在`.env`文件中设置：
```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
```

要使用Azure OpenAI进行行为树生成，可以在代码中指定provider参数：
```python
result = generate_behavior_tree(instruction, provider="azure")
```

## 命令列表
你可以通过输入以下命令来修改猫的行为:
- "default": 恢复默认行为树
- "sleep": 让猫睡觉
- "play": 让猫玩耍
- "wander": 让猫游荡
- "observe": 让猫观察周围物品
- "explore": 让猫探索
- "interact": 让猫互动
- "debug": 切换调试模式

## 猫咪状态说明
- sleeping (z): 猫在睡觉
- playing (!): 猫在玩耍
- wandering (o): 猫在游荡
- observing (?): 猫在观察周围物品
- waiting (.): 猫在等待
- moving (>): 猫在移动到目标点
- interacting (*): 猫在互动
- observing_wait (^): 猫在观望等待
- exploring (#): 猫在探索 