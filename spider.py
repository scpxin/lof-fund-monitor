import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional


class LOFFundSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*"
        }
        
    def get_fund_basic_info(self, fund_code: str) -> Optional[Dict]:
        """从天天基金获取基金基本信息（净值、申购状态等）"""
        try:
            url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            content = response.text.strip()
            if content.startswith("jsonpgz(") and content.endswith(")"):
                content = content[8:-1]
            
            data = eval(content)
            return {
                "fund_code": data.get("fundcode", ""),
                "fund_name": data.get("name", ""),
                "net_value": data.get("gsz", ""),
                "net_value_date": data.get("gztime", ""),
                "nav_1day_change": data.get("gszzl", ""),
            }
        except Exception as e:
            print(f"获取基金 {fund_code} 基础信息失败：{e}")
            return None
    
    def get_fund_market_data(self, fund_code: str) -> Optional[Dict]:
        """从东方财富获取 LOF 基金市场交易数据（市价、溢价率等）"""
        try:
            url = f"https://push2ex.eastmoney.com/GetFullFundInfoAll"
            params = {
                "id": fund_code,
                "cb": "jQuery"
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            content = response.text.strip()
            if content.startswith("jQuery(") and content.endswith(")"):
                content = content[7:-1]
            
            data = eval(content)
            fund_info = data.get("data", {}).get("fundinfo", {})
            
            return {
                "market_price": fund_info.get("npv", ""),
                "volume": fund_info.get("vol", ""),
                "turnover_rate": fund_info.get("hsl", ""),
            }
        except Exception as e:
            print(f"获取基金 {fund_code} 市场数据失败：{e}")
            return None
    
    def get_lof_list(self) -> List[Dict]:
        """获取所有 LOF 基金溢价率数据"""
        try:
            url = "https://www.jisilu.cn/data/lof/"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            table = soup.find("table", {"id": "lof_data"})
            if not table:
                table = soup.find("table")
            
            funds = []
            if table:
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                    for row in rows:
                        cols = row.find_all("td")
                        if len(cols) >= 8:
                            try:
                                fund = {
                                    "fund_code": cols[1].text.strip(),
                                    "fund_name": cols[2].text.strip(),
                                    "price": float(cols[3].text.strip().replace("--", "0") or 0),
                                    "nav": float(cols[4].text.strip().replace("--", "0") or 0),
                                    "premium_rate": float(cols[5].text.strip().replace("--", "0") or 0),
                                    "iopv": float(cols[6].text.strip().replace("--", "0") or 0),
                                    "premium_rate_1y": float(cols[7].text.strip().replace("--", "0") or 0),
                                }
                                funds.append(fund)
                            except (ValueError, IndexError):
                                continue
            return funds
        except Exception as e:
            print(f"获取 LOF 列表失败：{e}")
            return []
    
    def get_fund_limit(self, fund_code: str) -> str:
        """获取基金申购限额信息"""
        try:
            url = f"https://api.fund.eastmoney.com/f10/lsjz"
            params = {
                "fundcode": fund_code,
                "pageIndex": 1,
                "pageSize": 1,
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and data.get("Data"):
                fund_data = data.get("Data", {})
                limit = fund_data.get("SGZT", "") or fund_data.get("SGZT", "未披露")
                return limit if limit else "未披露"
            return "未披露"
        except Exception as e:
            print(f"获取基金 {fund_code} 申购限额失败：{e}")
            return "未披露"
    
    def get_premium_funds(self, fund_codes: List[str], threshold: float = 1.0) -> List[Dict]:
        """获取超过阈值的高溢价基金"""
        funds_data = []
        
        for code in fund_codes:
            try:
                basic_info = self.get_fund_basic_info(code)
                market_data = self.get_fund_market_data(code)
                limit_info = self.get_fund_limit(code)
                
                if basic_info:
                    net_value = float(basic_info.get("net_value", 0) or 0)
                    market_price = float(market_data.get("market_price", 0) if market_data else 0)
                    
                    if net_value > 0 and market_price > 0:
                        premium_rate = ((market_price - net_value) / net_value) * 100
                        
                        if abs(premium_rate) >= threshold:
                            funds_data.append({
                                "fund_code": code,
                                "fund_name": basic_info.get("fund_name", ""),
                                "market_price": market_price,
                                "net_value": net_value,
                                "premium_rate": round(premium_rate, 2),
                                "limit": limit_info,
                                "update_time": basic_info.get("net_value_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            })
            except Exception as e:
                print(f"处理基金 {code} 数据失败：{e}")
                continue
        
        funds_data.sort(key=lambda x: abs(x["premium_rate"]), reverse=True)
        return funds_data
    
    def get_all_lof_data(self, threshold: float = 0) -> pd.DataFrame:
        """获取所有 LOF 数据并返回 DataFrame"""
        funds = self.get_lof_list()
        
        if threshold > 0:
            funds = [f for f in funds if abs(f["premium_rate"]) >= threshold]
        
        return pd.DataFrame(funds)
