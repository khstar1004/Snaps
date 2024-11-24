 create table user_connections (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references auth.users(id) on delete cascade,
    platform text not null,
    access_token text not null,
    expires_at timestamp with time zone,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    unique(user_id, platform)
);

-- RLS 정책
alter table user_connections enable row level security;

create policy "Users can view their own connections"
    on user_connections for select
    using (auth.uid() = user_id);

create policy "Users can insert their own connections"
    on user_connections for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own connections"
    on user_connections for update
    using (auth.uid() = user_id);