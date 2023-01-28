import { useContext } from "react";
import { TrucoContext } from "../../context";
import './Board.css'

function Table() {
    const { state } = useContext(TrucoContext);
    const { game } = state;

    const cardsPlayedByPlayer = (playerId: string) => game.rounds.map((round) => 
      <div key={round.roundNumber} className="spanish-card">
        {round.cardPlayed.get(playerId)?.rank}{round.cardPlayed.get(playerId)?.suit}
      </div>
    );

    const cardsPlayed = game.currentPlayers.map((player) =>
          <div key={player} className="card-container">
            <>
              <h5>{player}</h5>
              {cardsPlayedByPlayer(player)}
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
