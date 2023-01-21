import { ReactNode, MouseEvent } from 'react';

interface LinkProps {
  className?: string;
  href: string;
  children: ReactNode
}

const Link = ({ className, href, children } : LinkProps) : any  => {
  
  const onClick = (event: MouseEvent) : void => {
    // Prevent page reload
    event.preventDefault();
    // Update browser's url address bar
    window.history.pushState({}, "", href)

    // Tell Routes that url has been changed
    const navEvent = new PopStateEvent('popstate');
    window.dispatchEvent(navEvent);
  };

  return (
    <a className={className} href={href}onClick={onClick}>
      {children}
    </a>
  )
}

export default Link; 
