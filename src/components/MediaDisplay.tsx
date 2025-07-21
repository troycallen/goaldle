'use client';

// import Image from 'next/image'; // Temporarily using regular img for SVGs
import { Player } from '@/utils/playerDatabase';

interface MediaDisplayProps {
  player: Player;
  revealed?: boolean;
}

export default function MediaDisplay({ player, revealed = false }: MediaDisplayProps) {
  if (!player || !player.media) {
    return (
      <div className="relative mx-auto max-w-sm">
        <div className="relative w-full h-80 rounded-2xl overflow-hidden bg-gray-50 border border-gray-200 shadow-lg">
          <div className="flex items-center justify-center h-full text-gray-500 text-lg font-bold">
            ⚽ Loading player...
          </div>
        </div>
      </div>
    );
  }

  const { media } = player;

  return (
    <div className="relative mx-auto max-w-3xl">
      <div className="relative w-full h-[32rem] rounded-2xl overflow-hidden bg-gray-50 border border-gray-200 shadow-lg">
        {media.type === 'video' ? (
          <video
            src={media.url}
            className="w-full h-full object-contain transition-all duration-700"
            controls={revealed}
            autoPlay={!revealed}
            loop
            muted={!revealed}
            poster={media.thumbnail || ''}
          />
        ) : (
          <img
            src={media.url}
            alt={revealed ? `${player.name}` : "Mystery player"}
            className="w-full h-full object-contain transition-all duration-700"
            onError={(e) => {
              console.error('Image failed to load:', media.url);
              e.currentTarget.style.display = 'none';
              e.currentTarget.parentElement!.style.backgroundColor = '#6b7280';
              e.currentTarget.parentElement!.innerHTML = '<div class="flex items-center justify-center h-full text-white text-lg font-bold">⚽ MYSTERY PLAYER</div>';
            }}
          />
        )}
      </div>
    </div>
  );
}