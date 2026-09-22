from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService


class DummyContentFilterService(IContentFilterService):
    
    async def check(self, fields: dict[str, str]) -> list[str]:
        # En una app real, esto llama a una API de moderación de OpenAI/Azure
        # Para el MVP, simplemente buscamos un par de palabras clave
        forbidden = ["casino", "apuestas", "ilegal", "droga", "violencia"]
        matches = []
        for field, text in fields.items():
            if text:
                for word in forbidden:
                    if word in text.lower():
                        matches.append(f"{field}:{word}")
        return matches
