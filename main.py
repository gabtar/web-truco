from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from models import Hand

app = FastAPI()

# TODO hacer con el cliente de javascript o algún framework de front
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Truco</title>
    </head>
    <body>
        <h1>Web Socket Truco</h1>
        <h2>User ID: <span id="ws-id"></span></h2>
        <button id="dealCards" onclick="deal()">Repartir cartas</button>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
            function deal() {
                ws.send('dealHand')
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

        # Crea una mano para las cartas
        self.hand = Hand()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        # Agrega juagadores a la mano actual
        self.hand.players.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

        self.hand.players.append(websocket)

    # Prueba repartir las cartas de la mano
    async def deal_cards(self):
        self.hand.deal_cards()
        for player in self.hand.players:
            player_cards = self.hand.cards_dealed[player]
            cards_json = ''
            for card in player_cards:
                cards_json += card.to_json()

            # Enviar a cada conexion las cartas
            await player.send_text(cards_json)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


# TODO, Ver como manejar los websocket como clases en la documentación
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            if data == 'dealHand':
                await manager.deal_cards()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
