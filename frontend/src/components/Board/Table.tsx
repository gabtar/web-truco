import { useContext } from "react";
import { TrucoContext } from "../../contexts/TrucoContext";
import './Board.css'

function Table() {
    const { state } = useContext(TrucoContext);
    const { game, player } = state;

    const cardsPlayedByPlayer = (playerId: string) => game.cards_played.get(playerId)?.map((card, index) => 
      <div key={index} className="table-card">
        {card.rank}{card.suit}
      </div>
    );

    {/* TODO, mostrar nombre del jugador, badge con turno, si es mano, etc */}
    const cardsPlayed = game.players.map((player) =>
          <div key={player.id} className="card-container">
            <>
              <div>
                <p>👤 {player.name}</p>
                <div className="badge">Es Mano</div>
                <div className="badge">Turno</div>
              </div>
              {cardsPlayedByPlayer(player.id)}
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
