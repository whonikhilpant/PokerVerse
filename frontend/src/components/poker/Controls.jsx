import { useState, useEffect } from 'react';

export default function Controls({ gameState, user, onAction }) {
    if (!gameState || !user) return null;

    const myPlayer = gameState.players.find(p => p.username === user.username);
    if (!myPlayer || !myPlayer.is_turn) {
        const currentPlayer = gameState.players.find(p => p.is_turn);
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-gray-400 italic text-lg animate-pulse">
                    Waiting for {currentPlayer?.username || 'opponents'}...
                </div>
            </div>
        );
    }

    const toCall = Number(gameState.current_bet) - Number(myPlayer.bet || 0);
    const canCheck = toCall === 0;

    // Logic for Raise limits
    // Minimum raise is usually double the current bet, or at least the big blind (20) if current bet is 0.
    const currentBet = Number(gameState.current_bet);
    const minRaise = currentBet > 0 ? currentBet * 2 : 20;

    // Max raise is limited by player's chips + what they already bet (total stack for the round)
    const maxRaise = Number(myPlayer.chips) + Number(myPlayer.bet || 0);

    // Ensure min <= max
    const safeMin = Math.min(minRaise, maxRaise);

    const [amount, setAmount] = useState(safeMin);

    // Reset amount when valid range changes
    useEffect(() => {
        setAmount(safeMin);
    }, [safeMin]);

    // Ensure slider updates correctly
    const handleSliderChange = (e) => {
        setAmount(Number(e.target.value));
    };

    const handleRaise = () => {
        onAction('raise', amount);
    };

    const canRaise = maxRaise >= minRaise;

    return (
        <div className="flex flex-col gap-4 w-full">
            {/* Action Buttons Row */}
            <div className="flex gap-4 justify-center">
                {/* FOLD */}
                <button
                    onClick={() => onAction('fold')}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-bold uppercase tracking-wider shadow-lg transform hover:-translate-y-1 transition-all"
                >
                    Fold
                </button>

                {/* CHECK / CALL (Dynamic Button) */}
                <button
                    onClick={() => onAction(canCheck ? 'check' : 'call')}
                    className={`${canCheck ? 'bg-blue-600 hover:bg-blue-700' : 'bg-green-600 hover:bg-green-700'} text-white px-6 py-3 rounded-lg font-bold uppercase tracking-wider shadow-lg transform hover:-translate-y-1 transition-all flex flex-col items-center leading-tight min-w-[120px]`}
                >
                    <span>{canCheck ? 'Check' : 'Call'}</span>
                    {!canCheck && <span className="text-xs opacity-80">${toCall}</span>}
                </button>
            </div>

            {/* Raise Section (Always render, disable if cannot raise) */}
            <div className={`bg-black/40 p-3 rounded-lg border border-white/10 flex items-center gap-3 transition-opacity ${!canRaise ? 'opacity-50 grayscale' : ''}`}>
                <div className="text-gray-300 font-bold text-sm">RAISE</div>

                <input
                    type="range"
                    min={minRaise}
                    max={maxRaise}
                    step={10}
                    value={amount}
                    onChange={handleSliderChange}
                    disabled={!canRaise}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-yellow-500 disabled:cursor-not-allowed"
                />

                <div className="bg-black/60 px-2 py-1 rounded text-yellow-500 font-mono font-bold min-w-[60px] text-center border border-yellow-500/30">
                    ${amount}
                </div>

                <button
                    onClick={handleRaise}
                    disabled={!canRaise}
                    className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:text-gray-400 text-black px-4 py-2 rounded font-bold uppercase text-sm shadow-lg transform hover:scale-105 active:scale-95 transition-all"
                >
                    Raise
                </button>
            </div>

            {/* Debug Info & Min message */}
            <div className="flex flex-col items-center">
                {!canRaise && toCall < myPlayer.chips && (
                    <div className="text-center text-xs text-gray-500 mb-1">Min Raise: ${minRaise} (Pool: ${gameState.current_bet})</div>
                )}

            </div>
        </div>
    );
}
