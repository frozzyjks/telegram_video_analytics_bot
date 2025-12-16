CREATE TABLE videos (
    id UUID PRIMARY KEY,
    creator_id UUID NOT NULL,
    video_created_at TIMESTAMP NOT NULL,
    views_count BIGINT,
    likes_count BIGINT,
    comments_count BIGINT,
    reports_count BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE video_snapshots (
    id UUID PRIMARY KEY,
    video_id UUID REFERENCES videos(id),
    views_count BIGINT,
    likes_count BIGINT,
    comments_count BIGINT,
    reports_count BIGINT,
    delta_views_count BIGINT,
    delta_likes_count BIGINT,
    delta_comments_count BIGINT,
    delta_reports_count BIGINT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE INDEX idx_videos_created_at
    ON videos(video_created_at);

CREATE INDEX idx_snapshots_created_at
    ON video_snapshots(created_at);

CREATE INDEX idx_snapshots_video_id
    ON video_snapshots(video_id);
