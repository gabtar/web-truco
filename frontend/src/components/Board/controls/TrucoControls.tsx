import { useWebSocket } from '../../../hooks/useWebSocket';
import { HandStatus, Truco } from '../../../types';

// TODO, Crear interfaz para tipos
export default function TrucoControls({ hand, player }: any) {

  const socket = useWebSocket();

  const isChantTurn = hand.chant_turn === player.id ? true : false;
  const isFinished = hand.status === HandStatus.FINISHED ? true : false;
  const isLocked = hand.status === HandStatus.LOCKED ? true : false;

  const isDisabled = isFinished || !isLocked || !isChantTurn;

  const handleResponseToTruco = (trucoLevel: number) => socket.send(JSON.stringify({
    event: "responseToTruco",
    payload: { playerId: player.id, handId: hand.id, level: trucoLevel }
  }));

  return (
    <div>
      Cantado: {Truco[hand.truco_status - 1]}
      <button
        className="btn"
        disabled={isDisabled} onClick={() => handleResponseToTruco(hand.truco_status)}
      >
        Quiero
      </button>
      {hand.truco_status > 3 ? '' :
        <button
          className="btn"
          disabled={isDisabled} onClick={() => handleResponseToTruco(hand.truco_status + 1)}
        >
          Quiero {Truco[hand.truco_status]}
        </button>

      }
      <button
        className="btn"
        disabled={isDisabled} onClick={() => handleResponseToTruco(hand.truco_status - 1)}
      >
        No quiero
      </button>
    </div>
  );
}

