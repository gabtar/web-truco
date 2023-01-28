import { useContext } from 'react';
import { TrucoContext } from '../../context';
import { useWebSocket } from '../../socket';
import { Game } from '../../types';
import './GamesList.css';

function GamesList() {
  const socket = useWebSocket();
  const { state } = useContext(TrucoContext);
  const { playerId, currentGames } = state;

  const handleCreateNewGame = () => socket.send(JSON.stringify({
    event: "createNewGame",
    payload: { playerId: playerId }
  }));

  const handleJoinGame = (handId: number) => socket.send(JSON.stringify({
    event: "joinGame",
    payload: { playerId: playerId, handId: handId }
  }));

  const gamesListRows = currentGames.map((game: Game) => 
      <tr key={game.id} className="trow">
        <td>{game.name}</td>
        <td>{game.currentPlayers}</td>
        <td>
          <button type="button" className="btn" onClick={() => handleJoinGame(game.id)}>Unirse</button> 
        </td>
      </tr>
  );

  return (
    <>
      <table>
        <thead>
          <tr>
            <th className="thead">Nombre Partida</th>
            <th className="thead">Jugadores</th>
            <th className="thead">Unirse</th>
          </tr>
        </thead>
        <tbody>
          {gamesListRows}
        </tbody>
      </table>
      <input type="button" className="btn" value="Crear partida" onClick={handleCreateNewGame} />
    </>
  )
  
}

export default GamesList;
