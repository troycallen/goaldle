'use client';

import Image from 'next/image';
import { Player } from '@/utils/playerDatabase';

interface MediaDisplayProps {
  player: Player;
  revealed?: boolean;
}

export default function MediaDisplay({ player, revealed = false }: MediaDisplayProps) {
  const { media } = player;

  return (
    <div className="relative">
      <div className="text-center space-y-4">
        {/* Media Container */}
        <div className="relative mx-auto max-w-md">
          {media.type === 'image' ? (
            <div className="relative w-full h-80 rounded-lg overflow-hidden shadow-lg">
              <Image
                src={media.url}
                alt={revealed ? `${player.name}` : media.description}
                fill
                className={`object-cover transition-all duration-500 ${
                  !revealed ? 'blur-md grayscale' : ''
                }`}
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
              {!revealed && (
                <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-4xl mb-2">❓</div>
                    <p className="text-sm">Guess the player!</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="relative w-full h-80 rounded-lg overflow-hidden shadow-lg bg-black">
              <video
                src={media.url}
                poster={media.thumbnail}
                controls={revealed}
                className={`w-full h-full object-cover ${
                  !revealed ? 'blur-md grayscale' : ''
                }`}
                muted
                loop
              >
                Your browser does not support the video tag.
              </video>
              {!revealed && (
                <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-4xl mb-2">🎥</div>
                    <p className="text-sm">Guess the player!</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Media Description */}
        <p className="text-gray-600 text-sm italic">
          {media.description}
        </p>

        {/* Game State Indicator */}
        <div className="text-xs text-gray-500">
          {revealed ? (
            <span className="text-green-600 font-semibold">✅ Player Revealed</span>
          ) : (
            <span>🔍 Can you identify this player?</span>
          )}
        </div>
      </div>
    </div>
  );
}