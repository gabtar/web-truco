
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
      return { ...state, messages: [...current_messages, action.message] };
    case 'gamesUpdate':
      return { ...state, currentGames: action.currentGames };
    case 'joinedHand':
      // TODO, When join a hand, show game interface eg set path -> "/game?id=2193979"
      return { ...state, handId: action.handId };
    case 'receiveDealedCards':
      return { ...state, playerCards: action.cards };
    default:
      console.log("Evento de WebSocket sin atender aún!!!");
      console.log(action);
      return { ...state }
      // throw new Error();
  }
}

// TODO otros reducer no relacionado con el socket?
// Separar reducers en cambios de estado Client -> Server
// y Server -> Client
