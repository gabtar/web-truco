import { MouseEventHandler, useContext } from 'react';
import { TrucoContext } from '../../context';
import { useWebSocket } from '../../socket';
import  Table from './Table'
import { Card } from '../../types';
import './Board.css'

function Board() {
  
  const socket = useWebSocket();
  const { state } = useContext(TrucoContext);
  const {playerCards, game, playerId} = state;

  const handleDealCards = () => socket.send(JSON.stringify({
    event: "dealCards",
    payload: { playerId: playerId, handId: game.id }
  }));

  const handlePlayCard = (suit: string, rank: string) => socket.send(JSON.stringify({
    event: "playCard",
    payload: { playerId: playerId, handId: game.id, suit: suit, rank: rank }
  }));

  const cardsDealed = playerCards.map((card: Card, index: number) => 
    <div key={index} className="spanish-card" onClick={() => handlePlayCard(card.suit, card.rank)}>{card.rank}{card.suit}</div>
  );
  /* UI - Debería mostrar las cartas del oponente o una sombra/avatar del oponente?
    Mostrar la mesa con las cartas jugadas
    Mostrar las cartas del jugador
    Mostrar una botonera/controles de la partida
    */

  return (
    <>
      <h3> Partida en juego </h3>
       {/* MOSTRAR 3 CARTAS DADAS VUELTA DEL OPONENTE/OPONENTES */}
       {/* CARTAS EN MESA */}
       <h3>Cartas en mesa:</h3>
       <Table />
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
