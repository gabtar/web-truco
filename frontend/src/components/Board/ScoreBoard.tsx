import { useContext } from 'react';
import { TrucoContext } from '../../contexts/TrucoContext';
import './ScoreBoard.css'

function ScoreBoard() {
  const { state } = useContext(TrucoContext);
  const { game } = state;

  return (
    <>
      <h3>Puntaje</h3>
      <table className="score-table">
        <thead>
          <tr>
            {game.players.map((player) => 
              <td>{player.name}</td>
            )}
          </tr>
        </thead>
        <tbody>
          <tr>
            {game.players.map((player) => 
              <td>{game.score.get(player.id) ? game.score.get(player.id) : '0'}</td>
            )}
          </tr>
        </tbody>
      </table>
    </>
  )
}

export default ScoreBoard;
