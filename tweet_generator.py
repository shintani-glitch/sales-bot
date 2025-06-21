# tweet_generator.py (最終調整版)
import json
import re
import requests
import pyshorteners
import google.generativeai as genai
import config

# Gemini APIの初期設定
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def generate_tweet_with_gemini(item_info):
    """Gemini APIを使ってツイート文とハッシュタグを生成する"""
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
    
    # ★★★ プロンプトを大幅に改善 ★★★
    prompt = f"""
# Role
あなたは、日本のSNSマーケティングを熟知したプロのセールスコピーライターです。あなたの使命は、商品の魅力を最大限に引き出し、クリック率と拡散力を最大化するツイートを考案することです。

# Goal
提供された商品情報から、最高のツイート文と、拡散に最適なハッシュタグのリストを考案し、指定したJSON形式で出力すること。

# Product Information
{product_data}

# Instructions
1.  **分析:** 商品の核心的な魅力と、ターゲット層を分析してください。
2.  **ツイート文作成:** 分析に基づき、ターゲットの心に響く、120文字程度の魅力的なツイート文を作成してください。**注意：このツイート文には、URLや[アフィリエイトリンク]のようなプレースホルダーを絶対に含めないでください。**
3.  **ハッシュタグ生成:** 作成したツイート文と商品情報に基づき、#PRとは別に、拡散に最も効果的と思われるハッシュタグを3つ生成してください。

# Output Format
以下のJSON形式のみで出力してください。他のテキストは一切含めないでください。
{{
  "best_tweet": "（ここに最終的に選ばれたツイート文を記述）",
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

def prepare_final_tweet_text(tweet_json):
    """
    Geminiが生成したJSONから、最終的なツイート全文を組み立てる。
    画像取得は行わない。
    """
    # Geminiが生成したツイート本文とハッシュタグを取得
    base_text = tweet_json.get("best_tweet", "")
    generated_hashtags = tweet_json.get("hashtags", [])

    # [アフィリエイトリンク] という文字列を念のため削除
    base_text = base_text.replace('[アフィリエイトリンク]', '').strip()

    # 短縮URLと基本のハッシュタグを用意
    s = pyshorteners.Shortener()
    # 実際のURLはbot.pyで付与するため、ここではダミーを入れる
    dummy_url = "https://tinyurl.com/dummy" 
    
    cta_and_link = f"\n\n👇セール会場へ急げ！\n{dummy_url}"
    
    # ハッシュタグを文字列に変換（#PRは必須）
    all_hashtags = ["#PR"] + generated_hashtags
    hashtag_string = " ".join(all_hashtags)

    # 最終的なツイートを組み立て
    final_tweet_parts = [base_text, cta_and_link, "\n\n" + hashtag_string]
    
    # 140文字の制限を超えないように調整
    # まずはURLとハッシュタグを除いた長さを計算
    while len("".join(final_tweet_parts)) > 140 and len(all_hashtags) > 1:
        all_hashtags.pop() # 後ろのハッシュタグから削除
        hashtag_string = " ".join(all_hashtags)
        final_tweet_parts = [base_text, cta_and_link, "\n\n" + hashtag_string]

    return "".join(final_tweet_parts)
