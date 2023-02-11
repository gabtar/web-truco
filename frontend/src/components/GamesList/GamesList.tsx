import { useContext } from 'react';
import { TrucoContext } from '../../contexts/TrucoContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Game } from '../../types';
import './GamesList.css';

function GamesList() {
  const socket = useWebSocket();
  const { state } = useContext(TrucoContext);
  const { player, currentGames } = state;

  const handleCreateNewGame = () => socket.send(JSON.stringify({
    event: "createNewGame",
    payload: { playerId: player.id }
  }));

  // TODO on click llevar a la ruta de game interface
  const handleJoinGame = (handId: number) => socket.send(JSON.stringify({
    event: "joinGame",
    payload: { playerId: player.id, handId: handId }
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

  const emptyGamesList = <tr className="empty-games-list"><td colSpan={3}>No hay partidas</td></tr>;

  return (
    <div className="left-column">
      <h2>Partidas en juego</h2>
      <table className="games-list-table">
        <thead>
          <tr>
            <th className="thead">Nombre Partida</th>
            <th className="thead">Jugadores</th>
            <th className="thead">Unirse</th>
          </tr>
        </thead>
        <tbody>
          {currentGames.length === 0 ? emptyGamesList : gamesListRows}
        </tbody>
      </table>
      <input type="button" className="btn" value="Crear partida" onClick={handleCreateNewGame} />
    </div>
  )
  
}

export default GamesList;
