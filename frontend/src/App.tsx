import { useState, useEffect, useCallback, useReducer } from 'react'
import { useWebSocket, SocketProvider } from './socket'
import GamesList from './components/GamesList';


function reducer(state: any, action: any) {
  switch (action.event) {
    case 'connect':
      return { ...state, playerId: action.player_id };
    case 'message':
      return { ...state, message: action.message };
    case 'gamesUpdate':
      return { ...state, totalGames: action.total_games };
    default:
      console.log("Default");
      console.log(action);
      return { ...state }
      // throw new Error();
  }
}

function App() {

  const socket = useWebSocket();

  const initialState = {
    playerId: '',
    message: '',
    totalGames: 0
  }
  const [state, dispatch] = useReducer(reducer, initialState);

  const [message, setMessage] = useState('');

  const handleChange = (event: any) => setMessage(event.target.value);
  const handleClick = () => socket.send(`{"event": "message", "message" : "${message}" }`);

  const onSocketEvent = useCallback(
    (message: any) => {
      const data = JSON.parse(JSON.stringify(message?.data));
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
        </div>
        <p>
          Último mensaje recibido: {state.message}
        </p>
        <div>
          <p>Enviar un mensaje</p>
          <input type="text" onChange={handleChange} />
          <input type="button" onClick={handleClick} value='Enviar' />
        </div>
        <p>Lista de manos en juego</p>
        <GamesList totalGames={state.totalGames} />
      </div>
    </SocketProvider>
  );
}

export default App;
