import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const { token } = useAuth();
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isConnected, setIsConnected] = useState(false);

    // We don't connect globally, but per room. 
    // However, for simplicity, we provide a connect function.
    const wsRef = useRef(null);

    const connectToRoom = (roomId) => {
        if (wsRef.current) {
            wsRef.current.close();
        }

        if (!token) return;

        const wsUrl = `ws://localhost:8000/ws/${roomId}?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to room:', roomId);
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMessages((prev) => [...prev, data]);
        };

        ws.onclose = () => {
            console.log('Disconnected from room:', roomId);
            setIsConnected(false);
        };

        wsRef.current = ws;
        setSocket(ws);
    };

    const sendMessage = (action, payload = {}) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ action, ...payload }));
        }
    };

    const disconnect = () => {
        if (wsRef.current) {
            wsRef.current.close();
            setSocket(null);
            setIsConnected(false);
        }
    };

    return (
        <WebSocketContext.Provider value={{ connectToRoom, sendMessage, messages, isConnected, disconnect }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => useContext(WebSocketContext);
