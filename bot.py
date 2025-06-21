# bot.py
import random
import tweepy
from datetime import datetime
import pytz

import config
import database
import rakuten_api
import tweet_generator

class DealScorer:
    """コストゼロのローカル処理で、セールの価値を点数化するクラス"""
    def __init__(self, item_data):
        self.item = item_data["Item"]
        self.weights = config.SCORE_WEIGHTS

    def calculate(self):
        score = 0
        score += self.item.get("pointRate", 0) * self.weights["point_rate"]
        score += float(self.item.get("reviewAverage", 0)) * self.weights["review_average"]
        if self.item.get("postageFlag", 1) == 0:
            score += self.weights["is_free_shipping"]
        return score

def is_post_time():
    """現在が投稿すべき時間かを判定する"""
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    weekday = now.weekday()
    hour = now.hour

    if config.SUPER_SALE_START <= now <= config.SUPER_SALE_END:
        return True

    if 0 <= weekday <= 4 and hour in [7, 12, 21]: return True
    if weekday >= 5 and hour in [10, 15, 21]: return True
            
    return False

def main():
    """Botのメイン処理"""
    if not is_post_time():
        print(f"現在時刻は投稿時間外です。処理をスキップします。")
        return

    print("処理開始: データベースとTwitter APIを準備します。")
    database.setup_database()
    
    try:
        client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY, consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN, access_token_secret=config.TWITTER_ACCESS_SECRET
        )
        auth = tweepy.OAuth1UserHandler(
            config.TWITTER_API_KEY, config.TWITTER_API_SECRET,
            config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_SECRET
        )
        api_v1 = tweepy.API(auth)
    except Exception as e:
        print(f"Twitter APIの認証に失敗しました: {e}")
        return

    search_keywords = random.sample(config.SEARCH_KEYWORDS, len(config.SEARCH_KEYWORDS))
    for keyword in search_keywords:
        print(f"\n--- キーワード「{keyword}」で検索 ---")
        items = rakuten_api.search_items(keyword)
        if not items: continue

        for item_data in items:
            scorer = DealScorer(item_data)
            score = scorer.calculate()
            if score < config.DEAL_SCORE_THRESHOLD:
                continue
            
            item_code = item_data["Item"]["itemCode"]
            print(f"L1突破: {item_data['Item']['itemName'][:30]}... (スコア: {score:.0f})")
            
            if database.is_recently_posted(item_code, days=30):
                print(f"30日以内に投稿済みのためスキップします。")
                continue

            generated_text = database.get_cached_tweet(item_code)
            if not generated_text:
                 print("L3: 未知の逸材、または古いキャッシュ。Geminiにツイート生成を依頼。")
                 tweet_json = tweet_generator.generate_tweet_with_gemini(item_data["Item"])
                 if not tweet_json or "best_tweet" not in tweet_json:
                     print("Geminiでの生成に失敗。この商品はスキップします。")
                     continue
                 generated_text = tweet_json["best_tweet"]
            else:
                print("L2: 30日以上前のキャッシュを発見。ツイートを再利用します。")
            
            final_tweet, image_path = tweet_generator.prepare_tweet_content(item_data, generated_text)
            
            try:
                media_id = None
                if image_path:
                    media = api_v1.media_upload(filename=image_path)
                    media_id = media.media_id_string
                
                client.create_tweet(text=final_tweet, media_ids=[media_id] if media_id else None)
                print("★★★ ツイート成功！ ★★★")
                
                database.save_posted_item(item_code, generated_text)
                
                print("素晴らしいディールを投稿したので、今回の実行はこれで終了します。")
                return
            except Exception as e:
                print(f"ツイートエラー: {e}")
                continue
    
    print("\n今回は投稿基準を満たす新しいディールが見つかりませんでした。")

if __name__ == "__main__":
    main()
