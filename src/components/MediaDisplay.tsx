'use client';

// import Image from 'next/image'; // Temporarily using regular img for SVGs
import { Player } from '@/utils/playerDatabase';

interface MediaDisplayProps {
  player: Player;
  revealed?: boolean;
}

export default function MediaDisplay({ player, revealed = false }: MediaDisplayProps) {
  const { media } = player;
  
  console.log('MediaDisplay - Player:', revealed ? player.name : '[HIDDEN]', 'Media URL:', media.url, 'Revealed:', revealed);

  return (
    <div className="relative mx-auto max-w-md">
      <div className="relative w-full h-80 rounded-lg overflow-hidden shadow-lg bg-gray-200">
        <img
          src={media.url}
          alt={revealed ? `${player.name}` : "Mystery player"}
          className={`w-full h-full object-cover transition-all duration-500 ${
            !revealed ? 'blur-lg grayscale' : ''
          }`}
          onError={(e) => {
            console.error('Image failed to load:', media.url);
            // Show a simple colored background if image fails
            e.currentTarget.style.display = 'none';
            e.currentTarget.parentElement!.style.backgroundColor = '#3b82f6';
            e.currentTarget.parentElement!.innerHTML = '<div class="flex items-center justify-center h-full text-white text-2xl font-bold">PLAYER IMAGE</div>';
          }}
          onLoad={() => console.log('Image loaded successfully:', media.url)}
        />
        {!revealed && (
          <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
            <div className="text-white text-center">
              <div className="text-4xl mb-2">❓</div>
              <p className="text-sm font-semibold">Mystery Player</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}