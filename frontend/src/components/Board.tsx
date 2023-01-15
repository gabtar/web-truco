import { useWebSocket } from '../socket';
import { Card } from '../types';
import './Board.css'

function Board({ cards, playerId, handId } : any) {
  
  const socket = useWebSocket();

  const handleDealCards = () => {
    socket.send(`{"event": "dealCards", "playerId": "${playerId}", "handId": "${handId}"}`);
  }

  const cardsDealed = cards.map((card: Card, index: number) => 
    <div key={index} className="spanish-card">{card.rank}{card.suit}</div>
  );
  /* UI - Debería mostrar las cartas del oponente o una sombra/avatar del oponente?
    Mostrar la mesa con las cartas jugadas
    Mostrar las cartas del jugador
    Mostrar una botonera/controles de la partida
    */

  return (
    <>
      <h3> Partida en juego </h3>
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
