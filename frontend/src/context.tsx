import React, { createContext, ReactNode, useReducer } from 'react';
import { Game, Card } from './types'
import { socketReducer } from './reducers'

type initialStateType = {
  playerId: string,
  messages: string[],
  handId: number,
  currentGames: Array<Game>,
  playerCards: Array<Card>,
}

const emptyCard = {
  suit: '#',
  rank: '#',
} as Card;

const initialState = {
  playerId: '',
  // TODO, podría ser un array de mensajes de un length determinado por ej que guarde los últimos 20 mensajes del chat
  messages: [],
  currentGames: [],
  // Puede ser un joinedGame/playingGame y el id del game/hand
  // Habría que separar por loby, en partida, y extras
  handId: -1,
  playerCards: [emptyCard, emptyCard, emptyCard],
}

const TrucoContext = createContext<{
  state: initialStateType;
  dispatch: React.Dispatch<any>;
}>({
  state: initialState,
  dispatch: () => null
});

// Uso con multiples reducers
// const mainReducer = ({ products, shoppingCart }, action) => ({
//   products: productReducer(products, action),
//   shoppingCart: shoppingCartReducer(shoppingCart, action),
// });

const TrucoProvider: React.FC<any> = ({children}) => {
  const [state, dispatch] = useReducer(socketReducer, initialState);

  return (
    <TrucoContext.Provider value={{state, dispatch}}>
      {children}
    </TrucoContext.Provider>
  )
};

export { TrucoContext, TrucoProvider };
