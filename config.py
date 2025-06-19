# config.py
import os
from datetime import datetime, timezone, timedelta

# --- API & DB設定 (Renderの環境変数から取得) ---
# この部分は変更ありません。
RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")


# ★★★ ここからがオールジャンル版の変更点 ★★★

# --- 検索キーワード (オールジャンル対応) ---
# 特定の製品名ではなく、楽天のランキングや広範なカテゴリで検索します。
# これにより、予期せぬ掘り出し物が見つかる可能性が高まります。
SEARCH_KEYWORDS = [
    # 楽天の総合ランキングTOP30から探す (最も効果的)
    "ランキング", 
    # 生活必需品・人気カテゴリ
    "日用品",
    "水 ドリンク",
    "スイーツ",
    "訳あり", # 「訳あり」にはお得な商品が多い
    # 家電・デジタル製品
    "家電",
    "イヤホン",
    "スマホアクセサリー",
    # ファッション・美容
    "ファッション",
    "コスメ",
    # 趣味・その他
    "アウトドア",
    "防災グッズ",
]

# --- ディールスコア設定 ---
# オールジャンル化に伴い、様々な商品がヒットするため、
# スコアの閾値を少し厳しめにして「本当に良いもの」だけを厳選するのも手です。
DEAL_SCORE_THRESHOLD = 85 # 例: 80から85に引き上げ

# スコアの重み付け (変更なし、お好みで調整)
SCORE_WEIGHTS = {
    "point_rate": 2.5,
    "review_average": 20,
    "is_free_shipping": 15,
}

# --- セールイベント期間設定 (変更なし) ---
JST = timezone(timedelta(hours=+9))
# 現在時刻を基準にしているので、ここは特に変更不要です。
# ただし、今はセール期間外ですね。
SUPER_SALE_START = datetime(2025, 9, 4, 20, 0, 0, tzinfo=JST)
SUPER_SALE_END = datetime(2025, 9, 11, 1, 59, 0, tzinfo=JST)
