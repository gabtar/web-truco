import './ScoreBoard.css'

function ScoreBoard() {

  return (
    <>
      <h1>Puntaje</h1>
      <table className="score-table">
        <thead>
          <tr>
            <td>Jugador 1</td>
            <td>Jugador 2</td>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>5</td>
            <td>10</td>
          </tr>
        </tbody>
      </table>
    </>
  )

}

export default ScoreBoard;
