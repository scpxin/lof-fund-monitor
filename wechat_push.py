import requests
import json
from typing import List, Dict
from datetime import datetime


class WeChatPush:
    def __init__(self, server_chan_key: str = "", push_plus_token: str = ""):
        self.server_chan_key = server_chan_key
        self.push_plus_token = push_plus_token
    
    def push_server_chan(self, title: str, content: str) -> bool:
        """使用 Server 酱推送"""
        if not self.server_chan_key:
            print("Server 酱 KEY 未配置")
            return False
        
        try:
            url = f"https://sctapi.ftqq.com/{self.server_chan_key}.send"
            data = {
                "title": title,
                "desp": content
            }
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                print("Server 酱推送成功")
                return True
            else:
                print(f"Server 酱推送失败：{result.get('message', '')}")
                return False
        except Exception as e:
            print(f"Server 酱推送异常：{e}")
            return False
    
    def push_push_plus(self, title: str, content: str) -> bool:
        """使用 PushPlus 推送"""
        if not self.push_plus_token:
            print("PushPlus TOKEN 未配置")
            return False
        
        try:
            url = "http://www.pushplus.plus/send"
            data = {
                "token": self.push_plus_token,
                "title": title,
                "content": content,
                "template": "markdown"
            }
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 200:
                print("PushPlus 推送成功")
                return True
            else:
                print(f"PushPlus 推送失败：{result.get('msg', '')}")
                return False
        except Exception as e:
            print(f"PushPlus 推送异常：{e}")
            return False
    
    def format_fund_message(self, funds: List[Dict]) -> str:
        """格式化基金消息为 Markdown"""
        if not funds:
            return "今日无符合条件的基金数据"
        
        message = f"""## LOF 基金溢价监控日报
**更新时间：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**数据条数：** {len(funds)}

### 溢价率排名

| 代码 | 名称 | 市价 | 净值 | 溢价率 | 申购限额 |
|------|------|------|------|--------|----------|
"""
        for fund in funds[:20]:
            premium_rate = fund.get("premium_rate", 0)
            rate_str = f"{premium_rate:+.2f}%"
            
            message += f"| {fund.get('fund_code', '')} | {fund.get('fund_name', '')} | {fund.get('price', 0):.3f} | {fund.get('nav', 0):.3f} | {rate_str} | {fund.get('limit', '未披露')} |\n"
        
        if len(funds) > 20:
            message += f"\n... 还有 {len(funds) - 20} 只基金，详见完整报告"
        
        message += "\n\n---\n数据来源：palmmicro.com"
        return message
    
    def format_single_fund_alert(self, fund: Dict) -> str:
        """格式化单只基金预警消息"""
        premium_rate = fund.get("premium_rate", 0)
        alert_level = "高溢价预警" if premium_rate > 3 else "折价机会" if premium_rate < -1 else "溢价提示"
        
        return f"""## {alert_level}
**代码：** {fund.get('fund_code', '')}
**名称：** {fund.get('fund_name', '')}
**溢价率：** {premium_rate:+.2f}%
**市价：** {fund.get('market_price', 0):.3f}
**净值：** {fund.get('net_value', 0):.3f}
**申购限额：** {fund.get('limit', '未披露')}

⚠️ 请注意风险，谨慎投资！
"""
    
    def push(self, funds: List[Dict], method: str = "server_chan") -> bool:
        """推送到微信"""
        title = f"LOF 基金溢价监控 - {len(funds)}只基金"
        content = self.format_fund_message(funds)
        
        if method == "push_plus":
            return self.push_push_plus(title, content)
        else:
            return self.push_server_chan(title, content)
    
    def push_alert(self, fund: Dict, method: str = "server_chan") -> bool:
        """推送单只基金预警"""
        premium_rate = fund.get("premium_rate", 0)
        title = f"{fund.get('fund_name', '')} 溢价{premium_rate:+.2f}%"
        content = self.format_single_fund_alert(fund)
        
        if method == "push_plus":
            return self.push_push_plus(title, content)
        else:
            return self.push_server_chan(title, content)
