import { useState } from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';
import { HandStatus, EnvidoLevels, EnvidoStatus, Card } from '../../../types';

// TODO, Crear interfaz para tipos en vez de any
export default function EnvidoControls({ game, player }: any) {

  const socket = useWebSocket();

  // Durante el envido aceptado
  const [selectedCards, setSelectedCards] = useState<Card[]>();
  const [envidoValue, setEnvidoValue] = useState<number>(0);

  const handleSelectEnvidoCards = (card: Card) => {
    // Veo si hay alguna carta seleccionada
    // TODO Le aplica el css para highlight/border seleccionado
    // Si es != y igual palo -> suma +20. Sino cambia la selección
    let envidoCardValue = Number(card.rank) < 10 ? Number(card.rank) : 0;

    if (selectedCards?.length === 1 && selectedCards[0].suit === card.suit && selectedCards[0] !== card) {
      // Agrega la carta a la seleccion y suma +20
      setSelectedCards([...selectedCards, card]);
      setEnvidoValue(envidoValue + envidoCardValue + 20);
      return;
    }
    //setea la carta y calcula valor envido
    setSelectedCards([card]);
    setEnvidoValue(envidoCardValue);
  }

  const isChantTurn = game.chant_turn === player.id ? true : false;
  const isChanting = game.envido?.status === EnvidoStatus.CHANTING ? true : false; // Si ya ha sido cantado
  const isNotStarted = game.envido.status === EnvidoStatus.NOT_STARTED ? true : false;

  const isEnvido = game.status === HandStatus.ENVIDO ? true : false;

  const isDisabled = !isEnvido || !isChantTurn;

  const handlePlayEnvido = () => socket.send(JSON.stringify({
    event: "playEnvido",
    payload: { playerId: player.id, handId: game.id, cards: selectedCards }
  }));

  const handleChantEnvido = (level: number) => socket.send(JSON.stringify({
    event: "chantEnvido",
    payload: { playerId: player.id, handId: game.id, level: level }
  }));

  const handleResponseToEnvido = (envidoLevel: number) => socket.send(JSON.stringify({
    event: "responseToEnvido",
    payload: { playerId: player.id, handId: game.id, level: envidoLevel }
  }));

  const handleChant = (envidoLevel: number) => isChanting ? handleResponseToEnvido(envidoLevel) : handleChantEnvido(envidoLevel);

  const handleAcceptEnvido = () => socket.send(JSON.stringify({
    event: "acceptEnvido",
    payload: { playerId: player.id, handId: game.id }
  }))

  const handleDeclilneEnvido = () => socket.send(JSON.stringify({
    event: "declineEnvido",
    payload: { playerId: player.id, handId: game.id }
  }))

  return (
    <div>
      {isChanting || isNotStarted ?
        <>
          Cantado: {game.envido.chanted.map(
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
      {game.envido.status === EnvidoStatus.ACCEPTED && isChantTurn ?
        <div>
          Cantar:
          Clickea sobre las cartas y envía
          {game.cards_dealed.map((card: Card, index: number) =>
            <button key={index} className="spanish-card"
              onClick={() => handleSelectEnvidoCards(card)}
            >
              {card.rank}{card.suit}
            </button>
          )}
          <button className="btn" onClick={handlePlayEnvido}>
            Enviar {envidoValue}
          </button>
        </div>
        :
        ''
      }
    </div>
  );
}