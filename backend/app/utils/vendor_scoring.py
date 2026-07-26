def calculate_rank_score(avg_rating: float, total_bookings: int) -> float:
    return round((avg_rating * 20) + (total_bookings * 0.5), 2)