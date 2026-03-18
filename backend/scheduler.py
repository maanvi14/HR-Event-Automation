from apscheduler.schedulers.blocking import BlockingScheduler
from backend.main import run_events

scheduler = BlockingScheduler()


scheduler.add_job(run_events, "cron", hour=9)

print("Scheduler running...")

scheduler.start()