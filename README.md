<div align="center">
  <img src="https://s2.loli.net/2022/06/16/opBDE8Swad5rU3n.png" width="180" height="180" alt="NoneBotPluginLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>


<div align="center">

# Nnonebot-plugin-gpt3

_✨ 基于openai GPT3官方API的对话插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/EtherLeaF/nonebot-plugin-colab-novelai" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0r4+-red.svg" alt="NoneBot">
  <a href="https://pypi.python.org/pypi/nonebot-plugin-gpt3">
      <img src="https://img.shields.io/pypi/dm/nonebot-plugin-gpt3" alt="pypi download">
  </a>
</p>


</div>

# 功能

- [x] 上下文功能
- [x] 会话导出
- [x] 返回文字图片渲染
- [x] 每个人单独会话
- [x] 人格设置
- [x] 连续会话

# 如何使用？

私聊中是直接发送消息，**群聊中是以回复的方式发送。**

以下是功能列表

|            功能            |           指令            |
| :------------------------: | :-----------------------: |
| 重置会话记录，开始新的对话 |       刷新/重置对话       |
|         重置AI人格         |         重置人格          |
|         设置AI人格         |         设置人格          |
|        导出历史会话        |     导出会话/导出对话     |
|     **基本的聊天对话**     | 基本会话（默认【.】触发） |
|        **连续对话**        |    chat/聊天/开始聊天     |
|    **结束连续聊天模式**    |    stop/结束/结束聊天     |
|       回答渲染为图片       |   图片渲染（默认关闭）    |

## 基本会话

对话前，加上前缀即可与GPT3对话。

​	![image-20221221203808576](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221221203808576.png)

## 连续会话

输入**chat/聊天/开始聊天**即可不加前缀，连续的对话，输入**结束/结束聊天**，即可结束聊天

![image-20221217230058979](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217230058979.png)

## 人格设置

预设了**AI助手/猫娘/nsfw猫娘**三种人格，可以通过人格设置切换。内置的设定可以从[这里看到](https://github.com/chrisyy2003/lingyin-bot/blob/main/plugins/gpt3/nonebot_plugin_gpt3/__init__.py#L16-L18)。

![image-20221217231703614](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217231703614.png)

同样也可以手动指定人格

![image-20221217232155100](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217232155100.png)

## 图片渲染

图片渲染可以在配置文件中配置是否，需要渲染

![image-20221217233729263](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217233729263.png)

# 安装

1.  使用 nb-cli

```
nb plugin install nonebot-plugin-gpt3
```

2.   通过包管理器安装，可以通过nb，pip3，或者poetry等方式安装，以pip为例

```
pip install nonebot-plugin-gpt3
```

随后在`bot.py`中加上如下代码，加载插件

```
nonebot.load_plugin('nonebot_plugin_gpt3')
```

**windows用户还需要安装一个rust环境，[点击这里下载安装](https://file.chrisyy.top/rustup-setup.exe)。**

# 配置

对于官方openai接口只需配置API Keys即可，所以请填写API在您配置的`chatgpt_token_path`下面，默认路径是`config/chatgpt_api_key.yml`

文件内格式如下，有多个Key请按照如下格式配置。

```
api_keys: [
	XXX,
	YYY
]
```

之后是一些自定义配置，根据注释可以自行修改，如果需要配置请在`env.dev`下进行配置。

```
gpt3_api_key_path = "config/chatgpt_api_key.yml"   # api文件的路径
gpt3_command_prefix = "."                          # 基本会话中的指令前缀
gpt3_need_at = False                               # 是否需要@才触发命令
gpt3_image_render = True                           # 是否渲染为图片
gpt3_image_limit = 100                             # 长度超过多少才会渲染成图片
gpt3_max_tokens = 400                              # 最大返回值长度
```

