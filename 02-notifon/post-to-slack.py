# coding: utf-8
import requests
# url is our secret value
url = ''
data = { "text": "Hello, world." }
requests.post(url, json=data)
