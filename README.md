# WebSocket TRUCO

Juego de Truco Argentino usando websockets


### Backend:
- [ ] Más tests/validaciones en socket_events
- [x] Funcionalidad para ir al mazo durante la partida
- [x] Notificar eventos de la partida por el socket (Ej Jugador 1 Gana el Envido/Canta x puntos)
- [x] Mejorar el tema del score(llega hasta 15)
- [x] Mejorar la lógica para determinar de quién es el siguiente turno. (ej si es parda juega el que empardó, etc)
- [x] Armar modelo de toda una partida/juego
- [ ] Si se desconecta del socket pierde y anuncia ganador?
- [ ] Anunciar ganador/Eliminar partida del repositorio

### Frontend:
- [x] No se puede cantar(desactivar botones) nada si no se han repartido las cartas
- [ ] Tipos en el reducer/generalizar acciones
- [x] Cambiar favicon! de react.
- [ ] Ajustes generales a los estilos
- [x] Notificar por alert cuando finaliza la mano/gana un jugador/canta truco
- [ ] Ver el tema del routeo a la partida, hay un error en la consola js
- [ ] Pasar layout del juego a css grid?
- [ ] Imágenes de las cartas

### Otros:
- [x] Dockerizar en algún momento
- [ ] Agregar base de datos?
- [ ] Averiguar seguridad/autorización/cors en websocket
- [ ] Ver reconexión en el socket


### Roadmap v0.1
- [x] Implementar truco
- [x] Implementar envido
- [x] Jugar hasta 15 puntos
