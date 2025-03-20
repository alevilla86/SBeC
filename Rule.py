from sklearn.metrics.pairwise import cosine_similarity


class Rule:
    """Clase base para todas las reglas."""
    def apply(self, user_input, travel_data):
        raise NotImplementedError("Cada regla debe implementar 'apply'")
    

class CosineSimilarityRule(Rule):
    def __init__(self, scaler, normalized_data):
        self.scaler = scaler
        self.normalized_data = normalized_data

    def apply(self, user_input, travel_data):
        user_input_scaled = self.scaler.transform([user_input])
        return cosine_similarity(user_input_scaled, self.normalized_data)[0]
    

class ThresholdRule(Rule):
    def __init__(self, threshold, column_name):
        self.threshold = threshold
        self.column_name = column_name

    def apply(self, user_input, travel_data):
        if self.column_name is None:
            return 0 # No se aplica la regla. Verificar si retornar 0 es lo correcto. TODO
        
        return (travel_data[self.column_name] <= self.threshold).astype(float)
    

class EqualityRule(Rule):
    def __init__(self, column_name, user_input):
        self.column_name = column_name
        self.user_input = user_input

    def apply(self, user_input, travel_data):
        if self.user_input is None:
            return 0 # No se aplica la regla. Verificar si retornar 0 es lo correcto. TODO
        
        return (travel_data[self.column_name] == self.user_input).astype(float) 
    