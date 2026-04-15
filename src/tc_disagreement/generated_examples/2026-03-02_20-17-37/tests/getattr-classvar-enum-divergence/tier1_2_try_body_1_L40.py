            cache = getattr(cls, "_user_status_cache")
            reveal_type(cache) # Expected divergence: Dict[UserID, StatusEnum] vs. Any