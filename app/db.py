import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="video_analytics",
        user="video_user",
        password="video_pass",
    )



def count_total_videos(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM videos")
        return cur.fetchone()[0]


def count_creator_videos_by_period(conn, creator_id, date_from, date_to):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM videos
            WHERE creator_id = %s
              AND video_created_at >= %s
              AND video_created_at <= %s
            """,
            (creator_id, date_from, date_to),
        )
        return cur.fetchone()[0]


def count_videos_views_gt(conn, threshold, creator_id=None):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM videos
            WHERE views_count > %s
              AND (%s IS NULL OR creator_id = %s)
            """,
            (threshold, creator_id, creator_id),
        )
        return cur.fetchone()[0]


def sum_delta_views_by_day(conn, day):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(delta_views_count), 0)
            FROM video_snapshots
            WHERE DATE(created_at) = %s
            """,
            (day,),
        )
        return cur.fetchone()[0]


def count_videos_with_delta_by_day(conn, day):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT video_id)
            FROM video_snapshots
            WHERE DATE(created_at) = %s
              AND delta_views_count > 0
            """,
            (day,),
        )
        return cur.fetchone()[0]

def count_negative_views_deltas(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM video_snapshots
            WHERE delta_views_count < 0
        """)
        return cur.fetchone()[0]