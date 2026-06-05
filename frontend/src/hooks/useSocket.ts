import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export const useSocket = (assignmentId: string | null) => {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (!assignmentId) return;

    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.emit('join', assignmentId);

    return () => {
      newSocket.close();
    };
  }, [assignmentId]);

  return socket;
};
