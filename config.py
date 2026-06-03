import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def _parse_list(env_var: str, default: list) -> list:
        """解析环境变量中的列表"""
        value = os.getenv(env_var, "")
        if value:
            try:
                return json.loads(value)
            except:
                return value.split(",")
        return default
    
    # 微信推送配置（二选一）
    SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY", "")  # Server 酱 SCKEY
    PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN", "")  # PushPlus token
    
    # 推送方式选择：server_chan 或 push_plus
    PUSH_METHOD = os.getenv("PUSH_METHOD", "server_chan")
    
    # 溢价率阈值（超过此值才推送）
    _premium = os.getenv("PREMIUM_RATE_THRESHOLD", "1.0")
    PREMIUM_RATE_THRESHOLD = float(_premium) if _premium else 1.0
    
    # 推送时间（24 小时制）
    # 注意：GitHub Actions 模式下，此配置不生效，推送时间由 workflow 文件定义
    PUSH_TIME = os.getenv("PUSH_TIME", "15:30")
