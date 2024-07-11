from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from app.services import paper_service
from app.api.paper.endpoints import searchPopularKeyword

async def scheduled_job():
    try:
        # 인기 검색어를 가져와 arXiv에서 검색
        search_results = await searchPopularKeyword()

        for result in search_results['data']:
            keyword_data = result
            await paper_service.saveWea(keyword_data)
    except Exception as e:
        print(f'Error in scheduled job: {e}')

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_job,
        trigger=CronTrigger(day_of_week='sun', hour=0, minute=0),  # 매주 일요일 자정에 실행
        id='weekly_job',
        replace_existing=True
    )
    scheduler.start()
