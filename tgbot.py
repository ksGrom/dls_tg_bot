import os
import asyncio
import subprocess
import time
from dotenv import load_dotenv

COMMANDS = {
    # 'start': start,
    #
}

load_dotenv()
TG_TOKEN = os.getenv("BOT_TOKEN")


async def run_fastapi():
    pass


async def main():
    task1 = asyncio.create_task(run_fastapi())
    await task1


if __name__ == '__main__':
    p = subprocess.Popen('uvicorn main:app --port 8000 --host 0.0.0.0')
    i = 0
    while True:
        i += 1
        time.sleep(1)
    # p.terminate()
