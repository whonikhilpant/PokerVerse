import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useWebSocket } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';
import ChatBox from '../components/poker/ChatBox';

function Card({ card, isRevealing = false }) {
    if (!card) return <div className="w-12 h-16 bg-gray-800 rounded border border-gray-600 m-1"></div>;

    const color = card.suit === 'Hearts' || card.suit === 'Diamonds' ? 'text-red-500' : 'text-black';
    const suitIcon = { 'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠' }[card.suit];

    return (
        <div
            className={`w-12 h-16 bg-white rounded flex flex-col items-center justify-center border border-gray-400 m-1 ${color} font-bold shadow-md transition-all duration-300 ${isRevealing ? 'animate-bounce' : ''} hover:scale-110 hover:shadow-xl`}
        >
            <span className="text-sm">{card.rank}</span>
            <span className="text-lg">{suitIcon}</span>
        </div>
    );
}

export default function GameRoom() {
    const { roomId } = useParams();
    const { connectToRoom, messages, sendMessage, isConnected } = useWebSocket();
    const { user } = useAuth();
    const [gameState, setGameState] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const navigate = useNavigate();

    const handleSendChat = (message) => {
        sendMessage('chat', { message });
    };

    useEffect(() => {
        connectToRoom(roomId);
    }, [roomId]);

    useEffect(() => {
        if (messages.length > 0) {
            const lastMsg = messages[messages.length - 1];

            // Handle game state updates
            if (lastMsg.state) {
                setGameState(lastMsg.state);
            }

            // Handle chat messages
            if (lastMsg.type === 'chat_message') {
                setChatMessages(prev => [...prev, lastMsg]);
            }
        }
    }, [messages]);


    if (!isConnected) {
        return <div className="text-white p-8">Connecting to Room {roomId}...</div>;
    }

    // Helper to find myself
    const myPlayer = gameState?.players.find(p => p.username === user.username);

    const handleAction = (action, amount = 0) => {
        sendMessage(action, { amount });
    };

    return (
        <div className="min-h-screen bg-poker-green relative overflow-hidden flex flex-col items-center justify-center text-white p-4">
            {/* Table Felt */}
            <div className="w-full max-w-4xl h-[600px] bg-[#2a503d] rounded-full border-[20px] border-[#4a2c2a] relative shadow-2xl flex items-center justify-center">

                {/* Pot */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                    <div className="text-poker-gold font-bold text-xl mb-2">POT: ${gameState?.pot || 0}</div>
                    <div className="flex bg-black/20 p-4 rounded-lg">
                        {gameState?.community_cards?.map((c, i) => <Card key={i} card={c} />)}
                    </div>
                </div>

                {/* Players (Simplified positioning) */}
                {gameState?.players.map((p, i) => (
                    <div key={i} className={`absolute flex flex-col items-center p-2 rounded-lg bg-black/50 backdrop-blur-sm
                ${i === 0 ? 'bottom-4' : i === 1 ? 'top-4' : 'left-4'} 
                ${p.is_turn ? 'border-2 border-poker-gold animate-pulse' : 'border border-gray-600'}
             `}>
                        <div className="font-bold">{p.username}</div>
                        <div className="text-poker-gold">${p.chips}</div>
                        {p.bet > 0 && <div className="text-xs bg-yellow-900 px-1 rounded">Bet: {p.bet}</div>}

                        {/* Hole Cards */}
                        <div className="flex mt-1">
                            {p.username === user.username ? (
                                // Show MY cards
                                p.hand && p.hand.length > 0 ? (
                                    p.hand.map((card, idx) => <Card key={idx} card={card} />)
                                ) : (
                                    [<Card key={1} card={null} />, <Card key={2} card={null} />]
                                )
                            ) : (
                                // Show opponent's cards as face-down
                                [<div key={1} className="w-10 h-14 bg-blue-900 border rounded m-0.5"></div>,
                                <div key={2} className="w-10 h-14 bg-blue-900 border rounded m-0.5"></div>]
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Controls */}
            <div className="mt-8 bg-gray-900 p-4 rounded-xl border border-gray-700 flex gap-4 w-full max-w-2xl justify-center z-10">
                {myPlayer?.is_turn ? (
                    <>
                        <button onClick={() => handleAction('fold')} className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded font-bold">Fold</button>
                        <button onClick={() => handleAction('check')} className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-bold">Check</button>
                        <button onClick={() => handleAction('call')} className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded font-bold">Call</button>
                        <button onClick={() => handleAction('raise', 100)} className="bg-yellow-600 hover:bg-yellow-700 px-6 py-2 rounded font-bold text-black text-center">Raise 100</button>
                    </>
                ) : (
                    <div className="text-gray-400 italic">Waiting for opponents...</div>
                )}
            </div>

            <button onClick={() => sendMessage('start_game')} className="absolute top-4 right-4 bg-purple-600 px-4 py-2 rounded shadow">Start Game</button>
            <div className="mt-4 max-w-md">
                <ChatBox messages={chatMessages} onSendMessage={handleSendChat} />
            </div>
        </div>
    );
}
