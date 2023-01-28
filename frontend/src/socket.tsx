import { createContext, useContext, ReactNode } from "react";

const ws = new WebSocket("ws://localhost/ws");

// Context
export const SocketContext = createContext(ws);

interface ISocketProvider {
  children: ReactNode;
}

export const SocketProvider = (props: ISocketProvider) => (
  <SocketContext.Provider value={ws}>{props.children}</SocketContext.Provider>
);

// Hook
export const useWebSocket = () => {
  const socket = useContext(SocketContext);
  
  return socket;
}

