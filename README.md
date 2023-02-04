# WebSocket TRUCO

Juego de Truco Argentino usando websockets

## EN PROGESO / TODO:

### Backend:
- [x] Desacople de los modelos básicos de dominio de la base de datos
- [ ] Agregar score de la mano (En proceso)
- [x] Agregar un servicio/manager para crear/buscar/borrar jugadores
- [ ] Mejorar el socketController
- [ ] Tests a los eventos del websocket/socketControler que devuelva los json
- [ ] Agregar envido
- [ ] Agregar niveles de truco

### Frontend:
- [x] Mejorar estilos/colores css
- [x] Mejorar ui en partida/ cartas en mesa
  - [ ] Notificar de que usuario es el turno.
  - [ ] Deshabilitar botones cuando no es el turno/no puede repartir, etc.
- [x] Notificador de errores/acciones inválidas durante la partida.
- [x] Usar la context API de react para guardar estado de la partida/juego
- [x] React router o usar context para navegar entre páginas
- [ ] Tipos en el reducer/generalizar acciones
- [x] Jugar la carta durante la partida y mostrar al oponente

### Otros:
- [x] Dockerizar en algún momento
- [ ] Agregar base de datos?
- [ ] Averiguar seguridad/autorización/cors en websocket
- [ ] Ver reconexión en el socket
