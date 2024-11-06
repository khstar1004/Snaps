import random

def generate_story_data(total_followers):
    # 총 팔로워 수가 최소 1 이상인지 확인
    total_followers = max(int(total_followers), 1)

    # Generate reach (10% to 30% of follows, with randomness)
    reach_percentage = random.uniform(0.1, 0.3)
    reach = int(follows * reach_percentage)
    reach = int(reach * random.uniform(0.9, 1.1))  # Adding randomness
    reach = min(reach, int(follows * 1.2))  # Constraint: reach ≤ follows × 1.2

    # Generate impressions (reach + 5% to 50% extra views)
    extra_views_percentage = random.uniform(0.05, 0.5)
    impressions = int(reach * (1 + extra_views_percentage))
    impressions = max(impressions, reach)  # Constraint: impressions ≥ reach

    # Generate replies (0.5% to 5% of reach)
    replies_percentage = random.uniform(0.005, 0.05)
    replies = int(reach * replies_percentage)
    replies = min(replies, reach)  # Constraint: replies ≤ reach

    # Generate shares (0.1% to 2% of reach)
    shares_percentage = random.uniform(0.001, 0.02)
    shares = int(reach * shares_percentage)
    shares = min(shares, reach)  # Constraint: shares ≤ reach

    # Calculate total interactions
    total_interactions = replies + shares  # total_interactions = replies + shares

    # Generate profile visits (1% to 10% of reach)
    profile_visits_percentage = random.uniform(0.01, 0.1)
    profile_visits = int(reach * profile_visits_percentage)
    profile_visits = min(profile_visits, reach)  # Constraint: profile_visits ≤ reach

    # Generate profile activity (10% to 50% of profile visits)
    profile_activity_percentage = random.uniform(0.1, 0.5)
    profile_activity = int(profile_visits * profile_activity_percentage)
    profile_activity = min(profile_activity, profile_visits)  # Constraint: profile_activity ≤ profile_visits

    # Generate follows from story (5% to 20% of profile visits)
    follows_from_story_percentage = random.uniform(0.05, 0.2)
    follows_from_story = int(profile_visits * follows_from_story_percentage)
    follows_from_story = min(follows_from_story, profile_visits)  # Constraint: follows_from_story ≤ profile_visits

    # Generate navigation actions (impressions × 1 to 2)
    navigation = int(impressions * random.uniform(1, 2))
    navigation = max(navigation, impressions)  # Constraint: navigation ≥ impressions

    # Compile all metrics into a dictionary
    metrics = {
        'follows': follows,
        'reach': reach,
        'impressions': impressions,
        'replies': replies,
        'shares': shares,
        'total_interactions': total_interactions,
        'profile_visits': profile_visits,
        'profile_activity': profile_activity,
        'follows_from_story': follows_from_story,
        'navigation': navigation
    }

    return metrics
