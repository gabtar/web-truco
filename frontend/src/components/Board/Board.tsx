import { useContext } from 'react';
import { TrucoContext } from '../../contexts/TrucoContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Card } from '../../types';
import ScoreBoard from './ScoreBoard';
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

  const isPlayerTurn = game.player_turn === player.id ? true : false;
  const isDealer = game.player_dealer === player.id ? true : false;
  const isFinished = game.winner != null ? true : false;

  const cardsDealed = game.cards_dealed.map((card: Card, index: number) => 
    <button key={index} className="spanish-card" disabled={!isPlayerTurn} onClick={() => handlePlayCard(card.suit, card.rank)}>{card.rank}{card.suit}</button>
  );

  return (
    <>
       <div className="game-status">
        <h1>GANADOR: {isFinished ? game.players.find((player) => player.id === game.winner)?.name : 'EN JUEGO'}</h1>
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
        {isDealer ? <button onClick={handleDealCards} className="btn">Repartir Mano</button> : '' }
        <button className="btn" disabled={!isPlayerTurn || !isFinished}>Cantar Envido</button>
        <button className="btn" disabled={!isPlayerTurn || !isFinished}>Cantar Truco</button>
        <button className="btn" disabled={!isPlayerTurn || !isFinished}>Cantar Flor</button>
       </div>
    </>
  );
}

export default Board;
