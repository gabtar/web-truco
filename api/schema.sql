-- Sqlite database schema

CREATE TABLE player(
  id TEXT NOT NULL,
  name TEXT NOT NULL,
  playing_hand INT
);

CREATE TABLE card(
  id INT PRIMARY KEY NOT NULL,
  rank TEXT NOT NULL,
  suit TEXT NOT NULL,
  value INT NOT NULL
);

CREATE TABLE playercard(
  player_id TEXT NOT NULL,
  card_id INT NOT NULL,
  CONSTRAINT playercard_pk PRIMARY KEY(player_id, card_id)
  CONSTRAINT playercard_player_fk FOREIGN KEY(player_id) REFERENCES player(id)
  CONSTRAINT playercard_card_fk FOREIGN KEY(card_id) REFERENCES card(id)
);

CREATE TABLE hand(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  player_turn TEXT,
  current_round INT NOT NULL,
  CONSTRAINT hand_player_fk FOREIGN KEY (player_turn) REFERENCES player(id)
);
