import { SocketProvider } from './contexts/SocketContext';
import { TrucoProvider } from './contexts/TrucoContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Truco from './Truco';


function App() {
  return (
    <NotificationProvider>
      <TrucoProvider>
        <SocketProvider>
          <Truco />
        </SocketProvider>
      </TrucoProvider>
    </NotificationProvider>
  );
}

export default App;
