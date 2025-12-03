class ReasoningEngine:

    def process(self, intent: str, context: dict):
        """
        Decide quali tool usare.
        Per ora ritorna una struttura vuota.
        """
        return {
            "intent": intent,
            "context": context,
            "result": None
        }
