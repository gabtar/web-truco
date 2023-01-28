/* Truco Game Round */
export interface Round {
  roundNumber: number,  // Va de 0 a 2
  cardPlayed: Map<string, Card>
}

/* Truco game */
/* En realidad es el objecto Hand del backend */
export interface Game {
  id: number,
  name: string,
  currentPlayers: Array<string>,
  rounds: Round[]
}

/* Card */
export interface Card {
  suit: string,
  rank: string
}

/* Chat message */
export interface Message {
  text: string,
  player: string,
  time: string,
}
