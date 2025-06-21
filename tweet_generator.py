# tweet_generator.py
import json
import re  # 正規表現を扱うためのライブラリをインポート
import requests
import pyshorteners
import google.generativeai as genai
import config

# Gemini APIの初期設定
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def generate_tweet_with_gemini(item_info):
    """Gemini APIを使ってツイート文を生成する"""
    if not config.GEMINI_API_KEY:
        print("Gemini APIキーが設定されていません。")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    product_data = f"""
    - 商品名: {item_info['itemName']}
    - 価格: {item_info['itemPrice']}円
    - ポイント: {item_info['pointRate']}倍
    - レビュー平均: {item_info['reviewAverage']}
    - ストア名: {item_info['shopName']}
    - 商品説明文: {item_info['itemCaption']}
    """
    
    prompt = f"""
# Role
あなたは、日本の20〜40代に絶大な人気を誇るガジェット系YouTuberであり、人間の購買心理を熟知した鋭い視点を持つセールスライターです。あなたの使命は、紹介する商品の魅力を最大限に引き出し、フォロワーの「欲しい」という感情を刺激して、アフィリエイトリンクのクリックを最大化することです。

# Goal
提供された商品情報から、最高のツイート文を1つ考案し、指定したJSON形式で出力すること。

# Product Information
{product_data}

# Instructions
1.  **分析:** まず、商品の最も強力なセールスポイントと、それを最も欲しがる人物像を分析してください。
2.  **下書き作成:** 次に、分析に基づき、「感情に訴える」「お得感を強調する」「意外な魅力を伝える」という3つの異なる切り口でツイートの下書きを考えてください。
3.  **最終選定と出力:** 最後に、3つの下書きの中から最もクリックされると確信したものを1つ選び、以下の制約を守って完成させてください。

### Constraints
- 125文字以内
- 箇条書きや「」を効果的に使い、視覚的に読みやすくする
- 必ず「#PR」のハッシュタグを含める
- 親しみやすく、少し興奮したプロのトーンを維持する

### Output Format
以下のJSON形式のみで出力してください。他のテキストは一切含めないでください。
{{
  "analysis": "（ここに分析結果を簡潔に記述）",
  "best_tweet": "（ここに最終的に選ばれたツイート文を記述）"
}}
"""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text

        # --- ★★★ 新しい、より堅牢なクリーニング処理 ★★★ ---
        print(f"--- Geminiからの生の応答 ---\n{raw_text}\n--- 応答ここまで ---")
        
        # 正規表現を使い、`{` で始まり `}` で終わるJSONオブジェクトの部分だけを抽出する
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            clean_json_text = match.group(0)
            print(f"--- クリーニング後のJSONテキスト ---\n{clean_json_text}\n--- テキストここまで ---")
            # 抽出したクリーンなテキストをJSONとして解析
            return json.loads(clean_json_text)
        else:
            # 応答からJSONオブジェクトが見つからなかった場合
            print("エラー: 応答テキストから有効なJSONオブジェクトを見つけられませんでした。")
            return None
        # --- ★★★ 修正部分ここまで ★★★

    except Exception as e:
        print(f"Gemini APIエラー（JSON解析中またはその他）: {e}")
        return None

def prepare_tweet_content(item_data, generated_text):
    """ツイート文と画像URLから、投稿に必要な情報を準備する"""
    s = pyshorteners.Shortener()
    short_link = s.tinyurl.short(item_data["Item"]['affiliateUrl'])
    
    final_tweet = f"{generated_text}\n\n👇セール会場へ急げ！\n{short_link}"

    image_url = item_data["Item"]['mediumImageUrls'][0]['imageUrl']
    image_path = "/tmp/tweet_image.jpg"
    
    try:
        res = requests.get(image_url, stream=True)
        res.raise_for_status()
        with open(image_path, 'wb') as f:
            f.write(res.content)
        return final_tweet, image_path
    except requests.exceptions.RequestException as e:
        print(f"画像ダウンロードエラー: {e}")
        return final_tweet, None
