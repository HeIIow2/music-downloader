import requests

API_ENDPOINT = "https://slavart.gamesdrive.net/api/search?q=Tekkno"
DOWNLOAD_ENDPOINT = "https://slavart-api.gamesdrive.net/api/download/track?id=153182274"


if __name__ == "__main__":
    r = requests.get(DOWNLOAD_ENDPOINT, headers={
        "Access-Control-Allow-Origin": "https://slavart.gamesdrive.net/"
    })
    print(r.status_code)
    print(r.text)
