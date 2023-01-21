# WebSocket TRUCO

Juego de Truco Argentino usando websockets

## EN PROGESO / TODO:

### Backend:
- [x] Modelos con pydantic.
- [x] Conectar a alguna DB para guardar los modelos.
- [x] Tests -> ver lo de mocks
- [x] Validaciones básicas al servicio
    - [x] No se puede crear nueva partida si ya esta jugando
    - [x] No se puede repartir cartas si el jugador no es mano
    - [x] No se puede unir a la partida si esta llena
    - [x] No se puede repartir si no hay suficientes jugadores
    - [x] No se puede jugar carta si ya jugó en el round
- [x] Agregar jugar carta
- [ ] Si ya jugaron todos la carta pasar al siguiente round
- [ ] Agregar score de la mano

### Frontend:
- [ ] Mejorar estilos/colores css
- [x] Usar la context API de react para guardar estado de la partida/juego
- [x] React router o usar context para navegar entre páginas
- [ ] Tipos en el reducer/generalizar acciones
- [ ] Jugar la carta durante la partida y mostrar al oponente

### Otros:
- [x] Dockerizar en algún momento
- [ ] Averiguar seguridad/autorización/cors en websocket
