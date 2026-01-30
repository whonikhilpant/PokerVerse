import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Leaderboard() {
    const [leaders, setLeaders] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetch('http://localhost:8000/leaderboard')
            .then(res => res.json())
            .then(data => setLeaders(data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="min-h-screen bg-poker-dark text-white p-8">
            <div className="max-w-2xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-poker-gold">🏆 Leaderboard</h1>
                    <button
                        onClick={() => navigate('/')}
                        className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded"
                    >
                        Back to Lobby
                    </button>
                </div>

                <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-900">
                            <tr>
                                <th className="px-6 py-3 text-left">Rank</th>
                                <th className="px-6 py-3 text-left">Player</th>
                                <th className="px-6 py-3 text-right">Chips</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leaders.map((player) => (
                                <tr key={player.rank} className="border-t border-gray-700 hover:bg-gray-750">
                                    <td className="px-6 py-4">
                                        <span className={`font-bold ${player.rank === 1 ? 'text-yellow-400' : player.rank === 2 ? 'text-gray-400' : player.rank === 3 ? 'text-orange-600' : 'text-gray-500'}`}>
                                            #{player.rank}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-semibold">{player.username}</td>
                                    <td className="px-6 py-4 text-right text-poker-gold font-bold">
                                        {player.chips.toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}