'use client';

import { useState } from 'react';
import { scoringSystem } from '@/utils/scoring';

interface ScoreDisplayProps {
  score: number;
  attempts: number;
  timeElapsed: number;
  won: boolean;
  onShare?: () => void;
}

export default function ScoreDisplay({ 
  score, 
  attempts, 
  timeElapsed, 
  won, 
  onShare 
}: ScoreDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);

  const rating = scoringSystem.getScoreRating(score);
  const shareText = scoringSystem.getShareText(
    score,
    attempts,
    won,
    new Date().toISOString().split('T')[0]
  );

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Goaldle Score',
          text: shareText,
        });
      } catch (error) {
        console.log('Error sharing:', error);
        copyToClipboard();
      }
    } else {
      copyToClipboard();
    }
    
    if (onShare) onShare();
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareText);
      alert('Score copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getRatingColor = (rating: string): string => {
    switch (rating) {
      case 'Legendary': return 'text-purple-600';
      case 'Excellent': return 'text-green-600';
      case 'Great': return 'text-blue-600';
      case 'Good': return 'text-teal-600';
      case 'Average': return 'text-yellow-600';
      case 'Fair': return 'text-orange-600';
      default: return 'text-red-600';
    }
  };

  if (!won) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
        <h3 className="text-lg font-semibold text-red-800 mb-2">Game Over</h3>
        <p className="text-red-600">Better luck next time!</p>
      </div>
    );
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center space-y-4">
      <div>
        <h3 className="text-2xl font-bold text-green-800 mb-2">🎉 Congratulations!</h3>
        <div className="space-y-2">
          <div className="text-3xl font-bold text-green-600">{score}</div>
          <div className={`text-lg font-semibold ${getRatingColor(rating)}`}>
            {rating}
          </div>
        </div>
      </div>

      <div className="flex justify-center space-x-6 text-sm text-gray-600">
        <div className="text-center">
          <div className="font-bold text-lg">{attempts}</div>
          <div>Attempts</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-lg">{formatTime(timeElapsed)}</div>
          <div>Time</div>
        </div>
      </div>

      <button
        onClick={() => setShowDetails(!showDetails)}
        className="text-blue-600 hover:text-blue-700 text-sm underline"
      >
        {showDetails ? 'Hide Details' : 'Show Details'}
      </button>

      {showDetails && (
        <div className="bg-white rounded p-4 text-left text-sm space-y-2">
          <div className="font-semibold text-gray-700">Score Breakdown:</div>
          <div className="space-y-1 text-gray-600">
            <div>Base Score: 1000</div>
            <div>Attempt Penalty: -{(attempts - 1) * 100}</div>
            <div>Time Bonus/Penalty: {timeElapsed < 120 ? '+' : '-'}{Math.abs((120 - timeElapsed) * 2)}</div>
            <div className="border-t pt-1 font-semibold">Final Score: {score}</div>
          </div>
        </div>
      )}

      <div className="space-y-2">
        <button
          onClick={handleShare}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
        >
          Share Score 📱
        </button>
        <div className="text-xs text-gray-500">
          Share your Goaldle achievement!
        </div>
      </div>
    </div>
  );
}