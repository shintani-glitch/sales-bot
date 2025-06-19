# rakuten_api.py
import requests
import config

def search_items(keyword):
    """楽天APIで商品を検索し、結果を返す"""
    endpoint = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": config.RAKUTEN_APP_ID,
        "affiliateId": config.RAKUTEN_AFFILIATE_ID,
        "keyword": keyword,
        "sort": "-reviewAverage",
        "hits": 30,
        "format": "json",
        "imageFlag": 1
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json().get("Items", [])
    except requests.exceptions.RequestException as e:
        print(f"楽天APIリクエストエラー: {e}")
        return []
