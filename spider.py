import requests
from datetime import datetime
from typing import List, Dict


class LOFFundSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://quote.eastmoney.com/"
        }
    
    def get_all_lof_data(self) -> List[Dict]:
        """从东方财富获取 LOF 基金实时数据"""
        try:
            # 东方财富 LOF 行情中心
            url = "https://63.push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": "500",
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf4c27f5e7810589",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0 LOF,m:1 LOF",
                "fields": "f12,f14,f2,f8,f15,f16,f17",
                "_": int(datetime.now().timestamp() * 1000)
            }
            
            print(f"请求 URL: {url}")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            print(f"响应状态码：{response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            print(f"返回数据：{data}")
            
            if not data.get("data"):
                print("警告：没有返回数据")
                return []
            
            funds = []
            
            for item in data.get("data", {}).get("diff", []):
                try:
                    fund_code = item.get("f12", "")
                    fund_name = item.get("f14", "")
                    price = item.get("f2", 0)  # 最新价
                    change_rate = item.get("f3", 0)  # 涨跌幅
                    premium_rate = item.get("f8", 0)  # 溢价率
                    discount_rate = item.get("f15", 0)  # 折价率
                    high = item.get("f16", 0)
                    low = item.get("f17", 0)
                    
                    # 估算净值（根据涨跌幅推算）
                    if price and price > 0 and change_rate:
                        nav = price / (1 + change_rate / 100)
                    else:
                        nav = price
                    
                    fund = {
                        "fund_code": fund_code,
                        "fund_name": fund_name,
                        "price": float(price) if price is not None else 0,
                        "nav": float(nav) if nav is not None else 0,
                        "premium_rate": float(premium_rate) if premium_rate is not None else 0,
                        "discount_rate": float(discount_rate) if discount_rate is not None else 0,
                        "limit": "未知",
                        "change_rate": float(change_rate) if change_rate is not None else 0,
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
