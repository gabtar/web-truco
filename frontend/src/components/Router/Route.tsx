import { ReactElement, useEffect, useState } from "react";

interface RouteProps {
  path: string
  children: ReactElement
}

const Route = ({ path, children } : RouteProps) : ReactElement | null => {

  // Ver de leer esto de un estado global/contexto/store
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const onLocationChange = () => {
      // Set the new path
      setCurrentPath(window.location.pathname);
    }

    window.addEventListener('popstate', onLocationChange);

    return () => {
      window.removeEventListener('popstate', onLocationChange);
    }
  }, [])

  return currentPath === path ? children : null
}

export default Route;
