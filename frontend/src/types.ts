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

export enum EnvidoLevels {
  // Valores 'mapeados' al enum de pydantic en el backend
  Envido = 2,
  RealEnvido = 3,
  FaltaEnvido = 30
}

export enum EnvidoStatus {
  NOT_STARTED = 'NOT_STARTED',
  CHANTING = 'CHANTING',
  ACCEPTED = 'ACCEPTED',
  FINISHED = 'FINISHED'
}

export enum HandStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  LOCKED = 'LOCKED',
  ENVIDO = 'ENVIDO',
  FINISHED = 'FINISHED'
}

export type Envido = {
  chanted: string[],
  points: number,
  cards_played: Map<string, Card[]>,
  winner: string,
  status: EnvidoStatus
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
  envido: Envido,
  truco_status: Truco,
  status: HandStatus,
  winner: string,
  // TODO, separar el score de la mano?
  score: Map<string, number>
}

export type Round = {
  cards_played: Map<string, Card>
}
