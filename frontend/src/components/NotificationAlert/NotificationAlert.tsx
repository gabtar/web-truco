import { Notification } from '../../types';
import './NotificationAlert.css';

function NotificationAlert({title, message} : Notification) {

  return(
    <div className="Notification">
      {title}: {message}
    </div>
  )
};

export default NotificationAlert;
