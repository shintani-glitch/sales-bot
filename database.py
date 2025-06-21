# database.py
import psycopg2
import config

def get_db_connection():
    """データベースへの接続を取得する"""
    return psycopg2.connect(config.DATABASE_URL)

# ↓ おそらく、お手元のファイルにはこの関数がありませんでした。
def setup_database():
    """起動時にテーブルが存在しない場合、作成する"""
    conn = get_db_connection()
    cur = conn.cursor()
    # item_codeを主キーとし、生成したツイート文をキャッシュするカラムを追加
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posted_items (
            item_code TEXT PRIMARY KEY,
            generated_text TEXT,
            posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def is_recently_posted(item_code, days=30):
    """
    指定された日数の期間内に、商品が投稿されたかどうかをチェックする。
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # NOW()から指定された日数を引いた時刻以降に投稿記録があるか調べるクエリ
    query = """
        SELECT 1 FROM posted_items 
        WHERE item_code = %s AND posted_at >= NOW() - INTERVAL '%s days';
    """
    cur.execute(query, (item_code, days))
    result = cur.fetchone()
    cur.close()
    conn.close()
    # レコードがあればTrue、なければFalseを返す
    return result is not None

def get_cached_tweet(item_code):
    """キャッシュされたツイート文を取得する"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT generated_text FROM posted_items WHERE item_code = %s;", (item_code,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result and result[0] else None

def save_posted_item(item_code, generated_text):
    """投稿済み商品IDと生成したツイート文を保存（キャッシュ）する"""
    conn = get_db_connection()
    cur = conn.cursor()
    # 既に存在するitem_codeの場合は、generated_textとposted_atを更新する
    cur.execute(
        """
        INSERT INTO posted_items (item_code, generated_text, posted_at) 
        VALUES (%s, %s, CURRENT_TIMESTAMP) 
        ON CONFLICT (item_code) 
        DO UPDATE SET 
            generated_text = EXCLUDED.generated_text, 
            posted_at = EXCLUDED.posted_at;
        """,
        (item_code, generated_text)
    )
    conn.commit()
    cur.close()
    conn.close()
