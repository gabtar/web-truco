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

  const cardsDealed = game.cards_dealed.map((card: Card, index: number) => 
    <div key={index} className="spanish-card" onClick={() => handlePlayCard(card.suit, card.rank)}>{card.rank}{card.suit}</div>
  );
  /* UI - Debería mostrar las cartas del oponente o una sombra/avatar del oponente?
    Mostrar la mesa con las cartas jugadas
    Mostrar las cartas del jugador
    Mostrar una botonera/controles de la partida
    */

  return (
    <>
       <div className="game-status">
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
        <button onClick={handleDealCards} className="btn">Repartir Mano</button>
        <button className="btn">Cantar Envido</button>
        <button className="btn">Cantar Truco</button>
        <button className="btn">Cantar Flor</button>
       </div>
    </>
  );
}

export default Board;
