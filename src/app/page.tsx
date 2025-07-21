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
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <header className="text-center py-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">⚽ GOALDLE ⚽</h1>
          <p className="text-gray-600">Guess today's mystery soccer player!</p>
        </header>


        {/* Game Container */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-400 mx-auto"></div>
              <p className="text-gray-500 mt-4 font-medium">Loading today's challenge...</p>
            </div>
          ) : gameState ? (
            <div className="p-8 space-y-8">
              {/* Player Image */}
              {gameState.targetPlayer ? (
                <MediaDisplay 
                  player={gameState.targetPlayer} 
                  revealed={gameState.gameWon || gameState.gameLost}
                />
              ) : (
                <div className="relative mx-auto max-w-sm">
                  <div className="relative w-full h-80 rounded-2xl overflow-hidden bg-gray-50 border border-gray-200 shadow-lg">
                    <div className="flex items-center justify-center h-full text-gray-500 text-lg font-bold">
                      ⚽ Loading player...
                    </div>
                  </div>
                </div>
              )}

              {/* Game States */}
              {gameState.gameWon ? (
                /* GAME WON */
                <div className="text-center space-y-6">
                  <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                    <h2 className="text-2xl font-bold text-green-800 mb-2">🎉 Correct!</h2>
                    <p className="text-green-700 mb-4">You guessed it!</p>
                    <div className="text-xl font-bold text-gray-800">
                      {gameState.targetPlayer?.name}
                    </div>
                  </div>
                  <button 
                    onClick={() => startNewGame(true)}
                    className="bg-gray-800 text-white px-8 py-3 rounded-xl font-semibold hover:bg-gray-900 transition-colors shadow-lg"
                  >
                    Play Again Tomorrow
                  </button>
                </div>
              ) : gameState.gameLost ? (
                /* GAME LOST */
                <div className="text-center space-y-6">
                  <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                    <h2 className="text-2xl font-bold text-red-800 mb-2">😔 Game Over</h2>
                    <p className="text-red-700 mb-4">The answer was:</p>
                    <div className="text-xl font-bold text-gray-800">
                      {gameState.targetPlayer?.name}
                    </div>
                  </div>
                  <button 
                    onClick={() => startNewGame(true)}
                    className="bg-gray-800 text-white px-8 py-3 rounded-xl font-semibold hover:bg-gray-900 transition-colors shadow-lg"
                  >
                    Try Again Tomorrow
                  </button>
                </div>
              ) : (
                /* PLAYING STATE */
                <>
                  <GuessInput onGuess={handleGuess} guess={guess} setGuess={setGuess} />
                  
                  {gameState.attempts && gameState.attempts.length > 0 && (
                    <div className="space-y-4">
                      <h3 className="font-bold text-gray-800 text-center">Your Guesses</h3>
                      <GuessTableHeader />
                      <div className="space-y-1">
                        {gameState.attempts.map((attempt, index) => (
                          <GuessRow key={index} attempt={attempt} index={index} />
                        ))}
                      </div>
                      <div className="text-center">
                        <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                          {gameState.attempts.length}/{gameState.maxAttempts} attempts
                        </span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-gray-500">Failed to load game</p>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-6 mt-8">
          <h3 className="font-bold text-gray-800 mb-4 text-center">How to Play</h3>
          <div className="text-gray-600 text-sm space-y-3">
            <p>1. Study the blurred video of today's mystery player.</p>
            <p>2. Guess any player name to see stat comparison and how close you are to the answer.</p>
            <p>3. Use the color coding and hints from the video to guide your next guess.</p>
            <div className="flex justify-center space-x-6 mt-3">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-500 rounded-md"></div>
                <span className="text-xs font-medium">CORRECT</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-yellow-500 rounded-md"></div>
                <span className="text-xs font-medium">CLOSE</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-500 rounded-md"></div>
                <span className="text-xs font-medium">WRONG</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}