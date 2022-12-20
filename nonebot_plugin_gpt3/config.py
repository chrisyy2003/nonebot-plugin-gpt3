import asyncio
from pydantic import BaseSettings
from nonebot import get_driver
from nonebot.rule import to_me
import yaml
from pathlib import Path

class Config(BaseSettings):
    # Your Config Here
    chatgpt_api_key_path: str = "config/chatgpt_api_key.yml"
    chatgpt_command_prefix: str = '.'
    chatgpt_need_at: bool = True
    chatgpt_image_render: bool = False
    chatgpt_image_limit: int = 100


    class Config:
        extra = "ignore"

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

chatgpt_api_keys_path = config.chatgpt_api_key_path
chatgpt_command_prefix = config.chatgpt_command_prefix
chatgpt_need_at = config.chatgpt_need_at
chatgpt_image_render = config.chatgpt_image_render
chatgpt_image_limit = config.chatgpt_image_limit


# 如果不存在则创建
LOCAL = Path() / "config"
LOCAL.mkdir(exist_ok=True)
if not Path(chatgpt_api_keys_path).exists():
    with open(chatgpt_api_keys_path, 'w', encoding='utf-8') as f:
        yaml.dump({"api_keys": []}, f, allow_unicode=True)

with open(chatgpt_api_keys_path, 'r', encoding='utf-8') as f:
    api_key_list = yaml.load(f, Loader=yaml.FullLoader).get('api_keys')

from nonebot.log import logger
logger.info(f"加载 {len(api_key_list)}个 APIKeys")
matcher_params = {}
matcher_params['cmd'] = chatgpt_command_prefix
if chatgpt_need_at:
    matcher_params['rule'] = to_me()
