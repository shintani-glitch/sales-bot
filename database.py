# database.py

# ... (get_db_connection, setup_database は変更なし) ...

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

# get_cached_tweet と save_posted_item は変更なし
# ...
