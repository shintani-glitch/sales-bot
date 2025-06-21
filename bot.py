# bot.py (最終調整版)
import random
import tweepy
from datetime import datetime
import pytz
import pyshorteners
import time

import config
import database
import rakuten_api
import tweet_generator

class DealScorer:
    # (このクラスは変更なし)
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
    # (この関数は変更なし)
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    weekday = now.weekday()
    hour = now.hour
    if config.SUPER_SALE_START <= now <= config.SUPER_SALE_END:
        return True
    if 0 <= weekday <= 4 and hour in [7, 9, 12, 15, 18, 21, 23]:
        return True
    if weekday >= 5 and hour in [9, 11, 12, 14, 16, 18, 19, 21, 22, 23]:
        return True
    return False

def main():
    """Botのメイン処理"""
    if not is_post_time():
        print(f"現在時刻 ({datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M')}) は投稿時間外です。処理をスキップします。")
        return

    print("処理開始: データベースとTwitter APIを準備します。")
    database.setup_database()
    
    try:
        client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY, consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN, access_token_secret=config.TWITTER_ACCESS_SECRET
        )
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

            # ★★★ 投稿ロジックを修正 ★★★
            # まずはツイート文のテンプレート（URLなし）を生成
            cached_text_template = database.get_cached_tweet(item_code)
            
            if cached_text_template:
                print("L2: キャッシュからツイートテンプレートを発見。")
                text_template = cached_text_template
            else:
                print("L3: 未知の逸材。Geminiにツイート生成を依頼。")
                tweet_json = tweet_generator.generate_tweet_with_gemini(item_data["Item"])
                time.sleep(2)

                if not tweet_json or "best_tweet" not in tweet_json:
                    print("Geminiでの生成に失敗。この商品はスキップします。")
                    continue
                
                # 最終的なツイート全文ではなく、URL部分を除いたテンプレートを生成
                text_template = tweet_generator.prepare_final_tweet_text(tweet_json)
                
            # 実際の短縮URLを生成
            s = pyshorteners.Shortener()
            short_link = s.tinyurl.short(item_data["Item"]['affiliateUrl'])
            
            # テンプレートに本物のURLを埋め込む
            final_tweet = text_template.replace("https://tinyurl.com/dummy", short_link)
            
            try:
                # 画像なしでツイート
                client.create_tweet(text=final_tweet)
                print("★★★ ツイート成功！ ★★★")
                
                # DBにはURLなしのテンプレートを保存
                database.save_posted_item(item_code, text_template)
                
                print("素晴らしいディールを投稿したので、今回の実行はこれで終了します。")
                return
            except Exception as e:
                print(f"ツイートエラー: {e}")
                continue
    
    print("\n今回は投稿基準を満たす新しいディールが見つかりませんでした。")

if __name__ == "__main__":
    main()
