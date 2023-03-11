import React, { createContext, useReducer } from 'react';
import { Game, Card, Message, GameState, Truco, Envido, EnvidoStatus, Player, HandStatus, HandState } from '../types';
import { trucoReducer } from '../reducers/SocketReducer';

export type TrucoStateType = {
  player: Player,
  messages: Array<Message>,
  currentGames: Array<Game>, // TODO, change to gamelist type or another interface for list games
  game: GameState
}

const emptyCard = {
  suit: '#',
  rank: '#',
} as Card;

const initialHandState : HandState = {
  id: '',
  player_turn: '',
  player_hand: '',
  chant_turn: '',
  player_dealer: '',
  cards_played: new Map<string, Card[]>(),
  cards_dealed: [emptyCard, emptyCard, emptyCard],
  rounds: [],
  envido: { chanted: [], winner: '', cards_played: new Map<string, Card[]>(), points: 0, status: EnvidoStatus.CHANTING} as Envido,
  winner: '',
  truco_status: Truco.NoCantado,
  status: HandStatus.NOT_STARTED,
}

const initialGameState : GameState = {
  id: '',
  players: [],
  current_hand: initialHandState,
  score: new Map<string, number>()
}

const initialTrucoState : TrucoStateType = {
  player: {id: '', name: ''} as Player,
  messages: new Array<Message>(),
  currentGames: new Array<Game>(),
  game: initialGameState
}

const TrucoContext = createContext<{
  state: TrucoStateType;
  dispatch: React.Dispatch<any>;
}>({
  state: initialTrucoState,
  dispatch: () => null
});

const TrucoProvider: React.FC<any> = ({children}) => {
  const [state, dispatch] = useReducer(trucoReducer, initialTrucoState);

  return (
    <TrucoContext.Provider value={{state, dispatch}}>
      {children}
    </TrucoContext.Provider>
  )
};

export { TrucoContext, TrucoProvider };
