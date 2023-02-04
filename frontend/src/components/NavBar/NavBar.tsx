import { useContext } from 'react';
import Link from '../Router/Link';
import { TrucoContext }  from '../../contexts/TrucoContext';
import './NabBar.css';

function NavBar() {

  const { state } = useContext(TrucoContext);
  const { player } = state;

  return(
      <div className="navbar">
        <div className="logo">
          <div>
           	&#9749;
          Web Socket Truco
          <div>
            {/* TODO, mostrar circulo verde/rojo si esta conectado o desconectado? */}
            Nombre: {player.name}
          </div>
          </div>
        </div>
        <div>
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/game" className="nav-link">Partida</Link>
        </div>
      </div>
  )
}

export default NavBar;
