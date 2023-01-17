import { createContext, useContext, ReactChild, ReactNode } from "react";

const ws = new WebSocket("ws://localhost:80/ws");

// Context
export const SocketContext = createContext(ws);

interface ISocketProvider {
  // TODO use ReactNode ?
  children: ReactChild;
}

export const SocketProvider = (props: ISocketProvider) => (
  <SocketContext.Provider value={ws}>{props.children}</SocketContext.Provider>
);

// Hook
export const useWebSocket = () => {
  const socket = useContext(SocketContext);
  
  return socket;
}

