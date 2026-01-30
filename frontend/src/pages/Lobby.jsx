import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Lobby() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [roomCode, setRoomCode] = useState('');

  const handleCreate = () => {
    // Generate random room ID (simplified)
    const newRoomId = Math.random().toString(36).substring(7);
    navigate(`/room/${newRoomId}`);
  };

  const handleJoin = () => {
    if (roomCode) navigate(`/room/${roomCode}`);
  };

  return (
    <div className="min-h-screen bg-poker-dark text-white p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
          <h1 className="text-3xl font-bold text-poker-gold">Lobby</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-300">
              Welcome, <span className="font-bold text-white">{user?.username}</span>
            </span>
            <div className="bg-gray-800 px-3 py-1 rounded text-poker-gold">
              Chips: {user?.chips}
            </div>
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition"
            >
              Logout
            </button>
            <button
              onClick={() => navigate('/leaderboard')}
              className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition"
            >
              🏆 Leaderboard
            </button>
          </div>
        </header>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold mb-4">Create Private Room</h2>
            <button
              onClick={handleCreate}
              className="w-full bg-poker-green py-2 rounded font-bold hover:bg-green-700 transition"
            >
              Create Table
            </button>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold mb-4">Join Room</h2>
            <input
              type="text"
              placeholder="Enter Room Code"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 mb-3 focus:border-poker-gold focus:outline-none"
            />
            <button
              onClick={handleJoin}
              className="w-full bg-blue-600 py-2 rounded font-bold hover:bg-blue-700 transition"
            >
              Join Table
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
