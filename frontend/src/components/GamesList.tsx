import { useWebSocket } from '../socket'
import { Game } from '../types'
import './GamesList.css'

interface props {
  currentGames: Game[],
  playerId: string
}

function GamesList({ currentGames, playerId } : props) {
  const socket = useWebSocket();

  const handleCreateNewGame = () => {
    socket.send(`{"event": "createNewGame", "playerId": "${playerId}"}`);
  }
  const handleJoinGame = (handId: number) => {
    socket.send(`{"event": "joinGame", "playerId": "${playerId}", "handId": "${handId}"}`);
  }

  const gamesList = currentGames.map((game: Game) => 
    <li key={game.id}>
      <div>
        {game.name}
      </div>
      <div>
        <button type="button" className="btn" onClick={() => handleJoinGame(game.id)}>Unirse</button> 
      </div>
    </li>
  );

  return (
    <>
      <ul>
        {gamesList}
      </ul>
      <input type="button" className="btn" value="Crear partida" onClick={handleCreateNewGame} />
    </>
  )
  
}

export default GamesList;
