import random

def generate_reels_data(follows):
    # Reach
    reach = follows * random.uniform(0.5, 5)
    reach = int(reach)

    # Plays
    plays = reach * random.uniform(1, 3)
    plays = int(plays)

    # Clips Replays Count
    clips_replays_count = plays * random.uniform(0.1, 0.5)
    clips_replays_count = int(clips_replays_count)

    # Total Instagram Plays
    total_instagram_plays = plays + clips_replays_count

    # Aggregated All Plays Count (including Facebook)
    ig_reels_aggregated_all_plays_count = total_instagram_plays * random.uniform(1.1, 1.5)
    ig_reels_aggregated_all_plays_count = int(ig_reels_aggregated_all_plays_count)

    # Average Watch Time (in seconds)
    ig_reels_avg_watch_time = random.uniform(5, 30)

    # Total Video View Time
    ig_reels_video_view_total_time = ig_reels_avg_watch_time * ig_reels_aggregated_all_plays_count

    # Likes
    likes = reach * random.uniform(0.01, 0.1)
    likes = int(likes)

    # Comments
    comments = reach * random.uniform(0.001, 0.01)
    comments = int(comments)

    # Saves
    saved = reach * random.uniform(0.001, 0.01)
    saved = int(saved)

    # Shares
    shares = reach * random.uniform(0.001, 0.01)
    shares = int(shares)

    # Total Interactions
    total_interactions = likes + saved + comments + shares

    # Video Views
    video_views = ig_reels_aggregated_all_plays_count * random.uniform(1, 1.1)
    video_views = int(video_views)

    # Ensure logical constraints are met
    # For example, ig_reels_avg_watch_time should be less than ig_reels_video_view_total_time
    assert ig_reels_avg_watch_time <= ig_reels_video_view_total_time, "Average watch time exceeds total watch time."

    # Compile the metrics into a dictionary
    metrics = {
        'clips_replays_count': clips_replays_count,
        'plays': plays,
        'ig_reels_aggregated_all_plays_count': ig_reels_aggregated_all_plays_count,
        'ig_reels_avg_watch_time': ig_reels_avg_watch_time,
        'ig_reels_video_view_total_time': ig_reels_video_view_total_time,
        'comments': comments,
        'likes': likes,
        'reach': reach,
        'saved': saved,
        'shares': shares,
        'total_interactions': total_interactions,
        'video_views': video_views
    }

    return metrics