# WebSocket TRUCO

Juego de Truco Argentino usando websockets


## EN PROGESO / TODO:


### Backend:
- [x] No se puede cantar nada si no se repartieron las cartas
- [ ] Más tests/validaciones, sobretodo al envido....
- [ ] Funcionalidad para ir al mazo durante la partida
- [ ] Notificar eventos de la partida por el socket (Ej Jugador 1 Gana el Envido/Canta x puntos)
- [ ] Mejorar el tema del score
- [ ] Agregar la lógica para determinar de quién es el siguiente turno. (ej si es parda juega el que empardó, etc)
- [ ] Armar modelo de toda una partida/juego

### Frontend:
- [x] No se puede cantar(desactivar botones) nada si no se han repartido las cartas
- [ ] Tipos en el reducer/generalizar acciones
- [x] Cambiar favicon! de react.
- [ ] Notificar por alert cuando finaliza la mano/gana un jugador/canta truco
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
- [ ] Jugar hasta 15 puntos
