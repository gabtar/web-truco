import { useContext } from 'react';
import { TrucoContext } from '../../contexts/TrucoContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Card, HandStatus, Truco } from '../../types';

import ScoreBoard from './ScoreBoard';
import TrucoControls from './controls/TrucoControls';
import  Table from './Table'

import './Board.css'

function Board() {

  const socket = useWebSocket();
  const { state } = useContext(TrucoContext);
  const {game, player} = state;

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
  const canDeal = game.player_dealer === player.id && game.status !== 'IN_PROGRESS' ? true : false;

  const isFinished = game.status === HandStatus.FINISHED ? true : false; 
  const isLocked = game.status === HandStatus.LOCKED ? true : false;

  const cardsDealed = game.cards_dealed.map((card: Card, index: number) => 
    <button key={index} className="spanish-card" disabled={!isPlayerTurn} onClick={() => handlePlayCard(card.suit, card.rank)}>{card.rank}{card.suit}</button>
  );

  return (
    <>
       <div className="game-status">
       {isFinished ? <h3>Ganador: {game.winner} </h3> : '' }
        <div className="table">
          <Table />
        </div>
        <div className="score-board">
           <ScoreBoard />
        </div>
       </div>
       <div  className="card-container">
        {cardsDealed}
       </div>
       <div>
        {canDeal ? <button onClick={handleDealCards} className="btn">Repartir Mano</button> : '' }
        <button className="btn" disabled={!isPlayerTurn || isFinished}>Cantar Envido</button>
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
