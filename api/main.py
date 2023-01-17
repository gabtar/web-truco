import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from services.services import ConnectionManager, HandManager


app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(ConnectionManager), game_manager: HandManager = Depends(HandManager)):
    await manager.connect(websocket)
    # TODO, Una vez connectado enviarle un update de las partidas en juego
    try:
        while True:
            # TODO, buscar algun tipo de routeo segun el tipo de evento
            # Una especie de controlador de WebSocket, ej
            # -> socketController.execute(action=data['event'], payload=data['payload'])
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            print("Total connected users: ", len(manager.active_connections))

            if data['event'] == 'createNewGame':
                # Crea la partida, agrega al jugador, y actualiza lista de partidas
                new_hand_id = await game_manager.new_hand(data['playerId'])
                await game_manager.join_hand(player_id=data['playerId'], hand_id=new_hand_id)
                await game_manager.games_update()
            elif data['event'] == 'joinGame':
                await game_manager.join_hand(hand_id=int(data['handId']), player_id=data['playerId'])
                # Actualiza la lista por si alguna mano se llenó de jugadores
                await game_manager.games_update()
            elif data['event'] == 'dealCards':
                # Busco la mano asociada al id de usuario
                # Y reparto las cartas
                await game_manager.deal_cards(hand_id=int(data['handId']))
            elif data['event'] == 'message':
                message = json.dumps({"event": "message", "message": data['message']})
                await manager.broadcast(message)

    except WebSocketDisconnect:
        # TODO end the game, set a winner if user was playing a game
        manager.disconnect(websocket)
        print(" User disconected")


"""
# TODO, ver como documentar mejor
GAMES / WEBSOCKET EVENTS:
(Naming convenion used for json: camelCase)

Server -> Client events:

- "event" : "gamesUpdate" -> updates the online games list
--------------------------------------------------------------
 Data sent: "totalGames" : int (Later will be a games_id to join)
--------------------------------------------------------------

- "event" : "joinedHand" -> the user succesfully joined a hand
--------------------------------------------------------------
 Data sent: "hand_id" : int
--------------------------------------------------------------

- "event" : "receiveDealedCards" -> sends the cards to the player
--------------------------------------------------------------
 Data sent: "cards" : Array of cards
--------------------------------------------------------------



Client -> Server events:

- "event" : "createNewGame" -> the user succesfully creates a hand
--------------------------------------------------------------
 Data sent: "playerId" : int
 Response: event -> joinedHand
--------------------------------------------------------------

- "event" : "joinGame" -> the user joins an available game
--------------------------------------------------------------
 Data sent: "playerId" : int, "hand_id" : int
--------------------------------------------------------------

- "event" : "dealCards" -> the user deals the cards in the the current game
--------------------------------------------------------------
 Data sent: "playerId" : int
            "handId" : int
--------------------------------------------------------------

- "event" : "message" -> the user sends a global message
--------------------------------------------------------------
 Data sent: "message" : str
--------------------------------------------------------------



"""
