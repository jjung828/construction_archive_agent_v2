from apscheduler.schedulers.blocking import BlockingScheduler
from main import main

scheduler = BlockingScheduler(timezone="Asia/Seoul")

# 매일 자정, 정오 실행
scheduler.add_job(main, "cron", hour="0,12", minute=0)

print("Scheduler started.")
print("Runs every day at 00:00 and 12:00 Asia/Seoul.")
print("Do not close this terminal if you want automatic collection.")
scheduler.start()