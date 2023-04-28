import asyncio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, PrivateMessageEvent, MessageSegment, GroupMessageEvent
from nonebot.params import Arg, ArgPlainText, CommandArg, Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
import time
from .config import *
from .openai import get_chat_response, gpt3_model
from typing import Dict

# 一些公共变量
default_preset = gpt3_default_preset
api_index = -1
# 公共模式
public_mode = False
public_sessionID = 'public_session'


class Session:
    chat_count: int = 1
    last_timestamp: int = 0

    def __init__(self, _id):
        self.session_id = _id
        self.preset = default_preset
        self.conversation = []
        self.reset()
        self.token_record = []
        self.total_tokens = 0

    # 重置会话
    def reset(self):
        self.conversation = []

    # 重置人格
    def reset_preset(self):
        self.preset = default_preset

    # 设置人格
    def set_preset(self, msg: str) -> str:
        if msg in prompts:
            self.preset = prompts[msg]
        else:
            self.preset = msg.strip()
        self.reset()
        return self.preset

    # 导入用户会话
    def load_user_session(self, msg) -> str:
        import ast
        config = ast.literal_eval(msg)
        self.set_preset(config[0]['content'])
        self.conversation = config[1:]

        return f'导入会话: {len(self.conversation)}条\n' \
               f'导入人格: {self.preset}'

    # 导出用户会话
    def dump_user_session(self):
        logger.debug("dump session")
        return str([{"role": "system", "content": self.preset}] + self.conversation)

    # 会话
    async def get_chat_response(self, msg, is_admin) -> str:
        if openai_api_key == '':
            return f'无API Keys，请在配置文件或者环境变量中配置'

        def check_and_reset() -> bool:
            if is_admin:
                return False
            # 超过一天重置
            from datetime import datetime
            last = datetime.fromtimestamp(self.last_timestamp)
            now = datetime.fromtimestamp(time.time())
            delta = now - last
            if delta.days > 0:
                self.chat_count = 0

            # 一天之内检查次数
            if self.chat_count >= gpt3_chat_count_per_day:
                return True
            return False

        if check_and_reset():
            return f'每日聊天次数达到上限'

        import tiktoken
        encoding = tiktoken.encoding_for_model(gpt3_model)
        # 长度超过4096时，删除最早的一次会话
        while self.total_tokens + len(encoding.encode(msg)) > 4096 - gpt3_max_tokens:
            logger.debug("长度超过4096 - max_token，删除最早的一次会话")
            self.total_tokens -= self.token_record[0]
            del self.conversation[0]
            del self.token_record[0]

        res, ok = await get_chat_response(gpt3_proxy,
                                          openai_api_key,
                                          self.preset,
                                          self.conversation,
                                          msg)
        if ok:
            self.chat_count += 1
            self.last_timestamp = int(time.time())
            # 输入token数
            self.token_record.append(res['usage']['prompt_tokens'] - self.total_tokens)
            # 回答token数
            self.token_record.append(res['usage']['completion_tokens'])
            # 总token数
            self.total_tokens = res['usage']['total_tokens']

            logger.debug(res['usage'])
            logger.debug(self.token_record)
            return self.conversation[-1]['content']
        else:
            # 出现错误自动重置
            self.reset()
            return res


user_session: Dict[str, Session] = {
    public_sessionID: Session(public_sessionID)
}
user_lock = {}


def get_user_session(user_id) -> Session:
    if user_id not in user_session:
        user_session[user_id] = Session(user_id)

    if public_mode:
        return user_session[public_sessionID]
    else:
        return user_session[user_id]


async def handle_msg(resp: str) -> str or MessageSegment:
    # 如果开启图片渲染，且字数大于limit则会发送图片 (AI绘画人格始终发送文字方便复制)
    if (default_preset != prompts['AI绘画']) and gpt3_image_render and (len(resp) > gpt3_image_limit):
        if resp.count("```") % 2 != 0:
            resp += "\n```"
        from nonebot_plugin_htmlrender import md_to_pic
        img = await md_to_pic(resp)
        return MessageSegment.image(img)
    else:
        return resp


def checker(event: GroupMessageEvent) -> bool:
    return not event.sender.role == "member"


switch_mode = on_command("全局会话", priority=10, block=True, **need_at)


