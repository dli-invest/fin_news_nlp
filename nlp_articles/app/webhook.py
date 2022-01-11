import json
import requests
def post_webhook_content(url, data: dict):
    try:
        result = requests.post(
            url, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        # convert data to raw bytes
        # send raw bytes to discord as file
        try:
            requests.post(
                url,
                files={"file": ("file.json", json.dumps(data).encode("utf-8"))},
                headers={
                    "Content-Type": "multipart/form-data",
                }
            )
        except requests.exceptions.HTTPError as err:
            print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
