'use client';

import { useState, useEffect } from 'react';
import ImageUpload from '@/components/ImageUpload';
import GuessInput from '@/components/GuessInput';
import PlayerCard from '@/components/PlayerCard';
import DailyChallenge from '@/components/DailyChallenge';
import ScoreDisplay from '@/components/ScoreDisplay';
import { GameState } from '@/utils/gameLogic';
import { scoringSystem, localStorageManager, GameScore } from '@/utils/scoring';

export default function Home() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [guess, setGuess] = useState('');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [hints, setHints] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [gameStartTime, setGameStartTime] = useState<Date | null>(null);
  const [isDailyChallenge, setIsDailyChallenge] = useState(false);
  const [showDailyChallenge, setShowDailyChallenge] = useState(true);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = async (isDaily: boolean = false) => {
    try {
      setLoading(true);
      const response = await fetch('/api/game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'start_new_game', data: { isDailyChallenge: isDaily } })
      });
      
      if (response.ok) {
        const result = await response.json();
        setGameState(result.gameState);
        setHints([]);
        setUploadedImage(null);
        setGameStartTime(new Date());
        setIsDailyChallenge(isDaily);
        setShowDailyChallenge(!isDaily);
      }
    } catch (error) {
      console.error('Error starting new game:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    const imageUrl = URL.createObjectURL(file);
    setUploadedImage(imageUrl);
    
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('image', file);
      
      const response = await fetch('/api/analyze-image', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Send analysis to game logic
        await fetch('/api/game', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            action: 'set_image_analysis', 
            data: { analysis: result.analysis } 
          })
        });
        
        setHints(result.hints || []);
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
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
        
        if (result.additionalHints) {
          setHints(prev => [...prev, ...result.additionalHints]);
        }

        // Handle game completion
        if (result.gameState.gameWon || result.gameState.gameLost) {
          const timeElapsed = gameStartTime 
            ? Math.floor((Date.now() - gameStartTime.getTime()) / 1000)
            : 0;
          
          if (result.gameState.gameWon) {
            const score = scoringSystem.calculateScore(
              result.gameState.attempts.length,
              timeElapsed,
              hints.length,
              true
            );

            const gameScore: GameScore = {
              playerId: 'anonymous', // In a real app, you'd have user IDs
              date: new Date().toISOString().split('T')[0],
              attempts: result.gameState.attempts.length,
              won: true,
              timeElapsed,
              hintsUsed: hints.length,
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

        {/* Daily Challenge */}
        {showDailyChallenge && (
          <DailyChallenge onStartDailyChallenge={() => startNewGame(true)} />
        )}

        {/* Game Container */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          {loading && (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Processing...</p>
            </div>
          )}
          
          {!uploadedImage ? (
            <ImageUpload onImageUpload={handleImageUpload} />
          ) : (
            <div className="space-y-6">
              {/* Uploaded Image */}
              <div className="text-center">
                <img 
                  src={uploadedImage} 
                  alt="Player to guess" 
                  className="max-w-md mx-auto rounded-lg shadow-md"
                />
              </div>

              {/* Hints from Image Analysis */}
              {hints.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-800 mb-2">🔍 Visual Clues:</h3>
                  <ul className="text-blue-700 text-sm space-y-1">
                    {hints.map((hint, index) => (
                      <li key={index}>• {hint}</li>
                    ))}
                  </ul>
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
                        hints.length,
                        true
                      )}
                      attempts={gameState.attempts.length}
                      timeElapsed={Math.floor((Date.now() - gameStartTime.getTime()) / 1000)}
                      won={true}
                    />
                  )}
                  
                  <div className="text-center space-x-4">
                    <button 
                      onClick={() => startNewGame(false)}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Play Again
                    </button>
                    {!isDailyChallenge && (
                      <button 
                        onClick={() => startNewGame(true)}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Daily Challenge
                      </button>
                    )}
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
                  <div className="space-x-4">
                    <button 
                      onClick={() => startNewGame(false)}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Try Again
                    </button>
                    <button 
                      onClick={() => startNewGame(true)}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Daily Challenge
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {/* Guess Input */}
                  <GuessInput onGuess={handleGuess} guess={guess} setGuess={setGuess} />

                  {/* Previous Attempts */}
                  {gameState?.attempts && gameState.attempts.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="font-semibold text-gray-700">Previous Guesses:</h3>
                      <div className="space-y-2">
                        {gameState.attempts.map((attempt, index) => (
                          <div key={index} className="bg-red-100 text-red-700 px-3 py-2 rounded-lg border">
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{attempt.playerName}</span>
                              <span className="text-sm">❌</span>
                            </div>
                            {attempt.player && (
                              <div className="text-xs mt-1 space-y-1">
                                <div className="flex space-x-4">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    attempt.similarity.team === 'correct' ? 'bg-green-200 text-green-800' :
                                    attempt.similarity.team === 'league_match' ? 'bg-yellow-200 text-yellow-800' :
                                    'bg-red-200 text-red-800'
                                  }`}>
                                    Team: {attempt.similarity.team}
                                  </span>
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    attempt.similarity.position === 'correct' ? 'bg-green-200 text-green-800' :
                                    attempt.similarity.position === 'similar' ? 'bg-yellow-200 text-yellow-800' :
                                    'bg-red-200 text-red-800'
                                  }`}>
                                    Position: {attempt.similarity.position}
                                  </span>
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    attempt.similarity.nationality === 'correct' ? 'bg-green-200 text-green-800' :
                                    'bg-red-200 text-red-800'
                                  }`}>
                                    Nation: {attempt.similarity.nationality}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      <p className="text-sm text-gray-500">
                        Attempts: {gameState.attempts.length}/{gameState.maxAttempts}
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <h3 className="font-semibold text-blue-800 mb-2">How to Play</h3>
          <p className="text-blue-600 text-sm">
            1. Upload or take a photo of a soccer player<br/>
            2. Guess the player&apos;s name<br/>
            3. You have 6 attempts to get it right!
          </p>
        </div>
      </div>
    </div>
  );
}