@switch_mode.handle()
async def _(matcher: Matcher, event: MessageEvent):
    if not checker(event):
        return

    global public_mode
    public_mode = not public_mode

    get_user_session(public_sessionID).reset()
    get_user_session(public_sessionID).reset_preset()

    if public_mode:
        await matcher.finish('已切换为全局会话')
    else:
        await matcher.finish('已关闭全局会话')


switch_img = on_command("图片渲染", priority=10, block=True, permission=SUPERUSER, **need_at)


@switch_img.handle()
async def _(matcher: Matcher):
    global gpt3_image_render
    gpt3_image_render = not gpt3_image_render

    if gpt3_image_render:
        await matcher.finish('图片渲染已打开')
    else:
        await matcher.finish('图片渲染已关闭')


reset_c = on_command("重置会话", priority=10, block=True, **need_at)


@reset_c.handle()
async def _(matcher: Matcher, event: MessageEvent):
    session_id = event.get_session_id()

    if public_mode:
        if not checker(event):
            await matcher.finish("公共模式下，仅管理员可以重置会话")
        get_user_session(public_sessionID).reset()
    else:
        get_user_session(session_id).reset()
    await matcher.finish("会话已重置")


now_model = on_command("当前模型", priority=10, block=True, **need_at)


@now_model.handle()
async def _(matcher: Matcher, event: MessageEvent):
    await matcher.finish(f"当前模型：{gpt3_model}")


now_preset = on_command("当前人格", priority=10, block=True, **need_at)


@now_preset.handle()
async def _(matcher: Matcher, event: MessageEvent):
    await matcher.finish(
        f"当前人格：{get_user_session(public_sessionID).preset if get_user_session(public_sessionID).preset else '无'} ")


all_preset = on_command("人格列表", aliases={"全部人格", "所有人格", "预设人格"}, priority=10, block=True)


@all_preset.handle()
async def _(matcher: Matcher, event: MessageEvent):
    resp = "\n\n".join(["**" + key + "**：" + value for key, value in prompts.items()])
    resp = await handle_msg(resp.replace("~", "\~"))  # 防止md格式渲染，萌新只会这样先简单处理了
    await matcher.send("/人格切换+名称" + resp, at_sender=True)


reset = on_command("重置人格", priority=10, block=True, **need_at)


@reset.handle()
async def _(matcher: Matcher, event: MessageEvent):
    session_id = event.get_session_id()

    if public_mode:
        if not checker(event):
            await matcher.finish("公共模式下，仅管理员可以重置人格")
        get_user_session(public_sessionID).reset_preset()
    else:
        get_user_session(session_id).reset_preset()

    await matcher.finish("人格已重置")


set_preset = on_command("设置人格", aliases={"人格设置", "人格", "人格切换"}, priority=10, block=True,
                        permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, **need_at)


@set_preset.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg:
        await matcher.finish("人格不能为空")

    global user_session
    user_session = {}

    global default_preset
    default_preset = get_user_session(public_sessionID).set_preset(msg)

    await matcher.finish(f"全局人格设置成功，当前人格：{get_user_session(public_sessionID).preset}")


# 连续聊天编辑人格预设文件
write_preset = on_command("编辑人格", priority=10, block=True, permission=SUPERUSER)


