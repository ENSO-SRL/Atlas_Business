from thefuzz import fuzz, process

from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService
from src.Settings.settings import Settings


class FuzzyContentFilterService(IContentFilterService):
    """
    Servicio de moderación de contenido basado en distancias de Levenshtein (thefuzz).
    Permite detectar variaciones u ofuscaciones de palabras prohibidas (ej. 'c4sino' o 'apuestasss').
    """
    
    def __init__(self, settings: Settings):
        self.threshold = settings.CONTENT_FILTER_THRESHOLD
        self.forbidden_words = [
            "casino", "apuestas", "ilegal", "droga", "violencia", 
            "armas", "prostitucion", "suicidio", "sexo", "porno"
        ]

    async def check(self, fields: dict[str, str]) -> list[str]:
        matches = []
        for field, text in fields.items():
            if not text:
                continue
                
            # Tokenizamos el texto por palabras (simplificado)
            words = text.lower().split()
            
            for word in words:
                # Extraemos el mejor match de la lista de palabras prohibidas
                best_match, score = process.extractOne(word, self.forbidden_words, scorer=fuzz.ratio)
                
                if score >= self.threshold:
                    matches.append(f"{field}:{best_match} (score: {score})")
                    # No necesitamos buscar más en este campo si ya falló
                    break
                    
        return matches
