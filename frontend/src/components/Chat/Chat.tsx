import { ReactNode } from 'react';
import { useState, useContext } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { TrucoContext } from '../../contexts/TrucoContext';
import { Message } from '../../types';
import './Chat.css';


// TODO en el mensaje agreagar la hora y el nombre del username?
const displayMessages = (messages: Message[]): ReactNode => {
    return messages.map((message: Message, index) => (
    <div key={index}>
        {message.time}({message.player}): {message.text}
    </div>)
    );
};

function Chat() {
    const { state } = useContext(TrucoContext);

    const [message, setMessage] = useState('');
    const socket = useWebSocket();

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => setMessage(event.target.value);

    const handleClick = () => socket.send(JSON.stringify({
      event: "message",
      payload: { playerId: state.player.id, message: message }
    }));

    return (
        <div className="right-column">
            <h2>Chat</h2>
            <div className="chat-window">
                {displayMessages(state.messages)}
            </div>
            <div>
              <input type="text" onChange={handleChange} placeholder="Enviar mensaje..." />
              <input type="button" className="btn" onClick={handleClick} value='Enviar' />
            </div>
        </div>
    );
}

export default Chat;
