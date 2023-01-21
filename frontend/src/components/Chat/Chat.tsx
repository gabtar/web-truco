import { ReactNode } from 'react';
import { useState, useContext } from 'react';
import { useWebSocket } from '../../socket';
import { TrucoContext } from '../../context';
import './Chat.css';

// TODO en el mensaje agreagar la hora y el nombre del username?
const displayMessages = (messages: string[]): ReactNode => {
    return messages.map((message: string, index) => (
    <div key={index}>
        {message}
    </div>)
    );
};

function Chat() {
    const { state } = useContext(TrucoContext);

    const [message, setMessage] = useState('');
    const socket = useWebSocket();

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => setMessage(event.target.value);
    const handleClick = () => socket.send(`{"event": "message", "message" : "${message}" }`);

    return (
        <div>
            <h2>Chat</h2>
            <div className="chat-window">
                {displayMessages(state.messages)}
            </div>
            <p>Enviar mensaje</p>
            <input type="text" onChange={handleChange} />
            <input type="button" className="btn" onClick={handleClick} value='Enviar' />
        </div>
    );
}

export default Chat;