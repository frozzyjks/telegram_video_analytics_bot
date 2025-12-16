from datetime import date, datetime
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


def total_videos() -> int:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM videos;")
        return cur.fetchone()[0]


def creator_videos_by_period(
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


def videos_views_gt(threshold: int, creator_id: str | None = None):
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



def sum_delta_views_by_day(target_date: date) -> int:
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


def videos_with_delta_by_day(target_date: date) -> int:
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