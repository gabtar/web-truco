import { useContext, useState } from 'react';
import { TrucoContext } from '../../contexts/TrucoContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Card, HandStatus, Truco } from '../../types';

import ScoreBoard from './ScoreBoard';
import TrucoControls from './controls/TrucoControls';
import EnvidoControls from './controls/EnvidoControls';
import Table from './Table'

import './Board.css'

function Board() {

  const socket = useWebSocket();
  const { state } = useContext(TrucoContext);
  const { game, player } = state;
  const hand = game.current_hand;

  const [selectedCards, setSelectedCards] = useState<Card[]>();
  const [envidoValue, setEnvidoValue] = useState<number>(0);

  const handleSelectEnvidoCards = (card: Card) => {
    let envidoCardValue = Number(card.rank) < 10 ? Number(card.rank) : 0;

    if (selectedCards?.length === 1 && selectedCards[0].suit === card.suit && selectedCards[0] !== card) {
      setSelectedCards([...selectedCards, card]);
      setEnvidoValue(envidoValue + envidoCardValue + 20);
      return;
    }
    setSelectedCards([card]);
    setEnvidoValue(envidoCardValue);
  }

  const handleDealCards = () => socket.send(JSON.stringify({
    event: "dealCards",
    payload: { playerId: player.id, handId: game.id }
  }));

  const handlePlayCard = (card: Card) => socket.send(JSON.stringify({
    event: "playCard",
    payload: { playerId: player.id, handId: game.id, suit: card.suit, rank: card.rank }
  }));

  const handleChantTruco = () => socket.send(JSON.stringify({
    event: "chantTruco",
    payload: { playerId: player.id, handId: game.id, level: hand.truco_status + 1 }
  }));

  const handleClickCard = (card: Card) => {
    if (isEnvido) {
      handleSelectEnvidoCards(card);
    } else {
      handlePlayCard(card);
    }
  };

  const isEnvido = hand.envido.status === 'ACCEPTED';
  const isPlayerTurn = hand.player_turn === player.id ? true : false;
  const isChantTurn = hand.chant_turn === player.id ? true : false;
  const canDeal = hand.player_dealer === player.id && hand.status === 'NOT_STARTED' ? true : false;
  const isFinished = hand.winner !== '' ? false : true;
  const isNotStarted = hand.status === HandStatus.NOT_STARTED ? true : false;
  const isLocked = hand.status === HandStatus.LOCKED ? true : false;
  const envidoAvailable = !hand.envido.winner && hand.rounds.length === 1

  const cardAlreadyPlayed = (card: Card) => {
    return hand.rounds.map(
      (round) => round.cards_played.get(player.id)
    ).filter(
      (card_played) =>
        card_played?.rank === card.rank
        &&
        card_played?.suit === card.suit)
      .length > 0
  }

  const isCardDisabled = (card: Card): boolean => isEnvido ? !isChantTurn : (!isPlayerTurn || cardAlreadyPlayed(card));

  const cardsDealed = hand.cards_dealed.map((card: Card, index: number) =>
    <button key={index} className={selectedCards?.includes(card) ? "spanish-card selected" : "spanish-card"} disabled={isCardDisabled(card)} onClick={() => handleClickCard(card)}>{card.rank}{card.suit}</button>
  );

  return (
    <>
      <div className="game-status">
        {isFinished ? <h3>Ganador: {hand.winner} </h3> : ''}
        <div className="table">
          <Table />
        </div>
        <div className="score-board">
          <ScoreBoard />
        </div>
      </div>
      <div className="card-container">
        {cardsDealed}
      </div>
      <div>
        {canDeal ? <button onClick={handleDealCards} className="btn">Repartir Mano</button> : ''}

        {envidoAvailable ?
          <EnvidoControls hand={hand} player={player} selectedCards={selectedCards} envidoValue={envidoValue} />
          :
          ''
        }


        <button className="btn" disabled={!isPlayerTurn || !isChantTurn || isFinished || isNotStarted} onClick={handleChantTruco}>Cantar {Truco[hand.truco_status]}</button>
        <button className="btn" disabled={!isPlayerTurn || !isChantTurn || isFinished || !isPlayerTurn || isNotStarted}>Cantar Flor</button>

        {isLocked ?
          <TrucoControls hand={hand} player={player} />
          :
          ''
        }
      </div>
    </>
  );
}

export default Board;
