/* Card */
export interface Card {
  suit: string,
  rank: string
}

export interface Game {
  id: number,
  name: string,
  currentPlayers: number
}

/* Chat message */
export interface Message {
  text: string,
  player: string,
  time: string,
}

/* Ingame notifications */
export interface Notification {
  id: number
  title: string,
  message: string,
}

// Contexto de la partida
export type Player = {
  id: string,
  name: string
}

export enum Truco {
  NoCantado,
  Truco,
  ReTruco,
  ValeCuatro
}

export enum Envido {
  NoCantado = 'NO_CANTADO',
  Envido = 'ENVIDO',
  RealEnvido = 'REAL_ENVIDO',
  FaltaEnvido = 'FALTA_ENVIDO'
}

export enum HandStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  LOCKED = 'LOCKED',
  FINISHED = 'FINISHED'
}

export type GameState = {
  id: number,
  players: Player[]
  player_turn: string,
  chant_turn: string,
  player_hand: string,
  player_dealer: string,
  cards_played: Map<string, Card[]>,
  cards_dealed: Card[],
  rounds: Round[],
  truco_status: Truco,
  envido_status: Envido,
  status: HandStatus,
  winner: string,
  // TODO, separar el score de la mano?
  score: Map<string, number>
}

export type Round = {
  cards_played: Map<string, Card>
}
