'use client';

// import Image from 'next/image'; // Temporarily using regular img for SVGs
import { Player } from '@/utils/playerDatabase';

interface MediaDisplayProps {
  player: Player;
  revealed?: boolean;
}

export default function MediaDisplay({ player, revealed = false }: MediaDisplayProps) {
  const { media } = player;
  
  console.log('MediaDisplay - Player:', player.name, 'Media URL:', media.url, 'Revealed:', revealed);

  return (
    <div className="relative">
      <div className="text-center space-y-4">
        {/* Media Container */}
        <div className="relative mx-auto max-w-md">
          {media.type === 'image' ? (
            <div className="relative w-full h-80 rounded-lg overflow-hidden shadow-lg">
              <img
                src={media.url}
                alt={revealed ? `${player.name}` : media.description}
                className={`w-full h-full object-cover transition-all duration-500 ${
                  !revealed ? 'blur-md grayscale' : ''
                }`}
                onError={(e) => {
                  console.error('Image failed to load:', media.url);
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                  e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQwMCIgZmlsbD0iIzMzNzNkYyIvPjx0ZXh0IHg9IjIwMCIgeT0iMjAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjZmZmZmZmIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiPk1FU1NJPC90ZXh0Pjwvc3ZnPg==';
                }}
                onLoad={() => console.log('Image loaded successfully:', media.url)}
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

      </div>
    </div>
  );
}