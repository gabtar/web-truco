import { useContext } from 'react';
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

  const handleDealCards = () => socket.send(JSON.stringify({
    event: "dealCards",
    payload: { playerId: player.id, handId: game.id }
  }));

  const handlePlayCard = (suit: string, rank: string) => socket.send(JSON.stringify({
    event: "playCard",
    payload: { playerId: player.id, handId: game.id, suit: suit, rank: rank }
  }));

  const handleChantTruco = () => socket.send(JSON.stringify({
    event: "chantTruco",
    payload: { playerId: player.id, handId: game.id, level: game.truco_status + 1 }
  }));

  const isPlayerTurn = game.player_turn === player.id ? true : false;
  const canDeal = game.player_dealer === player.id && game.status === 'NOT_STARTED' ? true : false;

  const isFinished = game.status === HandStatus.FINISHED ? true : false;
  const isLocked = game.status === HandStatus.LOCKED ? true : false;
  const isEnvidoAvailable = (true) ? true : false;

  // TODO, bastante rebuscado pero funciona. Hay que ver si se puede mejorar!
  const cardAlreadyPlayed = (card: Card) => {

    console.log(game.rounds.map(
      (round) => round.cards_played.get(player.id)
    ).filter((card_played) => card_played?.rank === card.rank && card_played?.suit === card.suit))

    return game.rounds.map(
      (round) => round.cards_played.get(player.id)
    ).filter(
      (card_played) =>
        card_played?.rank === card.rank
        &&
        card_played?.suit === card.suit)
      .length > 0
  }

  const cardsDealed = game.cards_dealed.map((card: Card, index: number) =>
    <button key={index} className="spanish-card" disabled={!isPlayerTurn || cardAlreadyPlayed(card)} onClick={() => handlePlayCard(card.suit, card.rank)}>{card.rank}{card.suit}</button>
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

        {isEnvidoAvailable ?
          <EnvidoControls game={game} player={player} />
          :
          ''
        }

        <button className="btn" disabled={!isPlayerTurn || isFinished} onClick={handleChantTruco}>Cantar {Truco[game.truco_status]}</button>
        <button className="btn" disabled={!isPlayerTurn || isFinished}>Cantar Flor</button>

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
