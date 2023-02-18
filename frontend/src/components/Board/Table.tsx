import { useContext } from "react";
import { TrucoContext } from "../../contexts/TrucoContext";
import './Board.css'

function Table() {
    const { state } = useContext(TrucoContext);
    const { game, player } = state;

    const cardsPlayedByPlayer = (playerId: string) => game.rounds.map((round, index) =>
      round.cards_played.get(playerId) === null ? '' :
      <div key={index} className="table-card">
        {round.cards_played.get(playerId)?.rank}{round.cards_played.get(playerId)?.suit}
      </div>
    );

    const cardsPlayed = game.players.map((user) =>
          <div key={user.id} className="card-container">
            <>
              <div>
                <p>👤 {user.name} { user.id === player.id ? <b>(Tú)</b> : ''}</p>
                {game.player_hand === user.id ? <div className="badge">✋Mano</div> : ''}
                {game.player_dealer === user.id ? <div className="badge">🂠 Repartidor</div> : ''}
                {game.player_turn === user.id ? <div className="badge">Turno</div> : ''}
              </div>
              {cardsPlayedByPlayer(user.id)}
            </>
          </div>
    );

    return (
        <>
          {cardsPlayed}
        </>
    );
}

export default Table;
