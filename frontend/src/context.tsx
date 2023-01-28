import React, { createContext, useReducer } from 'react';
import { Game, Card, Message, Round } from './types'
import { socketReducer } from './reducers'

type initialStateType = {
  playerId: string,
  messages: Array<Message>,
  currentGames: Array<Game>,
  playerCards: Array<Card>,
  game: Game
}

const emptyCard = {
  suit: '#',
  rank: '#',
} as Card;

const emptyRound = (number: number) : Round => {
  return {
    roundNumber: number,
    cardPlayed: new Map<string, Card>() 
  }
}

const emptyGame = {
  id: -1,
  name: '',
  currentPlayers: [],
  rounds: [emptyRound(0), emptyRound(1), emptyRound(2)]
}

const initialState = {
  playerId: '',
  messages: [],
  currentGames: [],
  playerCards: [emptyCard, emptyCard, emptyCard],
  game: emptyGame,
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
