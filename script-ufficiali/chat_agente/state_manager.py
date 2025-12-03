class StateManager:

    def __init__(self):
        self.state = {
            "last_intent": None,
            "slots": {},
            "last_simulation": None
        }

    def update(self, intent: str, slots: dict):
        """
        Aggiorna conversazione.
        """
        if intent:
            self.state["last_intent"] = intent

        # unisce i nuovi slot con quelli già noti
        self.state["slots"].update(slots)

        return self.state
