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

    @staticmethod
    def _normalize_criticality(value):
        """Convierte `value` a un float en [0,1].

        Acepta solo floats (o valores numéricos) en el rango [0,1].
        Si llega otro tipo o un número fuera de [0,1], lanza `ValueError`.
        """
        try:
            v = float(value)
        except Exception:
            raise ValueError("criticality must be a float in [0,1]")

        if 0.0 <= v <= 1.0:
            return v
        raise ValueError("criticality must be within [0,1]")

    @staticmethod
    def get_time_between_orders(criticality=1.0):
        """
        Muestra la variable discreta T (horas) entre órdenes médicas usando una
        mezcla paramétrica entre la distribución crítica P_C y la estable P_E.

        `criticality` puede ser:
        - bool (True crítico / False estable)
        - float en [0,1] donde 1=totalmente crítico y 0=totalmente estable

        Devuelve uno de {2,4,6,8,12} horas.
        """
        # Valores y distribuciones por defecto (tabla original)
        default_values = [2, 4, 6, 8, 12]
        default_pc = [0.50, 0.30, 0.15, 0.05, 0.00]
        default_pe = [0.00, 0.05, 0.15, 0.40, 0.40]

        return RandomGenerator.sample_mixture(
            criticality=criticality,
            values=default_values,
            pc=default_pc,
            pe=default_pe,
        )

    @staticmethod
    def mixture_probabilities(criticality, pc, pe):
        """Devuelve las probabilidades mezcladas alpha*pc + (1-alpha)*pe.

        - `pc` y `pe` deben ser listas de la misma longitud.
        - `criticality` float en [0,1].
        """
        if len(pc) != len(pe):
            raise ValueError("pc and pe must have the same length")

        alpha = RandomGenerator._normalize_criticality(criticality)
        probs = [alpha * pc_i + (1.0 - alpha) * pe_i for pc_i, pe_i in zip(pc, pe)]
        return probs

    @staticmethod
    def sample_mixture(criticality, values, pc, pe):
        """Muestra de una mezcla paramétrica entre dos distribuciones discretas.

        - `values`: lista de valores posibles
        - `pc`, `pe`: listas de probabilidades (misma longitud que `values`)
        - `criticality`: float en [0,1]

        Devuelve un valor tomado de `values` según las probabilidades mezcladas.
        """
        if not (len(values) == len(pc) == len(pe)):
            raise ValueError("values, pc and pe must have the same length")

        probs = RandomGenerator.mixture_probabilities(criticality, pc, pe)
        if sum(probs) <= 0:
            # fallback a uniforme
            return random.choice(values)
        return random.choices(values, weights=probs, k=1)[0]
