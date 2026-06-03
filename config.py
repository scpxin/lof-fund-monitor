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
    
    # 爬虫配置
    LOF_FUND_CODES = [
        "161706",  # 招商优质成长混合 (LOF)
        "163406",  # 兴全合润混合 (LOF)
        "162605",  # 景顺长城鼎益混合 (LOF)
        "160060",  # 华夏行业混合 (LOF)
        "166006",  # 中欧中小盘股票 (LOF)
        "161725",  # 招商中证白酒指数 (LOF)
        "164905",  # 交银国证新能源指数 (LOF)
        "165519",  # 中信保诚环保产业 (LOF)
        "168204",  # 中融国证钢铁行业 (LOF)
        "169010",  # 长信成长优选混合 (LOF)
        "161109",  # 易方达中小板指数 (LOF)
        "160716",  # 嘉实基本面 50 指数 (LOF)
        "163109",  # 申万菱信深证成指 (LOF)
        "164809",  # 工银沪深 300 指数 (LOF)
        "165309",  # 工银沪深 300ETF 联接 (LOF)
        "160119",  # 南方中证 500ETF 联接 (LOF)
        "167601",  # 国金沪深 300 指数增强 (LOF)
        "163821",  # 中银沪深 300 等权重指数 (LOF)
        "165806",  # 东吴沪深 300 指数 (LOF)
        "161207",  # 国投瑞银沪深 300 金融地产 (LOF)
        "161211",  # 国投瑞银瑞和沪深 300 指数 (LOF)
        "161213",  # 国投瑞银和瑞混合 (LOF)
        "161217",  # 国投瑞银中证上游资源产业 (LOF)
        "161219",  # 国投瑞银新兴产业混合 (LOF)
        "161224",  # 国投瑞银白银 (LOF)
        "161225",  # 国投瑞银瑞盈混合 (LOF)
        "161227",  # 国投瑞银瑞福深证 100 指数 (LOF)
        "161229",  # 国投瑞银研究精选股票 (LOF)
        "161607",  # 融通深证 100 指数 (LOF)
        "161810",  # 银华内需主题混合 (LOF)
    ]
    
    # 溢价率阈值（超过此值才推送）
    _premium = os.getenv("PREMIUM_RATE_THRESHOLD", "1.0")
    PREMIUM_RATE_THRESHOLD = float(_premium) if _premium else 1.0
    
    # 推送时间（24 小时制）
    # 注意：GitHub Actions 模式下，此配置不生效，推送时间由 workflow 文件定义
    PUSH_TIME = os.getenv("PUSH_TIME", "15:30")
