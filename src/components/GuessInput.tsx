'use client';

import { useState } from 'react';

interface GuessInputProps {
  onGuess: (guess: string) => void;
  guess: string;
  setGuess: (guess: string) => void;
}

export default function GuessInput({ onGuess, guess, setGuess }: GuessInputProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // Mock player suggestions - in a real app, this would come from an API
  const mockPlayers = [
    'Lionel Messi',
    'Cristiano Ronaldo',
    'Kylian Mbappé',
    'Erling Haaland',
    'Neymar Jr',
    'Kevin De Bruyne',
    'Mohamed Salah',
    'Robert Lewandowski',
    'Sadio Mané',
    'Virgil van Dijk',
    'Luka Modrić',
    'Karim Benzema',
    'Harry Kane',
    'Son Heung-min',
    'Bruno Fernandes'
  ];

  const handleInputChange = (value: string) => {
    setGuess(value);
    
    if (value.length > 1) {
      const filtered = mockPlayers.filter(player =>
        player.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5);
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (guess.trim()) {
      onGuess(guess.trim());
      setSuggestions([]);
    }
  };

  const handleSuggestionClick = (player: string) => {
    setGuess(player);
    setSuggestions([]);
    // Don't auto-submit - let user click the Submit button
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={guess}
            onChange={(e) => handleInputChange(e.target.value)}
            placeholder="Enter player name..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg"
            autoComplete="off"
          />
          
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-10 mt-1">
              {suggestions.map((player, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(player)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg"
                >
                  {player}
                </button>
              ))}
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={!guess.trim()}
          className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          Submit Guess
        </button>
      </form>
    </div>
  );
}