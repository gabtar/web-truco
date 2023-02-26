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
    payload: { playerId: player.id, handId: game.id, level: game.truco_status + 1 }
  }));

  const handleClickCard = (card: Card) => {
    if (isEnvido) {
      handleSelectEnvidoCards(card);
    } else {
      handlePlayCard(card);
    }
  };

  const isEnvido = game.envido.status === 'ACCEPTED';
  const isPlayerTurn = game.player_turn === player.id ? true : false;
  const isChantTurn = game.chant_turn === player.id ? true : false;
  const canDeal = game.player_dealer === player.id && game.status === 'NOT_STARTED' ? true : false;
  const isFinished = game.status === HandStatus.FINISHED ? true : false;
  const isNotStarted = game.status === HandStatus.NOT_STARTED ? true : false;
  const isLocked = game.status === HandStatus.LOCKED ? true : false;

  const cardAlreadyPlayed = (card: Card) => {
    return game.rounds.map(
      (round) => round.cards_played.get(player.id)
    ).filter(
      (card_played) =>
        card_played?.rank === card.rank
        &&
        card_played?.suit === card.suit)
      .length > 0
  }

  const isCardDisabled = (card: Card): boolean => isEnvido ? !isChantTurn : (!isPlayerTurn || cardAlreadyPlayed(card));

  const cardsDealed = game.cards_dealed.map((card: Card, index: number) =>
    <button key={index} className={selectedCards?.includes(card) ? "spanish-card selected" : "spanish-card"} disabled={isCardDisabled(card)} onClick={() => handleClickCard(card)}>{card.rank}{card.suit}</button>
  );

  return (
    <>
      <div className="game-status">
        {isFinished ? <h3>Ganador: {game.winner} </h3> : ''}
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

        <EnvidoControls game={game} player={player} selectedCards={selectedCards} envidoValue={envidoValue} />

        <button className="btn" disabled={!isPlayerTurn || !isChantTurn || isFinished || isNotStarted} onClick={handleChantTruco}>Cantar {Truco[game.truco_status]}</button>
        <button className="btn" disabled={!isPlayerTurn || !isChantTurn || isFinished || !isPlayerTurn || isNotStarted}>Cantar Flor</button>

        {isLocked ?
          <TrucoControls game={game} player={player} />
          :
          ''
        }
      </div>
    </>
  );
}

export default Board;
