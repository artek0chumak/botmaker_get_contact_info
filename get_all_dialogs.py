import aiohttp
import asyncio
import datetime
import os
import pandas as pd

from tqdm import tqdm


async def get_response(url, headers, sem):
    async with sem:
        async with aiohttp.ClientSession() as session:
            tries = 10
            while tries > 0:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    tries -= 1
                    await asyncio.sleep(10)


async def get_messages(
    access_token, days_range, hours_range, minutes_range, current_time
):
    url = "https://go.botmaker.com/api/v1.0/message/byDateRange"
    tasks = []
    sem = asyncio.Semaphore(10)
    for days in days_range:
        for hours in hours_range:
            for minutes in minutes_range:
                time_to = current_time - datetime.timedelta(days=days, hours=hours, minutes=minutes)
                time_from = current_time - datetime.timedelta(days=days, hours=hours, minutes=minutes + 15)
                headers={
                    'access-token': access_token,
                    'dateISOFrom': time_from.isoformat() + ".00Z",
                    'dateISOTo': time_to.isoformat() + ".00Z",
                    "chatPlatform": "TELEGRAM",
                }
                task = asyncio.create_task(get_response(url, headers, sem))
                tasks.append((time_from, time_to, task))
    
    result = []
    for time_from, time_to, task in tasks:
        await task
        done_task = task.result()
        if done_task["messages"]:
            print(f"From {time_from.isoformat()} to {time_to.isoformat()}  has {len(done_task['messages']):-4} messages")
            result.extend(done_task["messages"])

    return result


async def get_contact_info(access_token, contact_ids):
    url = "https://go.botmaker.com/api/v1.0/customer"
    tasks = []
    sem = asyncio.Semaphore(2)
    for contact_id in contact_ids:
        headers={
            'access-token': access_token,
            "chatPlatform": "TELEGRAM",
            "platformContactId": contact_id,
        }
        task = asyncio.create_task(get_response(url, headers, sem))
        tasks.append((contact_id, task))

    result = []
    for contact_id, task in tqdm(tasks):
        try:
            await task
            done_task = task.result()
            if done_task:
                result.append(done_task)
            else:
                print(f"Nothing for {contact_id}")
        except:
            print(f"Error for {contact_id}")
            pass

    return result


async def main():
    access_token = os.environ["BOTMAKER_ACCESS_TOKEN"]
    days_range = range(14, 7, -1)
    hours_range = range(0, 24)
    minutes_range = [0, 15, 30, 45]
    current_time = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    messages = await get_messages(access_token, days_range, hours_range, minutes_range, current_time)

    all_messages = pd.DataFrame(messages)
    all_messages.to_csv("all_messages.csv")

    all_contact_ids = all_messages["contactId"].unique()
    
    info = await get_contact_info(access_token, all_contact_ids)
    all_info = pd.DataFrame(info)
    all_info.to_csv("all_info.csv")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
