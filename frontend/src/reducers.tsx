import { Game } from './types'

// TODO armar bien los tipos/interfaces de state y action
// Habría que también agregarle los tipos a los eventos
// Se podría separar en GameReducer(eventos durante partida) y 
// OtrosReducer(buscar mejor nombre) para eventos chat, crear juego, etc
export const socketReducer = (state: any, action: any) => {
  switch (action.event) {
    case 'connect':
      return { ...state, playerId: action.playerId };
    case 'message':
      // state stores the last 10 chat messages
      let current_messages = state.messages.length + 1 > 9 ? state.messages.slice(1,9) : state.messages;
      return { ...state, messages: [...current_messages, action.payload.message] };
    case 'gamesUpdate':
      return { ...state, currentGames: action.payload.gamesList };
    case 'joinedHand':
      // TODO, When join a hand, show game interface eg set path -> "/game?id=2193979"
      window.history.pushState({}, "", "/game");

      const navEvent = new PopStateEvent('popstate');
      window.dispatchEvent(navEvent);

      return { ...state,
        game: { ...state.game, 
          id: action.payload.handId,
          name: action.payload.name,
          currentPlayers: action.payload.currentPlayers
        }
      };
    case 'newPlayerJoined':
      // Recive el player ID que se unió
      return {
        ...state, 
        game: { ...state.game,
          currentPlayers: [...state.game.currentPlayers, action.payload.playerId]
        }
      };
    case 'receiveDealedCards':
      return { ...state, playerCards: action.payload.cards };
    case 'cardPlayed':
      let current_game: Game = state.game;
      current_game.rounds[action.round].cardPlayed.set(action.player,action.card);

      return { ...state, game: current_game }
    default:
      console.log("Evento de WebSocket sin atender aún!!!");
      return { ...state }
      // throw new Error();
  }
}

// TODO otros reducer no relacionado con el socket?
// Separar reducers en cambios de estado Client -> Server
// y Server -> Client