@write_preset.handle()
async def _(args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        write_preset.set_arg("prompt", message=args)


@write_preset.got("prompt", prompt="进入编辑人格预设文件模式：\n"
                                   "1.[预设]查看当前预设内容\n"
                                   "2.[更新 人格名 内容]覆写或追加人格\n"
                                   "3.[保存]保存当前预设内容并结束\n"
                                   "4.[退出]不保存任何更改并结束")
async def handle_chat(msg: str = ArgPlainText("prompt")):
    if msg.startswith('预设'):
        resp = "\n\n".join(["**" + key + "**：" + value for key, value in prompts.items()])
        resp = await handle_msg(resp.replace("~", "\~"))  # 防止md格式渲染，萌新只会这样先简单处理了
        await write_preset.reject_arg('prompt', resp)
    elif msg.startswith('更新'):
        parts = msg.split()
        if len(parts) == 3:
            prompts.update({parts[1]: parts[2]})
            await write_preset.reject_arg('prompt', '暂存' + parts[1] + '：' + parts[2])
        else:
            await write_preset.reject_arg('prompt', '格式错误，用空格分隔成三段文本')
    elif msg.startswith('保存'):
        with open('config/prompts.yml', 'w', encoding='utf-8') as file:
            yaml.dump(prompts, file, allow_unicode=True, default_style="'")  # 键值两侧加单引号
        resp = "\n\n".join(["**" + key + "**：" + value for key, value in prompts.items()])
        resp = await handle_msg(resp.replace("~", "\~"))  # 防止md格式渲染，萌新只会这样先简单处理了
        await write_preset.finish(resp + "保存人格成功！")
    elif msg.startswith('退出'):
        await write_preset.finish('未保存任何更改')


load = on_command("导入会话", priority=10, block=True, **need_at)


@load.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()
    await matcher.finish(MessageSegment.reply(event.message_id) + get_user_session(session_id).load_user_session(msg))


dump = on_command("导出会话", priority=10, block=True, **need_at)


@dump.handle()
async def _(matcher: Matcher, event: MessageEvent):
    session_id = event.get_session_id()
    await matcher.finish(MessageSegment.reply(event.message_id) + get_user_session(session_id).dump_user_session())


switch = on_command("切换会话", aliases={"切换"}, priority=10, block=True, **need_at)


@switch.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()

    if not msg.isnumeric():
        await switch.finish('切换失败')

    import re
    # 私 -> 群
    # 群 -> 群
    if isinstance(event, GroupMessageEvent):
        new_session_id = re.sub(r'_(\d+)_', f'_{msg}_', session_id)
    else:
        new_session_id = f'group_{msg}_{session_id}'

    user_session[new_session_id] = get_user_session(session_id)
    logger.debug(f'切换会话 {session_id} -> {new_session_id}')
    await switch.finish('切换成功')


# 基本聊天
gpt3 = on_command(priority=100, block=True, **matcher_params)


@gpt3.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()

    if not msg:
        return

    if session_id in user_lock and user_lock[session_id]:
        await matcher.finish("消息太快啦～请稍后，或发送[/解锁]解除用户锁", at_sender=True)

    user_lock[session_id] = True
    resp = await get_user_session(session_id).get_chat_response(msg, checker(event))
    resp = await handle_msg(resp)

    # 发送消息
    # 如果是私聊直接发送
    if isinstance(event, PrivateMessageEvent):
        await matcher.send(resp, at_sender=True)
    else:
        # 如果不是则以回复的形式发送
        message_id = event.message_id
        await matcher.send(MessageSegment.reply(message_id) + resp, at_sender=True)
    user_lock[session_id] = False


unlock = on_command("解锁", aliases={"unlock"}, priority=10, block=True)


@unlock.handle()
async def _(matcher: Matcher, event: MessageEvent):
    user_lock[event.get_session_id()] = False
    await matcher.finish("解锁成功～可以继续对话啦", at_sender=True)


# 连续聊天
chat_gpt3 = on_command("开始聊天", aliases={"聊天", '聊天开始'}, priority=10, block=True, **need_at)
end_conversation = ['stop', '结束', '聊天结束', '结束聊天']
reset_p = ['重置人格', '人格重置']
reset = ['重置', '重置会话']


@chat_gpt3.handle()
async def _(args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        chat_gpt3.set_arg("prompt", message=args)


@chat_gpt3.got("prompt", prompt="聊天开始...")
async def handle_chat(event: MessageEvent, prompt: Message = Arg(), msg: str = ArgPlainText("prompt")):
    session_id = event.get_session_id()

    if msg in reset_p:
        get_user_session(session_id).reset_preset()
        await chat_gpt3.reject_arg('prompt', '人格已重置')
    elif msg in reset:
        get_user_session(session_id).reset()
        await chat_gpt3.reject_arg('prompt', '会话已重置')

    if msg not in end_conversation:
        resp = await get_user_session(session_id).get_chat_response(msg, checker(event))
        resp = await handle_msg(resp)

        # 如果是私聊直接发送
        if isinstance(event, PrivateMessageEvent):
            await chat_gpt3.reject_arg('prompt', resp)
        else:
            # 如果不是则以回复的形式发送
            message_id = event.message_id
            await chat_gpt3.reject_arg('prompt', MessageSegment.reply(message_id) + resp)

    await chat_gpt3.finish('聊天结束...')

# for test
# @driver.on_startup
# async def _():
#     bot = Session(0)
#     res = await bot.get_chat_response('你好, 我叫chris', True)
#     print(res)
#     a = await bot.get_chat_response('写一个反转二叉树', True)
#     print(res)
#     exit(0)
