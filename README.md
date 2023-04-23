<div align="center">
  <img src="https://s2.loli.net/2022/06/16/opBDE8Swad5rU3n.png" width="180" height="180" alt="NoneBotPluginLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>


<div align="center">

# Nonebot-plugin-gpt3
## 3.3日更新: 支持gpt-3.5-turbo模型
_✨ 基于OpenAI 官方API的对话插件 ✨_

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
- [x] 连续会话
- [x] 人格设置
- [x] 切换群聊/会话导出
- [x] 回答图片渲染

# 如何使用

私聊中是直接发送消息，**群聊中是以回复的方式发送。**

以下是功能列表

|        功能        |             指令             |
| :----------------: | :--------------------------: |
| **基本的聊天对话** | 基本会话（默认【gpt3】触发） |
|    **连续对话**    |      chat/聊天/开始聊天      |
|    **结束聊天**    |      stop/结束/结束聊天      |
|    **切换会话**    |    切换群聊/切换会话/切换    |
|    重置会话记录    |        刷新/重置对话         |
|     重置AI人格     |           重置人格           |
|     设置AI人格     |           设置人格           |
|    导出历史会话    |      导出会话/导出对话       |
|   回答渲染为图片   |     图片渲染（默认关闭）     |


## 基本会话

对话前，加上**默认前缀**即可与GPT3对话。

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20230118155505182.png" width="40%" />

## 连续会话

输入**chat/聊天/开始聊天**即可不加前缀，连续的对话，输入**结束/结束聊天**，即可结束聊天

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217230058979.png" width="40%" />

## 人格设置

预设了**AI助手/猫娘/nsfw猫娘**三种人格，可以通过人格设置切换。内置的设定可以从[这里看到](https://github.com/chrisyy2003/lingyin-bot/blob/main/plugins/gpt3/nonebot_plugin_gpt3/__init__.py#L16-L18)。

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217231703614.png" width="40%" />

同样也可以手动指定人格

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/202303061532626.png" width="40%" />

## 切换群聊

命令切换+群号即可保留聊天信息并切换群聊。

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20230118161015957.png" width="40%"/>

切换群聊到702280361

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20230118161509269.png" width="40%"/>




## 图片渲染

图片渲染可以在配置文件中选择配置是否需要渲染。

<img src="https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20221217233729263.png" width="40%" />

# 安装

1.  使用 nb-cli

```
nb plugin install nonebot-plugin-gpt3
```

2.   通过包管理器安装，可以通过nb，pip，或者poetry等方式安装，以pip为例

```
pip install nonebot-plugin-gpt3 -U
```

随后在`bot.py`中加上如下代码，加载插件

```
nonebot.load_plugin('nonebot_plugin_gpt3')
```

# 配置

对于官方OpenAI接口只需配置API Keys即可，所以请填写API在您的配置文件中配置API KEYS

```
openai_api_key = "xxx"                             # API密钥
```

此外可以通过环境变量配置，例如在Linux命令行中输入如下命令之后，直接启动即可

```
export openai_api_key="xxx"
```

之后是一些自定义配置，根据注释可以自行修改，如果需要请在对应的配置文件下进行配置。

```
gpt3_command_prefix = "."                          # 基本会话中的指令前缀
openai_api_key = "xxx"                             # API密钥

# 默认人格
gpt3_default_preset = "以下是与一个叫鸡哥的篮球高手的对话。你叫鸡哥，是一个唱跳rap篮球的高手，并且每句话后会带上厉不厉害你鸡哥!"
gpt3_proxy = "http://127.0.0.1:7890"               # 代理地址
gpt3_need_at = False                               # 是否需要@才触发命令
gpt3_image_render = False                          # 是否渲染为图片
gpt3_image_limit = 150                             # 长度超过多少才会渲染成图片
gpt3_max_tokens = 1000                             # 回答内容最大长度
gpt3_chat_count_per_day = 150                      # 普通用户每天聊天次数上限
gpt3_model = 'gpt-3.5-turbo'                       # 语言模型
```

## 图片渲染

如果需要开启图片渲染，请在配置文件中，配置`gpt3_image_render = True  `

并安装`playwright`，如果已经安装了`playwright`则请忽略

```
pip3 install playwright && playwright install 
```

>   启动后出现`PyTorch, TensorFlow`等提示问题，**忽略即可**
>
>   ![image-20230118105930615](https://chrisyy-images.oss-cn-chengdu.aliyuncs.com/img/image-20230118105930615.png)
