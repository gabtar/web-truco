import { useWebSocket } from '../socket'

function GamesList({ totalGames } : any) {
  const socket = useWebSocket();

  // TODO, for testing only
  const handleCreateNewGame = () => socket.send('{"event": "createNewGame", "player_id": "1111"}');

  return (
    <>
      <ul>
        <h1>{totalGames}</h1>
      </ul>
      <input type="button" value="Crear partida" onClick={handleCreateNewGame} />
    </>
  )
  
}

export default GamesList;
