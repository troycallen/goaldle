'use client';

import { useState, useEffect } from 'react';
import MediaDisplay from '@/components/MediaDisplay';
import GuessInput from '@/components/GuessInput';
import PlayerCard from '@/components/PlayerCard';
// import DailyChallenge from '@/components/DailyChallenge'; // Removed - starting directly with game
import ScoreDisplay from '@/components/ScoreDisplay';
import GuessRow from '@/components/GuessRow';
import GuessTableHeader from '@/components/GuessTableHeader';
import { GameState } from '@/utils/gameLogic';
import { scoringSystem, localStorageManager, GameScore } from '@/utils/scoring';

export default function Home() {
  const [guess, setGuess] = useState('');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [gameStartTime, setGameStartTime] = useState<Date | null>(null);
  const [isDailyChallenge, setIsDailyChallenge] = useState(true);

  useEffect(() => {
    startNewGame(true); // Always start as daily challenge
  }, []);

  const startNewGame = async (isDaily: boolean = false) => {
    try {
      setLoading(true);
      // Reset all state
      setGameState(null);
      setGuess('');
      const response = await fetch('/api/game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'start_new_game', data: { isDailyChallenge: isDaily } })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Starting new game, result:', result);
        console.log('Game state attempts:', result.gameState?.attempts?.length);
        console.log('Game won/lost:', result.gameState?.gameWon, result.gameState?.gameLost);
        setGameState(result.gameState);
        setGameStartTime(new Date());
        setIsDailyChallenge(isDaily);
      }
    } catch (error) {
      console.error('Error starting new game:', error);
    } finally {
      setLoading(false);
    }
  };


  const handleGuess = async (playerGuess: string) => {
    if (!gameState || gameState.gameWon || gameState.gameLost) return;
    
    try {
      setLoading(true);
      const response = await fetch('/api/game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'make_guess', 
          data: { playerName: playerGuess } 
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setGameState(result.gameState);
        setGuess('');
        
        // Handle game completion
        if (result.gameState.gameWon || result.gameState.gameLost) {
          const timeElapsed = gameStartTime 
            ? Math.floor((Date.now() - gameStartTime.getTime()) / 1000)
            : 0;
          
          if (result.gameState.gameWon) {
            const score = scoringSystem.calculateScore(
              result.gameState.attempts.length,
              timeElapsed,
              0, // No hints used in new format
              true
            );

            const gameScore: GameScore = {
              playerId: 'anonymous', // In a real app, you'd have user IDs
              date: new Date().toISOString().split('T')[0],
              attempts: result.gameState.attempts.length,
              won: true,
              timeElapsed,
              hintsUsed: 0, // No hints used in new format
              score
            };

            localStorageManager.saveScore(gameScore);
          }
        }
      }
    } catch (error) {
      console.error('Error making guess:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center py-8">
          <h1 className="text-5xl font-bold text-green-700 mb-2">⚽ Goaldle</h1>
          <p className="text-lg text-gray-600">Guess the soccer player from the image!</p>
        </header>


        {/* Game Container */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          {loading ? (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading game...</p>
            </div>
          ) : gameState ? (
            <div className="space-y-6">
              {/* DEBUG INFO */}
              <div className="text-xs text-gray-500 p-2 bg-gray-100 rounded">
                Debug: Won={String(gameState.gameWon)} | Lost={String(gameState.gameLost)} | Attempts={gameState.attempts?.length || 0}
              </div>

              {/* SIMPLE IMAGE */}
              <div className="text-center">
                <div className="w-80 h-80 mx-auto bg-blue-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-2xl font-bold">MYSTERY PLAYER</span>
                </div>
              </div>

              {/* SIMPLE INPUT - ALWAYS SHOW FOR NOW */}
              <div className="space-y-4">
                <input 
                  type="text"
                  value={guess}
                  onChange={(e) => setGuess(e.target.value)}
                  placeholder="Enter player name..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 bg-white"
                />
                <button 
                  onClick={() => handleGuess(guess)}
                  className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700"
                >
                  Submit Guess
                </button>
              </div>

              {/* SIMPLE ATTEMPTS LIST */}
              {gameState.attempts && gameState.attempts.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold">Attempts:</h3>
                  {gameState.attempts.map((attempt, index) => (
                    <div key={index} className="p-2 bg-gray-100 rounded">
                      {attempt.playerName} - {attempt.isCorrect ? '✅ CORRECT!' : '❌ Wrong'}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-600">No game loaded</p>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-3 text-center">How to Play</h3>
          <div className="text-blue-600 text-sm space-y-2">
            <p>1. Study the blurred image of today&apos;s mystery player</p>
            <p>2. Guess any player name to see stat comparisons</p>
            <p>3. Use the color coding to guide your next guess:</p>
            <div className="flex justify-center space-x-4 mt-2">
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-xs">Correct</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span className="text-xs">Close</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-xs">Wrong</span>
              </div>
            </div>
            <p className="text-center mt-2">4. You have 6 attempts to identify the player!</p>
          </div>
        </div>
      </div>
    </div>
  );
}