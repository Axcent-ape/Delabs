import random
import datetime

from data import config
from src.utils import logger, random_line, get_all_lines
from src import Delabs
import pandas as pd


async def DailyDelab(thread: int):
    logger.info(f"Thread {thread} | Start work")
    while True:
        act = await random_line('data/accounts.txt')
        if not act: break

        if '::' in act:
            private_key, proxy = act.split('::')
        else:
            private_key = act
            proxy = None

        delabs = Delabs(key=private_key, thread=thread, proxy=proxy)

        if await delabs.login():
            if await delabs.set_referrer():
                logger.success(f"Thread {thread} | Set referral code {config.REF_CODE}! Address: {delabs.web3_utils.acct.address}")

            if await delabs.check_in():
                logger.success(f"Thread {thread} | Completed daily check in! Address: {delabs.web3_utils.acct.address}")
            else:
                logger.warning(f"Thread {thread} | Already completed daily check in! Address: {delabs.web3_utils.acct.address}")

            if await delabs.draw():
                logger.success(f"Thread {thread} | Completed daily draw! Address: {delabs.web3_utils.acct.address}")
            else:
                logger.warning(f"Thread {thread} | Already completed daily draw! Address: {delabs.web3_utils.acct.address}")

        await delabs.sleep(random.uniform(config.DELAY[0], config.DELAY[1]))
        await delabs.logout()

    logger.info(f"Thread {thread} | Finish work")


async def StatsDelay():
    accounts = get_all_lines('data/accounts.txt')
    if not accounts:
        logger.warning(f"No accounts in data/accounts.txt")
        return

    data = []
    for num, account in enumerate(accounts):
        if '::' in account:
            private_key, proxy = account.split('::')
        else:
            private_key = account
            proxy = None

        delabs = Delabs(key=private_key, thread=-1, proxy=proxy)

        if await delabs.login():
            user_stats = await delabs.get_user_info()
            data.append(user_stats)
        await delabs.logout()
        logger.info(f"{num+1}/{len(accounts)} | Compiled stats for {delabs.web3_utils.acct.address}")

    time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = f"data/statistics_{time}.csv"

    columns = ['Address', 'Referral Count', 'Total Points', 'Referral Code']
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False)

    logger.success(f"Saved statistics to {path}")
