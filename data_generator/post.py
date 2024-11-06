import random

def generate_post_data(total_followers):
    # 총 팔로워 수가 최소 1 이상인지 확인
    total_followers = max(int(total_followers), 1)

    # 도달 범위 계산
    reach = int(total_followers * random.uniform(0.5, 2.0))
    reach = max(reach, 1)

    # 노출 수 계산
    impressions = int(reach * random.uniform(1.0, 3.0))
    impressions = max(impressions, reach)

    # 좋아요 수 계산
    likes = int(reach * random.uniform(0.01, 0.05))
    likes = max(likes, 0)

    # 댓글 수 계산
    comments = int(reach * random.uniform(0.001, 0.01))
    comments = max(comments, 0)

    # 저장 수 계산
    saved = int(reach * random.uniform(0.001, 0.01))
    saved = max(saved, 0)

    # 공유 수 계산
    shares = int(reach * random.uniform(0.001, 0.01))
    shares = max(shares, 0)

    # 프로필 방문 수 계산
    profile_visits = int(reach * random.uniform(0.01, 0.1))
    profile_visits = max(profile_visits, 0)

    # 프로필 활동 계산
    profile_activity = int(profile_visits * random.uniform(0.1, 0.5))
    profile_activity = max(profile_activity, 0)

    # 새로운 팔로우 수 계산
    new_follows = int(profile_visits * random.uniform(0.01, 0.1))
    new_follows = max(new_follows, 0)

    # 총 상호작용 수 계산
    total_interactions = likes + comments + saved + shares

    # 결과를 딕셔너리로 반환
    metrics = {
        'impressions': impressions,
        'reach': reach,
        'saved': saved,
        'comments': comments,
        'follows': new_follows,
        'likes': likes,
        'profile_activity': profile_activity,
        'profile_visits': profile_visits,
        'shares': shares,
        'total_interactions': total_interactions
    }

    return metrics
