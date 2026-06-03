from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from spider import LOFFundSpider
from wechat_push import WeChatPush
from config import Config


class FundMonitorScheduler:
    def __init__(self):
        self.spider = LOFFundSpider()
        self.pusher = WeChatPush(
            server_chan_key=Config.SERVER_CHAN_KEY,
            push_plus_token=Config.PUSH_PLUS_TOKEN
        )
        self.scheduler = BlockingScheduler()
    
    def daily_report_job(self):
        """每日定时推送任务"""
        print(f"[{datetime.now()}] 开始执行每日推送任务...")
        
        try:
            funds = self.spider.get_premium_funds(
                Config.LOF_FUND_CODES,
                Config.PREMIUM_RATE_THRESHOLD
            )
            
            if funds:
                self.pusher.push(funds, Config.PUSH_METHOD)
                print(f"推送成功，共{len(funds)}只基金")
            else:
                print("没有符合条件的基金数据")
        except Exception as e:
            print(f"执行任务失败：{e}")
    
    def schedule_daily(self, hour: int = 15, minute: int = 30):
        """设置每日定时任务"""
        self.scheduler.add_job(
            self.daily_report_job,
            CronTrigger(hour=hour, minute=minute),
            id="daily_report",
            name="LOF 基金每日推送"
        )
        print(f"已设置每日 {hour}:{minute:02d} 自动推送")
    
    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("调度器已停止")


def run_once():
    """立即运行一次（用于测试）"""
    spider = LOFFundSpider()
    pusher = WeChatPush(
        server_chan_key=Config.SERVER_CHAN_KEY,
        push_plus_token=Config.PUSH_PLUS_TOKEN
    )
    
    print("获取基金数据中...")
    funds = spider.get_premium_funds(
        Config.LOF_FUND_CODES,
        Config.PREMIUM_RATE_THRESHOLD
    )
    
    if funds:
        print(f"获取到 {len(funds)} 只基金数据")
        pusher.push(funds, Config.PUSH_METHOD)
    else:
        print("没有符合条件的基金数据")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        scheduler = FundMonitorScheduler()
        
        time_parts = Config.PUSH_TIME.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        scheduler.schedule_daily(hour, minute)
        print("LOF 基金监控系统已启动，按 Ctrl+C 停止")
        scheduler.start()
