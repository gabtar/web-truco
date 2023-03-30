import { useContext } from "react";
import { TrucoContext } from "../../contexts/TrucoContext";
import './Board.css'

function Table() {
    const { state } = useContext(TrucoContext);
    const { game, player } = state;
    const hand = game.current_hand;

    const cardsPlayedByPlayer = (playerId: string) => hand.rounds.map((round, index) =>
      round.cards_played.get(playerId) === null ? '' :
      <div key={index} className="table-card">
        <img src={`./assets/images/cards/${round.cards_played.get(playerId)?.rank}${round.cards_played.get(playerId)?.suit}.png`} />
      </div>
    );

    const cardsPlayed = game.players.map((user) =>
          <div key={user.id} className="card-container">
            <>
              <div>
                <p>👤 {user.name} { user.id === player.id ? <b>(Tú)</b> : ''}</p>
                {hand.player_hand === user.id ? <div className="badge">✋Mano</div> : ''}
                {hand.player_dealer === user.id ? <div className="badge">🂠 Repartidor</div> : ''}
                {hand.player_turn === user.id ? <div className="badge">Turno</div> : ''}
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
