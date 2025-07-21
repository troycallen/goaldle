'use client';

interface Player {
  id: string;
  name: string;
  team: string;
  position: string;
  nationality: string;
  age: number;
  imageUrl?: string;
}

interface PlayerCardProps {
  player: Player;
  isCorrect?: boolean;
}

export default function PlayerCard({ player, isCorrect = false }: PlayerCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-4 border-2 ${
      isCorrect ? 'border-green-500 bg-green-50' : 'border-gray-200'
    }`}>
      <div className="flex items-center space-x-4">
        {player.imageUrl && (
          <img
            src={player.imageUrl}
            alt={player.name}
            className="w-16 h-16 rounded-full object-cover"
          />
        )}
        
        <div className="flex-1">
          <h3 className={`text-lg font-bold ${
            isCorrect ? 'text-green-700' : 'text-gray-800'
          }`}>
            {player.name}
            {isCorrect && ' ✅'}
          </h3>
          
          <div className="space-y-1 text-sm text-gray-600">
            <p><span className="font-medium">Team:</span> {player.team}</p>
            <p><span className="font-medium">Position:</span> {player.position}</p>
            <p><span className="font-medium">Nationality:</span> {player.nationality}</p>
            <p><span className="font-medium">Age:</span> {player.age}</p>
          </div>
        </div>
      </div>
    </div>
  );
}