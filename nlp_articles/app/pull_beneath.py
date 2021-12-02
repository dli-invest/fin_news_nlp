import asyncio
import os
import beneath
import json
from datetime import datetime, timedelta

async def callback(record):
    print(record)

async def main():
    beneathKey = os.getenv("BENEATH_SECRET")
    client = beneath.Client(secret=beneathKey)
    table = await client.find_table("examples/reddit/r-wallstreetbets-posts")
    table_instance = await table.find_instances()
    first_instance = table_instance[0]

    start_date = datetime.today() - timedelta(hours=0, minutes=50)
    start_time_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
    filter = json.dumps({"created_on": { "_gte": start_time_str, "_lt": end_time_str}})
    cursor = await first_instance.query_index(filter=filter)
    records = await cursor.read_all()
    print(records)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())