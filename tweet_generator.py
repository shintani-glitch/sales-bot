# tweet_generator.py (可読性向上版)
import json
import re
import google.generativeai as genai
import config

# Gemini APIの初期設定
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def generate_tweet_with_gemini(item_info):
    """Gemini APIを使って、構造化されたツイートパーツを生成する"""
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
    
    # ★★★ プロンプトと出力形式を更新 ★★★
    prompt = f"""
# Role
あなたは、非常に優れたSNSマーケティング担当者です。あなたの使命は、商品の情報を基に、ユーザーの目を引き、内容を理解しやすく、クリックしたくなるようなツイートの構成要素を考案することです。

# Goal
提供された商品情報から、ツイートの各構成要素を考案し、指定したJSON形式で出力すること。

# Product Information
{product_data}

# Instructions
1.  **catchphrase:** 商品の最も魅力的な点（価格や特徴）を、15文字程度の短いキャッチコピーにしてください。【】で囲んでください。
2.  **product_name:** ツイートに掲載するための、分かりやすい商品名を30文字以内で記述してください。
3.  **benefits:** ユーザーが「欲しい！」と感じるような、この商品の魅力的なポイントやメリットを、25文字程度の短い文章で3つ、リスト形式で作成してください。
4.  **hashtags:** この商品の拡散に最も効果的と思われるハッシュタグを、#PRとは別に3つ生成してください。

# Output Format
以下のJSON形式のみで出力してください。他のテキストは一切含めないでください。
{{
  "catchphrase": "【ここにキャッチコピー】",
  "product_name": "ここに商品名",
  "benefits": [
    "ここに魅力ポイント1",
    "ここに魅力ポイント2",
    "ここに魅力ポイント3"
  ],
  "hashtags": ["#ハッシュタグ1", "#ハッシュタグ2", "#ハッシュタグ3"]
}}
"""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            clean_json_text = match.group(0)
            return json.loads(clean_json_text)
        else:
            print("エラー: 応答テキストから有効なJSONオブジェクトを見つけられませんでした。")
            return None
    except Exception as e:
        print(f"Gemini APIエラー: {e}")
        return None

# このファイルの他の関数は不要になるため削除します
