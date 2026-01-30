import { useState } from 'react';

export default function ChatBox({ messages, onSendMessage }) {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim()) {
            onSendMessage(input);
            setInput('');
        }
    };

    return (
        <div className="bg-gray-900 rounded-lg p-4 h-64 flex flex-col border border-gray-700">
            <h3 className="text-poker-gold font-bold mb-2">Table Chat</h3>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto mb-2 space-y-1">
                {messages.map((msg, i) => (
                    <div key={i} className="text-sm">
                        <span className="text-poker-gold font-semibold">{msg.username}:</span>
                        <span className="text-gray-300 ml-2">{msg.message}</span>
                    </div>
                ))}
            </div>

            {/* Input */}
            <div className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type a message..."
                    className="flex-1 bg-gray-800 border border-gray-600 rounded px-3 py-1 text-sm focus:outline-none focus:border-poker-gold"
                />
                <button
                    onClick={handleSend}
                    className="bg-poker-green hover:bg-green-700 px-4 py-1 rounded text-sm font-bold"
                >
                    Send
                </button>
            </div>
        </div>
    );
}