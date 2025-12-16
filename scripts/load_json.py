import json
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "video_analytics",
    "user": "video_user",
    "password": "video_pass",
}

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "videos.json"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data["videos"]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    video_rows = []
    snapshot_rows = []

    for video in videos:
        video_rows.append((
            video["id"],
            video["creator_id"],
            video["video_created_at"],
            video.get("views_count"),
            video.get("likes_count"),
            video.get("comments_count"),
            video.get("reports_count"),
            video.get("created_at"),
            video.get("updated_at"),
        ))

        for snap in video.get("snapshots", []):
            snapshot_rows.append((
                snap["id"],
                video["id"],
                snap.get("views_count"),
                snap.get("likes_count"),
                snap.get("comments_count"),
                snap.get("reports_count"),
                snap.get("delta_views_count"),
                snap.get("delta_likes_count"),
                snap.get("delta_comments_count"),
                snap.get("delta_reports_count"),
                snap["created_at"],
                snap.get("updated_at"),
            ))

    execute_batch(
        cur,
        """
        INSERT INTO videos (
            id, creator_id, video_created_at,
            views_count, likes_count, comments_count, reports_count,
            created_at, updated_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
        """,
        video_rows,
        page_size=1000,
    )

    execute_batch(
        cur,
        """
        INSERT INTO video_snapshots (
            id, video_id,
            views_count, likes_count, comments_count, reports_count,
            delta_views_count, delta_likes_count,
            delta_comments_count, delta_reports_count,
            created_at, updated_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
        """,
        snapshot_rows,
        page_size=1000,
    )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Загружено видео: {len(video_rows)}")
    print(f"Загружено снапшотов: {len(snapshot_rows)}")


if __name__ == "__main__":
    main()