import asyncio
from src import StatsDelay, DailyDelab


async def main():
    print("Soft's author: https://t.me/ApeCryptor")

    action = int(input("\nSelect action:\n1. Start claimer\n2. Get statistics\n\n> "))

    if action == 2:
        await StatsDelay()
    elif action == 1:
        thread_count = int(input("Input count of threads: "))

        tasks = []
        for thread in range(1, thread_count+1):
            tasks.append(asyncio.create_task(DailyDelab(thread)))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
