import { useState, useEffect, useCallback, useReducer } from 'react'
import { useWebSocket, SocketProvider } from './socket'
import GamesList from './components/GamesList';
import Board from './components/Board';
import { Card } from './types';
import './App.css'

// TODO, hacer un TrucoContext global que tenga un store con las
// varaibles de estado principales de la partida
// y mediante el reducer use el hook del socket para escuchar los eventos
// del server
function reducer(state: any, action: any) {
  switch (action.event) {
    case 'connect':
      return { ...state, playerId: action.playerId };
    case 'message':
      return { ...state, message: action.message };
    case 'gamesUpdate':
      return { ...state, currentGames: action.currentGames };
    case 'joinedHand':
      return { ...state, handId: action.handId };
    case 'receiveDealedCards':
      return { ...state, playerCards: action.cards };
    default:
      console.log("Evento de WebSocket sin atender aún!!!");
      console.log(action);
      return { ...state }
      // throw new Error();
  }
}

function App() {

  const socket = useWebSocket();

  // TODO, Extraer a un store / session context o algo así

  const emptyCard = {
    suit: '#',
    rank: '#',
  } as Card;

  const initialState = {
    playerId: '',
    message: '',
    handId: -1,
    currentGames: [],
    playerCards: [emptyCard, emptyCard, emptyCard]
  }

  const [state, dispatch] = useReducer(reducer, initialState);

  const [message, setMessage] = useState('');

  const handleChange = (event: any) => setMessage(event.target.value);
  const handleClick = () => socket.send(`{"event": "message", "message" : "${message}" }`);

  const onSocketEvent = useCallback(
    (message: any) => {
      const data = JSON.parse(JSON.stringify(message?.data));
      // TODO, delete, just to check message sended via socket
      console.log(JSON.parse(message?.data));
      dispatch(JSON.parse(data));
    }, [],
  );

  useEffect(() => {
    socket.addEventListener("message", onSocketEvent);

    return () => {
      socket.removeEventListener("message", onSocketEvent);
    }
  }, [socket, onSocketEvent])

  return (
    <SocketProvider>
      <div style={{textAlign: "center"}}>
        <div>
          <h1> Web Socket Truco </h1>
          <p>Id: {state.playerId}</p>
        </div> <p> Último mensaje recibido: {state.message} </p> <div>
          <p>Enviar un mensaje</p>
          <input type="text" onChange={handleChange} />
          <input type="button" className="btn" onClick={handleClick} value='Enviar' />
        </div>
        <div>
          <Board playerId={state.playerId} cards={state.playerCards} handId={state.handId}/>
        </div>
        <p>Lista de manos en juego</p>
        <GamesList currentGames={state.currentGames} playerId={state.playerId} />
      </div>
    </SocketProvider>
  );
}

export default App;
