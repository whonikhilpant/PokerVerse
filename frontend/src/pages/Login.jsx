import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            login(data.access_token);
            navigate('/');
        } catch (err) {
            setError('Invalid username or password');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-poker-dark text-white">
            <div className="bg-gray-800 p-8 rounded-lg shadow-xl w-96 border border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-center text-poker-gold">PokerVerse</h2>
                {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-400 mb-1">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-poker-gold"
                        />
                    </div>
                    <div>
                        <label className="block text-gray-400 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-poker-gold"
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-poker-green hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition duration-200"
                    >
                        Enter Table
                    </button>
                </form>
                <p className="mt-4 text-center text-gray-400">
                    New Player? <Link to="/register" className="text-poker-gold hover:underline">Register</Link>
                </p>
            </div>
        </div>
    );
}
