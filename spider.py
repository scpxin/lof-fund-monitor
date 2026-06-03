import requests
from datetime import datetime
from typing import List, Dict


class LOFFundSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*",
            "Referer": "https://palmmicro.com/woody/res/lofcn.php"
        }
    
    def get_all_lof_data(self) -> List[Dict]:
        """从 palmmicro 获取 LOF 基金溢价率数据"""
        try:
            url = "https://palmmicro.com/woody/res/lofcn.php?sort=premium"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            funds = []
            
            for item in data:
                try:
                    fund = {
                        "fund_code": item.get("基金代码", ""),
                        "fund_name": item.get("基金名称", ""),
                        "price": float(item.get("成交价", 0) or 0),
                        "nav": float(item.get("净值", 0) or 0),
                        "premium_rate": float(item.get("溢价率 (%)", 0) or 0),
                        "iopv": float(item.get("估值参考价", 0) or 0),
                        "limit": item.get("申购状态", "") or item.get("状态", "开放"),
                        "change_rate": float(item.get("涨幅 (%)", 0) or 0),
                        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    funds.append(fund)
                except (ValueError, TypeError, KeyError) as e:
                    print(f"解析基金数据失败：{e}")
                    continue
            
            print(f"获取到 {len(funds)} 只基金")
            return funds
        except Exception as e:
            print(f"获取 LOF 数据失败：{e}")
            return []
    
    def get_premium_funds(self, threshold: float = 1.0) -> List[Dict]:
        """获取超过阈值的基金"""
        all_funds = self.get_all_lof_data()
        
        # 筛选超过阈值的基金
        filtered = []
        for fund in all_funds:
            premium_rate = fund.get("premium_rate", 0)
            if abs(premium_rate) >= threshold:
                filtered.append(fund)
        
        # 按溢价率绝对值排序
        filtered.sort(key=lambda x: abs(x.get("premium_rate", 0)), reverse=True)
        return filtered
