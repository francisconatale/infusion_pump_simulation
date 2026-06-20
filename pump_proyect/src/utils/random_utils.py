import random

def hours_to_minutes(hours):
    """Converts hours to minutes."""
    return hours * 60.0

def minutes_to_seconds(minutes):
    """Converts minutes to seconds."""
    return minutes * 60.0

def hours_to_seconds(hours):
    """Converts hours to seconds directly."""
    return hours * 3600.0

class RandomGenerator:
    """Utility class for generating common random variables in simulations."""
    
    @staticmethod
    def get_normal(mu, sigma, min_val=None, max_val=None):
        """
        Generates a value from a truncated Normal distribution using rejection sampling.
        mu: mean
        sigma: standard deviation
        min_val: minimum allowed value (optional)
        max_val: maximum allowed value (optional)
        """
        while True:
            val = random.gauss(mu, sigma)
            
            if min_val is not None and val < min_val:
                continue
            if max_val is not None and val > max_val:
                continue
            
            return val

    @staticmethod
    def get_exponential(mean_time, min_val=0.0):
        """
        Generates a value from a truncated Exponential distribution.
        mean_time: the average time between events (1/lambda).
        min_val: minimum value (default 0.0 to avoid negative times)
        """
        if mean_time <= 0:
            return min_val
        
        val = random.expovariate(1.0 / mean_time)
        return max(min_val, val)

    @staticmethod
    def get_uniform(a, b):
        """Generates a random value between a and b."""
        return random.uniform(a, b)

