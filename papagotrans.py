import os
import json
import urllib.request
import urllib.parse


class Translator:
    def __init__(self):
        self.client_id = os.environ.get('PAPAGO_CLIENT_ID')
        self.client_secret = os.environ.get('PAPAGO_CLIENT_SECRET')
        self.url = "https://openapi.naver.com/v1/papago/n2mt"

    def translate(self, text: str, dest='en', src='ko'):
        data = f"source={src}&target={dest}&text={urllib.parse.quote(text)}"
        request = urllib.request.Request(self.url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            result = Translated(src=src, dest=dest, text=data["message"]["result"]["translatedText"])
            return result
        else:
            raise ValueError("Error Code:" + rescode)


class Translated:
    def __init__(self, src, dest, text):
        self.src = src
        self.dest = dest
        self.text = text
