import { createContext, ReactNode } from "react";

const ws = new WebSocket("ws://localhost/ws");

const SocketContext = createContext(ws);

interface ISocketProvider {
  children: ReactNode;
}

const SocketProvider = (props: ISocketProvider) => (
  <SocketContext.Provider value={ws}>{props.children}</SocketContext.Provider>
);

export { SocketContext, SocketProvider };

