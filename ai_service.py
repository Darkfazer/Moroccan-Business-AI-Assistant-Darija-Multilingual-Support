import openai
import os
from typing import Dict, Any
import logging
from translate import Translator  # Free translation library

class AIService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.darija_dataset = self._load_darija_dataset()
        self.translator = Translator(to_lang="fr")  # Default to French

    def _load_darija_dataset(self) -> Dict[str, Dict[str, str]]:
        """Enhanced Moroccan Darija dataset"""
        return {
            "common_phrases": {
                "salam": {"french": "Bonjour", "english": "Hello", "response": "Salam! Comment puis-je vous aider?"},
                "labas": {"response": "Alhamdulillah, tout va bien. Et vous?"},
                "chhal": {"french": "Combien", "english": "How much", "response": "Le prix est {price} DH"},
                "wach": {"response": "Oui" if "{positive}" else "Non"},
                "fin": {"response": "Notre boutique est située à {location}"},
                "3andkom": {"response": "Oui, nous avons {product} en stock"},
                "livraison": {"response": "Livraison disponible partout au Maroc sous 2-3 jours"}
            },
            "products": {
                "tajine": {"response": "Nous avons plusieurs modèles de tajines artisanaux."},
                "argan": {"response": "Notre huile d'argan est 100% pure et bio."},
                "zellige": {"response": "Carreaux zellige disponibles en 15 motifs traditionnels."}
            }
        }

    async def translate(self, text: str, target_lang: str = "fr") -> str:
        """Free translation method supporting Arabic/French/English"""
        try:
            if target_lang == "ar":
                translator = Translator(to_lang="ar", from_lang="fr")
            else:
                translator = Translator(to_lang=target_lang)
            return translator.translate(text)
        except Exception as e:
            logging.error(f"Translation Error: {str(e)}")
            return text  # Fallback to original text

    async def generate_response(self, message: str, business: Dict[str, Any]) -> str:
        """Generate context-aware responses with Darija priority"""
        try:
            # 1. Check for exact Darija matches
            lower_msg = message.lower()
            
            # Product-specific responses
            for product, data in self.darija_dataset["products"].items():
                if product in lower_msg:
                    return data["response"]
            
            # Common phrases
            for phrase, data in self.darija_dataset["common_phrases"].items():
                if phrase in lower_msg:
                    return data["response"].format(
                        price=business.get("price", "___"),
                        location=business.get("location", "notre adresse principale"),
                        product=business.get("product", "ce produit"),
                        positive="oui" in lower_msg
                    )

            # 2. Fallback to OpenAI with business context
            response = await openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Vous êtes un assistant marocain pour {business['name']}.
                        Détails: {business.get('description', '')}
                        Livraison: {business.get('delivery_info', '2-3 jours')}
                        Répondez en français ou darija."""
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"AI Generation Error: {str(e)}")
            return "Désolé, je rencontre des difficultés techniques. Veuillez réessayer plus tard."

    async def detect_language(self, text: str) -> str:
        """Simple language detection for Moroccan contexts"""
        arabic_chars = set("ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي")
        if any(char in arabic_chars for char in text):
            return "ar"
        elif any(word in text.lower() for word in ["salam", "labas", "wach"]):
            return "darija"
        return "fr"