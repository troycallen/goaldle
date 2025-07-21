'use client';

import { useState, useEffect } from 'react';
import { localStorageManager, GameScore } from '@/utils/scoring';

interface DailyChallengeProps {
  onStartDailyChallenge: () => void;
}

export default function DailyChallenge({ onStartDailyChallenge }: DailyChallengeProps) {
  const [todayScore, setTodayScore] = useState<GameScore | null>(null);
  const [stats, setStats] = useState<{
    gamesPlayed: number;
    gamesWon: number;
    winRate: number;
    averageAttempts: number;
    bestScore: number;
    currentStreak: number;
    maxStreak: number;
  } | null>(null);

  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    const score = localStorageManager.getTodayScore(today);
    const userStats = localStorageManager.getStats();
    
    setTodayScore(score);
    setStats(userStats);
  }, []);

  const getTimeUntilMidnight = () => {
    const now = new Date();
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    
    const diff = midnight.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 mb-6">
      <div className="text-center mb-4">
        <h2 className="text-2xl font-bold text-purple-700 mb-2">
          🏆 Daily Challenge
        </h2>
        <p className="text-purple-600">
          {formatDate(new Date())}
        </p>
      </div>

      {todayScore ? (
        <div className="space-y-4">
          <div className="bg-white rounded-lg p-4 text-center">
            <h3 className="font-semibold text-gray-700 mb-2">Today&apos;s Result</h3>
            <div className="space-y-2">
              <p className="text-2xl font-bold text-green-600">
                {todayScore.won ? '🎉 Completed!' : '❌ Failed'}
              </p>
              <p className="text-gray-600">
                Score: <span className="font-bold">{todayScore.score}</span>
              </p>
              <p className="text-gray-600">
                Attempts: <span className="font-bold">{todayScore.attempts}/6</span>
              </p>
            </div>
          </div>
          
          <div className="text-center text-purple-600 text-sm">
            <p>Next challenge in: <span className="font-bold">{getTimeUntilMidnight()}</span></p>
          </div>
        </div>
      ) : (
        <div className="text-center space-y-4">
          <p className="text-purple-700 mb-4">
            Test your skills with today&apos;s featured player!
          </p>
          <button
            onClick={onStartDailyChallenge}
            className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors text-lg"
          >
            Start Daily Challenge
          </button>
        </div>
      )}

      {stats && (
        <div className="mt-6 bg-white rounded-lg p-4">
          <h3 className="font-semibold text-gray-700 mb-3 text-center">Your Stats</h3>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">{stats.gamesPlayed}</p>
              <p className="text-xs text-gray-600">Games Played</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats.winRate.toFixed(0)}%</p>
              <p className="text-xs text-gray-600">Win Rate</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">{stats.currentStreak}</p>
              <p className="text-xs text-gray-600">Current Streak</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">{stats.bestScore}</p>
              <p className="text-xs text-gray-600">Best Score</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}