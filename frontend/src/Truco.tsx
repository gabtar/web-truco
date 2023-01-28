import React, { useState, useEffect, useCallback, useContext } from 'react'

import { useWebSocket } from './socket';
import { TrucoContext } from './context';

import Route from './components/Router/Route'
import Link from './components/Router/Link'
import GamesList from './components/GamesList/GamesList';
import Board from './components/Board/Board';
import Chat from './components/Chat/Chat';
import './App.css'


function Truco() {

  const socket = useWebSocket();

  const { state, dispatch } = useContext(TrucoContext);

  const [message, setMessage] = useState('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => setMessage(event.target.value);
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
    <div style={{ textAlign: "center" }}>
      <div>
        Menu:
        <Link href="/">| Home |</Link>
        <Link href="/game"> Partida |</Link>
      </div>

      <div>
        <h1> Web Socket Truco </h1>
        <p>Id: {state.playerId}</p>
      </div>

      {/* MAIN PAGE/LOBBY/CHAT */}
      <Route path="/">
        <>
          <Chat />
          <div>
            <p>Lista de manos en juego</p>
            <GamesList />
          </div>
        </>
      </Route>

      {/* EN PARTIDA */}
      {/* TODO más adelante, si esta jugando y abandola el path, hacerle un alert o algo que pierde ? */}
      <Route path="/game">
        <Board />
      </Route>
    </div>
  );
}

export default Truco;
