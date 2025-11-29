import uvicorn

class Server:
    def __init__(self,app):
        self.app = app
    def run(self):
        try:
            uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")
        except Exception as e:
            print(f"Errore durante l'avvio del server: {str(e)}")
            raise e