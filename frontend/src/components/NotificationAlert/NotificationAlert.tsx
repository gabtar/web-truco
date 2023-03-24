import { Notification } from '../../types';
import './NotificationAlert.css';

function NotificationAlert({title, message, type} : Notification) {

  return(
    <div className={"notification " + (type === 'ERROR' ? 'error' : 'info')}>
      {title}: {message}
    </div>
  )
};

export default NotificationAlert;
