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
  CONSTRAINT playercard_pk PRIMARY KEY(player_id, card_id),
  CONSTRAINT playercard_player_fk FOREIGN KEY(player_id) REFERENCES player(id),
  CONSTRAINT playercard_card_fk FOREIGN KEY(card_id) REFERENCES card(id)
);

CREATE TABLE hand(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  player_turn TEXT,
  player_hand TEXT,
  current_round INT NOT NULL,
  CONSTRAINT hand_player_fk FOREIGN KEY (player_turn) REFERENCES player(id),
  CONSTRAINT turn_player_fk FOREIGN KEY (player_turn) REFERENCES player(id)
);

CREATE TABLE round(
  hand_id INT NOT NULL,
  card_id INT NOT NULL,
  player_id TEXT NOT NULL,
  round_number INT,
  CONSTRAINT round_pk PRIMARY KEY(hand_id, player_id, card_id),
  CONSTRAINT round_player_fk FOREIGN KEY(player_id) REFERENCES player(id),
  CONSTRAINT round_card_fk FOREIGN KEY(card_id) REFERENCES card(id),
  CONSTRAINT round_hand_fk FOREIGN KEY(hand_id) REFERENCES hand(id)
);
