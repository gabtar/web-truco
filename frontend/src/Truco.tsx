import { useEffect, useCallback, useContext } from 'react';

import { useWebSocket } from './hooks/useWebSocket';
import { useNotification } from './hooks/useNotification';

import { TrucoContext } from './contexts/TrucoContext';

import { Notification } from './types';

import Route from './components/Router/Route'
import NotificationAlert from './components/NotificationAlert/NotificationAlert';
import GamesList from './components/GamesList/GamesList';
import Board from './components/Board/Board';
import Chat from './components/Chat/Chat';
import NavBar from './components/NavBar/NavBar';
import './App.css'


function Truco() {
  const { notifications, addNotification } = useNotification();

  const socket = useWebSocket();

  const { dispatch } = useContext(TrucoContext);

  const onSocketEvent = useCallback(
    (message: any) => {
      const data = JSON.parse(message?.data);

      // Handles Notifications
      if (data.event === 'error' || data.event === 'notify') {
        const { title, text, type } = data.payload
        addNotification(title, text, type);
        return;
      }

      dispatch(data);
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
      <NavBar />
      {notifications.map((notification: Notification) => 
        <NotificationAlert 
          key={notification.id}
          id={notification.id}
          title={notification.title} 
          message={notification.message}
          type={notification.type}
          />
      )}

      {/* MAIN PAGE/LOBBY/CHAT */}
      <Route path="/">
          <div className="container">
              <GamesList />
              <Chat />
          </div>
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
