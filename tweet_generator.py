# tweet_generator.py

# ... (他の部分は変更なし) ...
def generate_tweet_with_gemini(item_info):
    if not config.GEMINI_API_KEY:
        print("Gemini APIキーが設定されていません。")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash')
    # ... (promptの定義は変更なし) ...
    
    try:
        response = model.generate_content(prompt)
        # ★★★ デバッグ用のログを追加 ★★★
        print("--- Geminiからの生の応答 ---")
        print(response)
        print("--- 応答ここまで ---")
        # ★★★ 追加部分ここまで ★★★
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Gemini APIエラー: {e}")
        # ★★★ エラー時の応答もログに出す ★★★
        if 'response' in locals() and hasattr(response, 'parts'):
            print("--- Geminiからのエラー応答詳細 ---")
            print(response.parts)
            print("--- 応答ここまで ---")
        return None
