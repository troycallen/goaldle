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
          {loading && (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading game...</p>
            </div>
          )}
          
          {gameState?.targetPlayer && (
            <div className="space-y-6">
              {console.log('Rendering game, attempts length:', gameState.attempts?.length)}
              
              {/* Player Media */}
              <MediaDisplay 
                player={gameState.targetPlayer} 
                revealed={gameState.gameWon || gameState.gameLost}
              />

              {/* Guess Input - Below the image */}
              {!gameState.gameWon && !gameState.gameLost && (
                <GuessInput onGuess={handleGuess} guess={guess} setGuess={setGuess} />
              )}

              {/* Wordle-style Guess Table - Only show if there are attempts */}
              {gameState.attempts && gameState.attempts.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-700 text-center">Your Guesses</h3>
                  <GuessTableHeader />
                  <div className="space-y-0">
                    {gameState.attempts.map((attempt, index) => (
                      <GuessRow key={index} attempt={attempt} index={index} />
                    ))}
                  </div>
                  <p className="text-sm text-gray-500 text-center">
                    Attempts: {gameState.attempts.length}/{gameState.maxAttempts}
                  </p>
                </div>
              )}

              {/* Progressive Hints - Only show if there are attempts */}
              {gameState.attempts.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-800 mb-2">💡 Hints:</h3>
                  <ul className="text-blue-700 text-sm space-y-1">
                    {gameState.targetPlayer.hints.slice(0, gameState.attempts.length).map((hint, index) => (
                      <li key={index}>• {hint}</li>
                    ))}
                  </ul>
                  {gameState.attempts.length < gameState.targetPlayer.hints.length && (
                    <p className="text-xs text-blue-600 mt-2 italic">
                      More hints unlock with each guess...
                    </p>
                  )}
                </div>
              )}

              {/* Game Won State */}
              {gameState?.gameWon ? (
                <div className="space-y-4">
                  {gameState.targetPlayer && (
                    <PlayerCard player={gameState.targetPlayer} isCorrect={true} />
                  )}
                  
                  {gameStartTime && (
                    <ScoreDisplay
                      score={scoringSystem.calculateScore(
                        gameState.attempts.length,
                        Math.floor((Date.now() - gameStartTime.getTime()) / 1000),
                        0, // No hints used in new format
                        true
                      )}
                      attempts={gameState.attempts.length}
                      timeElapsed={Math.floor((Date.now() - gameStartTime.getTime()) / 1000)}
                      won={true}
                    />
                  )}
                  
                  <div className="text-center">
                    <button 
                      onClick={() => startNewGame(true)}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Play Again
                    </button>
                  </div>
                </div>
              ) : gameState?.gameLost ? (
                <div className="text-center space-y-4">
                  <h2 className="text-2xl font-bold text-red-600">😔 Game Over!</h2>
                  <p className="text-gray-600">You&apos;ve used all your attempts.</p>
                  {gameState.targetPlayer && (
                    <div>
                      <p className="text-gray-700 mb-2">The correct answer was:</p>
                      <PlayerCard player={gameState.targetPlayer} />
                    </div>
                  )}
                  <div className="text-center">
                    <button 
                      onClick={() => startNewGame(true)}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              ) : null}
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