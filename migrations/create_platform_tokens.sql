-- 기존 테이블 삭제 (있는 경우)
DROP TABLE IF EXISTS platform_tokens;

-- UUID 확장 추가 (없는 경우)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- platform_tokens 테이블 생성
CREATE TABLE platform_tokens (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    access_token TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- RLS 정책 설정
ALTER TABLE platform_tokens ENABLE ROW LEVEL SECURITY;

-- RLS 정책 생성
CREATE POLICY "Users can view their own platform tokens"
    ON platform_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own platform tokens"
    ON platform_tokens FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own platform tokens"
    ON platform_tokens FOR UPDATE
    USING (auth.uid() = user_id); 