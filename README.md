# WebSocket TRUCO

Juego de Truco Argentino usando websockets


## EN PROGESO / TODO:


### Backend:
- [x] Desacople de los modelos básicos de dominio de la base de datos
- [x] Agregar score de la mano (En proceso)
- [x] Agregar un servicio/manager para crear/buscar/borrar jugadores
- [x] Mejorar el socketController
- [x] Tests a los eventos del websocket/socketControler que devuelva los json
- [x] Reiniciar la mano cuando hay ganador
- [x] Refactorizar lógica del ganador de la mano
- [x] Si ya hay ganador que no se puedan jugar más cartas
- [x] Agregar niveles de truco / cantar truco
- [x] Agregar envido
- [ ] Más tests/validaciones, sobretodo al envido....
- [ ] Funcionalidad para ir al mazo durante la partida
- [ ] Notificar eventos de la partida por el socket (Ej Jugador 1 Gana el Envido/Canta x puntos)
- [ ] Mejorar el tema del score
- [ ] Agregar la lógica para determinar de quién es el siguiente turno. (ej si es parda juega el que empardó, etc)
- [ ] Armar modelo de toda una partida/juego

### Frontend:
- [x] Mejorar estilos/colores css
- [x] Mejorar ui en partida/ cartas en mesa
  - [x] Notificar de que usuario es el turno.
  - [x] Deshabilitar botones cuando no es el turno/no puede repartir, etc.
- [x] Notificador de errores/acciones inválidas durante la partida.
- [x] Usar la context API de react para guardar estado de la partida/juego
- [x] React router o usar context para navegar entre páginas
- [x] Mejorar jugabilidad/ Deshabilitar cartas al jugar
- [ ] Tipos en el reducer/generalizar acciones
- [x] Jugar la carta durante la partida y mostrar al oponente
- [ ] Mejorar el componente del envido/extraer a otros componentes/y mejoras en css
- [ ] Cambiar favicon! de react.
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
