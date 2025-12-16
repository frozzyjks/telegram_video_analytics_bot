from datetime import date, datetime, time
from db import get_connection

def normalize_uuid(uuid_str: str) -> str:
    if len(uuid_str) == 32:
        return (
            uuid_str[0:8] + "-" +
            uuid_str[8:12] + "-" +
            uuid_str[12:16] + "-" +
            uuid_str[16:20] + "-" +
            uuid_str[20:32]
        )
    return uuid_str


def total_videos(conn) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM videos;")
        return cur.fetchone()[0]


def creator_videos_by_period(conn,
    creator_id: str,
    date_from: date,
    date_to: date,
) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM videos
            WHERE creator_id = %s
              AND video_created_at::date BETWEEN %s AND %s;
            """,
            (creator_id, date_from, date_to),
        )
        return cur.fetchone()[0]


def videos_views_gt(conn, threshold: int, creator_id: str | None = None):
    conn = get_connection()
    cur = conn.cursor()

    if creator_id:
        creator_id = normalize_uuid(creator_id)
        cur.execute(
            """
            SELECT COUNT(*)
            FROM videos
            WHERE views_count > %s
              AND creator_id = %s
            """,
            (threshold, creator_id)
        )
    else:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM videos
            WHERE views_count > %s
            """,
            (threshold,)
        )

    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def sum_delta_views_by_interval(conn, creator_id: str, target_date: date, start_time: time, end_time: time) -> int:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(SUM(s.delta_views_count), 0)
            FROM video_snapshots s
            JOIN videos v ON v.id = s.video_id
            WHERE v.creator_id = %s
              AND DATE(s.created_at) = %s
              AND s.created_at::time BETWEEN %s AND %s
        """, (creator_id, target_date, start_time, end_time))
        return cur.fetchone()[0]


def sum_delta_views_by_day(conn, target_date: date) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(delta_views_count), 0)
            FROM video_snapshots
            WHERE created_at::date = %s;
            """,
            (target_date,),
        )
        return cur.fetchone()[0]

def videos_with_delta_by_day(conn, target_date: date) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT video_id)
            FROM video_snapshots
            WHERE created_at::date = %s
              AND delta_views_count > 0;
            """,
            (target_date,),
        )
        return cur.fetchone()[0]

def count_negative_views_deltas(conn) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM video_snapshots
            WHERE delta_views_count < 0;
            """
        )
        return cur.fetchone()[0]

def sum_views_by_month(conn, month: int, year: int) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(views_count), 0)
            FROM videos
            WHERE EXTRACT(MONTH FROM video_created_at) = %s
              AND EXTRACT(YEAR FROM video_created_at) = %s;
            """,
            (month, year)
        )
        return cur.fetchone()[0]

def count_creators_with_videos_views_gt(threshold: int) -> int:
    """
    Считает количество уникальных креаторов, у которых есть хотя бы одно видео
    с количеством просмотров больше threshold.
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT creator_id)
            FROM videos
            WHERE views_count > %s;
            """,
            (threshold,)
        )
        return cur.fetchone()[0]

def count_creator_published_days(creator_id: str, month: int, year: int) -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT DATE(video_created_at))
            FROM videos
            WHERE creator_id = %s
              AND EXTRACT(MONTH FROM video_created_at) = %s
              AND EXTRACT(YEAR FROM video_created_at) = %s;
            """,
            (creator_id, month, year)
        )

def creator_active_days_in_month(creator_id: str, month: int, year: int) -> int:
    creator_id = normalize_uuid(creator_id)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT DATE(video_created_at))
            FROM videos
            WHERE creator_id = %s
            AND EXTRACT(MONTH FROM video_created_at) = %s
            AND EXTRACT(YEAR FROM video_created_at) = %s;
            """,
            (creator_id, month, year)
        )
        return cur.fetchone()[0]

        return cur.fetchone()[0]
