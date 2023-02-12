import { Card, Round } from '../types';

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

      return { ...state };
    case 'handUpdated':
      // Mapeo a la estructura de cartas en mesa
      const cards_in_hand = new Map<string, Card>();
      for (const key in payload.hand.cards_played) {
        cards_in_hand.set(key, payload.hand.cards_played[key]);
      }

      // Mapeo de los rounds
      let rounds: Round[] = [];
      for (const round of payload.hand.rounds) {
        const newRound = { cards_played: new Map<string, Card>() } as Round;
        for (const key in round.cards_played) {
          newRound.cards_played.set(key, round.cards_played[key]);
        }
        rounds.push(newRound);
      }

      return { ...state,
        game: { ...state.game, 
          id: payload.hand.id,
          name: payload.hand.name,
          players: payload.hand.players,
          player_hand: payload.hand.player_hand,
          player_dealer: payload.hand.player_dealer,
          player_turn: payload.hand.player_turn,
          cards_played: cards_in_hand,
          cards_dealed: payload.hand.cards_dealed,
          rounds: rounds,
          winner: payload.hand.winner,
          truco_status: payload.hand.truco_status,
          envido_status: payload.hand.envido,
        }
    }
    case 'updateScore':
      const score = new Map<string, number>();
      // Ojo!, Score del backend viene como {id , score}
      for (const key in payload.score.score) {
        score.set(key, payload.score.score[key]);
      }
      console.log(payload.score);

      return { ...state,
        game: { ...state.game,
          score: score,
        }
      }
    default:
      console.log("Evento de WebSocket sin atender aún!!!");
      return { ...state }
      // throw new Error();
  }
}

// TODO otros reducer no relacionado con el socket?
// Separar reducers en cambios de estado Client -> Server
// y Server -> Client
