import { useWebSocket } from '../../../hooks/useWebSocket';
import { HandStatus, EnvidoLevels, EnvidoStatus } from '../../../types';

// TODO, Crear interfaz para tipos en vez de any
export default function EnvidoControls({ hand, player, selectedCards, envidoValue }: any) {

  const socket = useWebSocket();

  const isChantTurn = hand.chant_turn === player.id ? true : false;
  const isChanting = hand.envido?.status === EnvidoStatus.CHANTING ? true : false; // Si ya ha sido cantado
  const isInProgress = hand.status === HandStatus.IN_PROGRESS ? true : false;

  const isEnvido = hand.status === HandStatus.ENVIDO ? true : false;

  const isDisabled = !isEnvido || !isChantTurn;

  // TODO, reset las cartas elegidas
  const handlePlayEnvido = () => socket.send(JSON.stringify({
    event: "playEnvido",
    payload: { playerId: player.id, handId: hand.id, cards: selectedCards }
  }));

  const handleChantEnvido = (level: number) => socket.send(JSON.stringify({
    event: "chantEnvido",
    payload: { playerId: player.id, handId: hand.id, level: level }
  }));

  const handleResponseToEnvido = (envidoLevel: number) => socket.send(JSON.stringify({
    event: "responseToEnvido",
    payload: { playerId: player.id, handId: hand.id, level: envidoLevel }
  }));

  const handleChant = (envidoLevel: number) => isChanting ? handleResponseToEnvido(envidoLevel) : handleChantEnvido(envidoLevel);

  const handleAcceptEnvido = () => socket.send(JSON.stringify({
    event: "acceptEnvido",
    payload: { playerId: player.id, handId: hand.id }
  }))

  const handleDeclilneEnvido = () => socket.send(JSON.stringify({
    event: "declineEnvido",
    payload: { playerId: player.id, handId: hand.id }
  }))

  return (
    <div>
      {hand.envido.status === EnvidoStatus.ACCEPTED && isChantTurn ?
        <div>
          Envido:
          Clickeá sobre las cartas y envía
          <button className="btn" onClick={handlePlayEnvido}>
            Enviar {envidoValue}
          </button>
        </div>
        :
        ''
      }
      {isChanting || isInProgress ?
        <>
          Cantado: {hand.envido.chanted.map(
            (level: number, index: number) => <span key={index}> {EnvidoLevels[level]} </span>)
          }
          <div>
            <button className="btn" disabled={!isChantTurn} onClick={() => handleChant(EnvidoLevels.Envido)}>Envido</button>
            <button className="btn" disabled={!isChantTurn} onClick={() => handleChant(EnvidoLevels.RealEnvido)}>Real Envido</button>
            <button className="btn" disabled={!isChantTurn} onClick={() => handleChant(EnvidoLevels.FaltaEnvido)}>Falta Envido</button>
          </div>
          {isChanting && isChantTurn ?
            <>
              <button
                className="btn"
                disabled={isDisabled} onClick={handleAcceptEnvido}
              >
                Quiero
              </button>
              <button
                className="btn"
                disabled={isDisabled} onClick={handleDeclilneEnvido}
              >
                No quiero
              </button>
            </>
            :
            ''
          }
        </>
        :
        ''
      }
    </div>
  );
}
