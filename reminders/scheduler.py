from reminders.database import r
from reminders.objects import Job
from reminders.config import logger

import time
from datetime import datetime

def run():
    logger.debug("Scheduler thread started")
    while True:
        now = datetime.now()
        ts = int(time.mktime(now.timetuple()))
        jobs = r.zrangebyscore("jobs", "-inf", ts)

        if len(jobs):
            for job in jobs:
                Job.from_config_key(r, job).execute(r)
                r.zrem("jobs", job)
            logger.debug("Executed %d jobs" % len(jobs))

        time.sleep(1)

if __name__ == '__main__':
    run()
