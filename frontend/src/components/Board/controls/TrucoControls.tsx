import { useWebSocket } from '../../../hooks/useWebSocket';
import { HandStatus, Truco } from '../../../types';

// TODO, Crear interfaz para tipos
export default function TrucoControls({ game, player }: any) {

  const socket = useWebSocket();

  const isChantTurn = game.chant_turn === player.id ? true : false;
  const isFinished = game.status === HandStatus.FINISHED ? true : false;
  const isLocked = game.status === HandStatus.LOCKED ? true : false;

  const isDisabled = isFinished || !isLocked || !isChantTurn;

  const handleResponseToTruco = (trucoLevel: number) => socket.send(JSON.stringify({
    event: "responseToTruco",
    payload: { playerId: player.id, handId: game.id, level: trucoLevel }
  }));

  return (
    <div>
      Cantado: {Truco[game.truco_status - 1]}
      <button
        className="btn"
        disabled={isDisabled} onClick={() => handleResponseToTruco(game.truco_status)}
      >
        Quiero
      </button>
      {game.truco_status > 3 ? '' :
        <button
          className="btn"
          disabled={isDisabled} onClick={() => handleResponseToTruco(game.truco_status + 1)}
        >
          Quiero {Truco[game.truco_status]}
        </button>

      }
      <button
        className="btn"
        disabled={isDisabled} onClick={() => handleResponseToTruco(game.truco_status - 1)}
      >
        No quiero
      </button>
    </div>
  );
}

