import { useContext } from 'react';
import { SocketContext } from '../contexts/SocketContext';

export const useWebSocket = () => {
  const socket = useContext(SocketContext);
  
  return socket;
}
