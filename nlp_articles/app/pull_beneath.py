import asyncio
import os
import beneath
import json

async def callback(record):
    print(record)

async def main():
    beneathKey = os.getenv("BENEATH_SECRET")
    client = beneath.Client(secret=beneathKey)
    table = await client.find_table("examples/reddit/r-wallstreetbets-posts")
    table_instance = await table.find_instances()
    first_instance = table_instance[0]
    filter = json.dumps({"created_on": { "_gte": "2021-03-09", "_lt": "2021-03-16"}})
    cursor = await first_instance.query_index(filter=filter)
    records = await cursor.read_all()
    print(records)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())