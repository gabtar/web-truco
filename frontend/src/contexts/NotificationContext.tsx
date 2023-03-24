import React, { createContext, useCallback, useState } from 'react';
import { Notification } from '../types';

const initialNotifications = new Array<Notification>();

const NotificationContext = createContext({
  notifications: initialNotifications,
  addNotification: (text: string, message: string, type: string) => {}
});

const NotificationProvider: React.FC<any> = ({children}) => {
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications);

  const addNotification = useCallback(
  (title: string, message: string, type: string) => {
       const notification_id = new Date().valueOf();

       setNotifications([
          ...notifications, 
          { id: new Date().valueOf() , title: title, message: message, type: type} as Notification]
       )

       // Removes the notification after 3sec
       setTimeout(
        () => setNotifications((notifications) =>
            notifications.filter((notification) => notification.id !== notification_id)
          )
       , 3000);

       }
  , [notifications, setNotifications]);

  return (
    <NotificationContext.Provider value={{notifications, addNotification}}>
      {children}
    </NotificationContext.Provider>
  )
};

export { NotificationProvider, NotificationContext };
