import { SocketProvider } from './socket'
import { TrucoProvider } from './context'
import Truco from './Truco';


function App() {
  return (
    <TrucoProvider>
      <SocketProvider>
        <Truco />
      </SocketProvider>
    </TrucoProvider>
  );
}

export default App;
