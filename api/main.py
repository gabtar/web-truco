import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from services.connection_manager import ConnectionManager, dep_connection_manager
from events.socket_events import socketController


app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint_new(
        websocket: WebSocket,
        manager: ConnectionManager = Depends(dep_connection_manager)
):
    player_id = await manager.connect(websocket)
    await socketController["gamesUpdate"](playerId=player_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            print("Total connected users: ", len(manager.active_connections))

            try:
                await socketController[data['event']](**data['payload'])
            except (Exception) as e:
                message = json.dumps({"event": "error", "message": str(e)})
                print("ERROR: ", message)
                await manager.send(json_string=message, player_id=data['payload']['playerId'])

    except WebSocketDisconnect:
        # TODO end the game, set a winner if user was playing a game
        # Notify all users
        # socketControler["endgame"](game_id)
        manager.disconnect(websocket)
        print("LOGGER:: User disconected")
