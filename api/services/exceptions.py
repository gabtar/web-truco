class GameException(Exception):
    def __init__(self, message='Error en la partida'):
        self.message = message

    def __str__(self):
        return str(self.message)
