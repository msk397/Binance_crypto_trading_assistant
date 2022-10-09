import json

import requests


def bark(title,mess,barkUrl,barkKey):
    response = requests.post(
        url=barkUrl,
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        proxies={'https': 'http://127.0.0.1:7890'},
        data=json.dumps({
                "body": mess,
                "device_key": barkKey,
                "title": title,
        })
    )
    response.close()
