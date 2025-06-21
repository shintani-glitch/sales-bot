# bot.py (main関数の中のループ部分)

# ... (for keyword in search_keywords: の中) ...
    for item_data in items:
        # (L1フィルターのスコア計算は同じ)
        # ...

        item_code = item_data["Item"]["itemCode"]
        print(f"L1突破: {item_data['Item']['itemName'][:30]}... (スコア: {score:.0f})")

        # ★★★ ここを修正 ★★★
        # 以前のチェック方法： if database.get_cached_tweet(item_code): ...
        # 新しいチェック方法：
        if database.is_recently_posted(item_code, days=30):
            print(f"30日以内に投稿済みのためスキップします。")
            continue
        # ★★★ 修正ここまで ★★★

        # L3フィルター: Gemini API呼び出し (キャッシュがなければ)
        # ※is_recently_posted が False でも、キャッシュ自体は古いものが残っている可能性がある
        # そのため、キャッシュ取得のロジックは残しつつ、再投稿を許可する
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

        # (ツイート準備と投稿処理は同じ)
        # ...
