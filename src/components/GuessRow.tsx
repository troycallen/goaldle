'use client';

import { GuessAttempt } from '@/utils/gameLogic';

interface GuessRowProps {
  attempt: GuessAttempt;
  index: number;
}

export default function GuessRow({ attempt, index }: GuessRowProps) {
  const { player, similarity } = attempt;

  if (!player) {
    return (
      <div className="grid grid-cols-6 gap-2 mb-2">
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Player</div>
          <div className="text-xs">Not Found</div>
        </div>
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Team</div>
          <div className="text-xs">-</div>
        </div>
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Position</div>
          <div className="text-xs">-</div>
        </div>
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Nationality</div>
          <div className="text-xs">-</div>
        </div>
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Age</div>
          <div className="text-xs">-</div>
        </div>
        <div className="bg-gray-100 p-3 rounded text-center text-gray-500">
          <div className="font-semibold text-sm">Height</div>
          <div className="text-xs">-</div>
        </div>
      </div>
    );
  }

  const getColorClass = (similarity: string) => {
    switch (similarity) {
      case 'correct':
        return 'bg-green-500 text-white';
      case 'close':
      case 'similar':
      case 'league_match':
        return 'bg-yellow-500 text-white';
      default:
        return 'bg-red-500 text-white';
    }
  };

  return (
    <div className="grid grid-cols-6 gap-2 mb-2">
      {/* Player Name */}
      <div className={`p-3 rounded text-center ${getColorClass(attempt.isCorrect ? 'correct' : 'wrong')}`}>
        <div className="font-semibold text-sm">Player</div>
        <div className="text-xs">{player.name}</div>
      </div>

      {/* Team */}
      <div className={`p-3 rounded text-center ${getColorClass(similarity.team)}`}>
        <div className="font-semibold text-sm">Team</div>
        <div className="text-xs">{player.team}</div>
      </div>

      {/* Position */}
      <div className={`p-3 rounded text-center ${getColorClass(similarity.position)}`}>
        <div className="font-semibold text-sm">Position</div>
        <div className="text-xs">{player.position}</div>
      </div>

      {/* Nationality */}
      <div className={`p-3 rounded text-center ${getColorClass(similarity.nationality)}`}>
        <div className="font-semibold text-sm">Nationality</div>
        <div className="text-xs">{player.nationality}</div>
      </div>

      {/* Age */}
      <div className={`p-3 rounded text-center ${getColorClass(similarity.age)}`}>
        <div className="font-semibold text-sm">Age</div>
        <div className="text-xs">{player.age}</div>
      </div>

      {/* Height */}
      <div className={`p-3 rounded text-center ${getColorClass(similarity.height)}`}>
        <div className="font-semibold text-sm">Height</div>
        <div className="text-xs">{player.height}cm</div>
      </div>
    </div>
  );
}