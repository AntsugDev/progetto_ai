class ResponseGenerator:

    def generate(self, intent: str, result: dict, context: dict) -> str:
        """
        Genera risposta naturale.
        Poi aggiungeremo tono umano + consigli.
        """
        return f"Ho ricevuto la tua richiesta ({intent}). A breve potrò risponderti."
