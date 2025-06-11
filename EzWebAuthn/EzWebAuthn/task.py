import os
import time

import schedule


def job():
    os.system("python3 db.py init")


schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
