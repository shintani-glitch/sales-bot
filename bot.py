# bot.py (最終調整版)
import random
import tweepy
from datetime import datetime
import pytz
import pyshorteners
import time
import json

import config
import database
import rakuten_api
import tweet_generator

class DealScorer:
    # (変更なし)
    def __init__(self, item_data):
        self.item = item_data["Item"]
        self.weights = config.SCORE_WEIGHTS
    def calculate(self):
        score = 0; score += self.item.get("pointRate", 0) * self.weights["point_rate"]; score += float(self.item.get("reviewAverage", 0)) * self.weights["review_average"];
        if self.item.get("postageFlag", 1) == 0: score += self.weights["is_free_shipping"];
        return score

def is_post_time():
    """現在が投稿すべき時間かを判定する (最終調整版)"""
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    weekday = now.weekday()  # 月曜=0, ..., 日曜=6
    hour = now.hour

    # 大型セール期間中は毎時投稿 (変更なし)
    if config.SUPER_SALE_START <= now <= config.SUPER_SALE_END:
        return True

    # --- ★★★ ここからが最新のスケジュールです ★★★ ---
    # 平日 (月曜〜金曜) の投稿時間
    if 0 <= weekday <= 4 and hour in [0, 7, 9, 12, 15, 18, 19, 20, 21, 22, 23]:
        return True
        
    # 休日 (土曜・日曜) の投稿時間
    if weekday >= 5 and hour in [0, 9, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23]:
        return True
            
    return False

def main():
    if not is_post_time():
        print(f"現在時刻 ({datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M')}) は投稿時間外です。処理をスキップします。"); return

    print("処理開始..."); database.setup_database()
    try:
        client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY, consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN, access_token_secret=config.TWITTER_ACCESS_SECRET
        )
    except Exception as e:
        print(f"Twitter API認証エラー: {e}"); return

    search_keywords = random.sample(config.SEARCH_KEYWORDS, len(config.SEARCH_KEYWORDS))
    for keyword in search_keywords:
        print(f"\n--- キーワード「{keyword}」で検索 ---")
        items = rakuten_api.search_items(keyword)
        if not items: continue

        for item_data in items:
            scorer = DealScorer(item_data); score = scorer.calculate()
            if score < config.DEAL_SCORE_THRESHOLD: continue
            
            item_code = item_data["Item"]["itemCode"]
            print(f"L1突破: {item_data['Item']['itemName'][:30]}... (スコア: {score:.0f})")
            
            if database.is_recently_posted(item_code, days=30):
                print(f"30日以内に投稿済みのためスキップ。"); continue

            tweet_parts_json = database.get_cached_tweet(item_code)
            if tweet_parts_json:
                print("L2: キャッシュからツイートパーツを発見。")
                tweet_json = json.loads(tweet_parts_json)
            else:
                print("L3: Geminiにツイートパーツ生成を依頼。")
                tweet_json = tweet_generator.generate_tweet_with_gemini(item_data["Item"])
                time.sleep(2)
                if not tweet_json:
                    print("Geminiでの生成に失敗。スキップします。"); continue
            
            catchphrase = tweet_json.get("catchphrase", "")
            product_name = tweet_json.get("product_name", item_data["Item"]["itemName"][:30])
            benefits = tweet_json.get("benefits", [])
            hashtags = tweet_json.get("hashtags", [])
            
            s = pyshorteners.Shortener()
            short_link = s.tinyurl.short(item_data["Item"]['affiliateUrl'])

            tweet_lines = []
            tweet_lines.append(catchphrase)
            tweet_lines.append(product_name)
            tweet_lines.append("")
            
            for benefit in benefits:
                tweet_lines.append(f"✅ {benefit}")
            
            tweet_lines.append("")
            tweet_lines.append("👇セール会場へ急げ！")
            tweet_lines.append(short_link)
            tweet_lines.append("")

            hashtag_string = "#PR " + " ".join(hashtags)
            tweet_lines.append(hashtag_string)

            final_tweet = "\n".join(tweet_lines)

            try:
                client.create_tweet(text=final_tweet)
                print("★★★ ツイート成功！ ★★★")
                print(final_tweet)
                
                database.save_posted_item(item_code, json.dumps(tweet_json, ensure_ascii=False))
                
                print("素晴らしいディールを投稿したので、今回の実行はこれで終了します。"); return
            except Exception as e:
                print(f"ツイートエラー: {e}"); continue
    
    print("\n今回は投稿基準を満たす新しいディールが見つかりませんでした。")

if __name__ == "__main__":
    main()
