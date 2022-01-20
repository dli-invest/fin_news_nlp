import json
import requests
import time

def post_webhook_content(url, data: dict):
    try:
        result = requests.post(
            url, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        if status_code == 429:
            print("Rate limited by discord")
            # wait for a minute
            time.sleep(60)
            post_webhook_content(url, data)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
