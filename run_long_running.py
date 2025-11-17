# run_long_running.py
import time
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.services.session_service import SessionService
from src.services.logger_service import LoggerService
from run_cycle_sessions import main as cycle_once

def long_running(interval=30):
    logger = LoggerService()
    logger.log("Long-running agent started.", agent="LongRunner")

    while True:
        logger.log("Tick: checking for active sessions...", agent="LongRunner")
        cycle_once()  # attempt session cycle
        time.sleep(interval)

if __name__ == "__main__":
    long_running(interval=60)
