# config.py
import os
from datetime import datetime, timezone, timedelta

# --- API & DB設定 (Renderの環境変数から取得) ---
# 重要：これらの値はコードに直接書かず、必ず環境変数として設定してください。
RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# --- 検索キーワード ---
# あなたのBotの専門ジャンルに合わせてキーワードを設定
SEARCH_KEYWORDS = [
    "ゲーミングモニター 4K 144Hz",
    "Anker Soundcore",
    "Logicool MX Master",
    "ワイヤレスイヤホン ノイズキャンセリング",
    "プロテイン ザバス",
    "釣り具 シーバス ルアー"
]

# --- ディールスコア設定 ---
# このスコアを超えたら、Geminiに問い合わせる候補とする
DEAL_SCORE_THRESHOLD = 80

# スコアの重み付け
SCORE_WEIGHTS = {
    "point_rate": 2.5,          # ポイント1倍あたり2.5点
    "review_average": 20,       # レビュー平均1点あたり20点
    "is_free_shipping": 15,     # 送料無料なら+15点
}

# --- セールイベント期間設定 (手動で設定) ---
JST = timezone(timedelta(hours=+9))
# 例：次の楽天スーパーセール期間を想定
SUPER_SALE_START = datetime(2025, 9, 4, 20, 0, 0, tzinfo=JST)
SUPER_SALE_END = datetime(2025, 9, 11, 1, 59, 0, tzinfo=JST)
