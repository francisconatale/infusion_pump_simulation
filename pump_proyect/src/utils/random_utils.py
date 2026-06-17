import random

def hours_to_minutes(hours):
    """Convierte horas a minutos."""
    return hours * 60.0

def minutes_to_seconds(minutes):
    """Convierte minutos a segundos."""
    return minutes * 60.0

def hours_to_seconds(hours):
    """Convierte horas a segundos directamente."""
    return hours * 3600.0

class RandomGenerator:
    """Clase de utilidad para generar variables aleatorias comunes en simulaciones."""
    
    @staticmethod
    def get_normal(mu, sigma, min_val=None, max_val=None):
        """
        Genera un valor de una distribución Normal TRUNCADA usando rejection sampling.
        mu: media
        sigma: desviación estándar
        min_val: valor mínimo permitido (opcional)
        max_val: valor máximo permitido (opcional)
        """
        while True:
            val = random.gauss(mu, sigma)
            
            # Rechazar si está fuera de los límites
            if min_val is not None and val < min_val:
                continue
            if max_val is not None and val > max_val:
                continue
            
            return val

    @staticmethod
    def get_exponential(mean_time, min_val=0.0):
        """
        Genera un valor de una distribución Exponencial TRUNCADA.
        mean_time: el tiempo promedio entre eventos (1/lambda).
        min_val: valor mínimo (por defecto 0.0 para evitar tiempos negativos)
        """
        if mean_time <= 0:
            return min_val
        
        val = random.expovariate(1.0 / mean_time)
        return max(min_val, val)

    @staticmethod
    def get_uniform(a, b):
        """Genera un valor aleatorio entre a y b."""
        return random.uniform(a, b)
