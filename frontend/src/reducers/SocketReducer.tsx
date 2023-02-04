import { Card } from '../types';

export const trucoReducer = (state: any, action: any) => {
  const { event, payload } = action;

  switch (event) {
    case 'connect':
      return { ...state, player: payload.player };
    case 'message':
      // state stores the last 10 chat messages
      let current_messages = state.messages.length + 1 > 9 ? state.messages.slice(1,9) : state.messages;
      return { ...state, messages: [...current_messages, payload.message] };
    case 'gamesUpdate':
      return { ...state, currentGames: payload.gamesList };
    case 'joinedHand':
      // TODO, When join a hand, show game interface eg set path -> "/game?id=2193979"
      window.history.pushState({}, "", "/game");

      const navEvent = new PopStateEvent('popstate');
      window.dispatchEvent(navEvent);

      return { ...state,
        game: { ...state.game, 
          id: payload.handId,
          name: payload.name,
          players: payload.currentPlayers
        }
      };
    case 'newPlayerJoined':
      // Recive el player ID que se unió
      return {
        ...state, 
        game: { ...state.game,
          players: [...state.game.players, payload.player]
        }
      };
    case 'receiveDealedCards':
      return { ...state,
        game: { ...state.game,
          cards_dealed: payload.cards
        }
      };
    case 'cardPlayed':
      const cards_played = new Map<string, Card>();
      for (const key in payload.cardsPlayed) {
        cards_played.set(key, payload.cardsPlayed[key]);
      }

      return { ...state,
        game: { ...state.game,
          cards_played: cards_played
        }
      };
    default:
      console.log("Evento de WebSocket sin atender aún!!!");
      return { ...state }
      // throw new Error();
  }
}

// TODO otros reducer no relacionado con el socket?
// Separar reducers en cambios de estado Client -> Server
// y Server -> Client
