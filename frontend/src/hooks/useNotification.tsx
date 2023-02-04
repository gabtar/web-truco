import { useContext } from 'react';
import { NotificationContext } from '../contexts/NotificationContext';

export const useNotification = () => {
  const notification = useContext(NotificationContext);
  
  return notification;
}
