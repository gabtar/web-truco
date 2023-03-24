import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from services.connection_manager import ConnectionManager, dep_connection_manager
from events.socket_events import SocketController, dep_socket_controller


app = FastAPI()


@app.websocket("/ws")
async def websocket_truco(
        websocket: WebSocket,
        manager: ConnectionManager = Depends(dep_connection_manager),
        socket_controller: SocketController = Depends(dep_socket_controller)
):
    player_id = await manager.connect(websocket)
    await socket_controller.call_event(
            event="gamesUpdate",
            payload={'playerId': player_id}
        )
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            print("Total connected users: ", len(manager.active_connections))

            try:
                await socket_controller.call_event(event=data['event'], payload=data['payload'])
            except (Exception) as e:
                # Notificación del error al front
                await socket_controller.call_event(
                        event="notify",
                        payload={'playerId': player_id, 'title': 'ERROR', 'message': str(e), 'type': 'ERROR'}
                )
                # Log del error en la consola
                print("ERROR: ", data)
                print("ERROR message: ", str(e))

    except WebSocketDisconnect:
        # TODO end the game, set a winner if user was playing a game
        # Notify all users
        manager.disconnect(websocket)
