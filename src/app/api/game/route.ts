import { NextRequest, NextResponse } from 'next/server';
import { gameLogic } from '@/utils/gameLogic';
import { playerDB } from '@/utils/playerDatabase';

export async function POST(request: NextRequest) {
  try {
    const { action, data } = await request.json();

    switch (action) {
      case 'start_new_game':
        const isDailyChallenge = data?.isDailyChallenge || false;
        const gameState = gameLogic.startNewGame(isDailyChallenge);
        return NextResponse.json({
          success: true,
          gameState: {
            ...gameState,
            targetPlayer: undefined // Don't reveal the answer
          }
        });

      case 'make_guess':
        const { playerName } = data;
        if (!playerName) {
          return NextResponse.json({ error: 'Player name is required' }, { status: 400 });
        }

        try {
          const result = gameLogic.makeGuess(playerName);
          return NextResponse.json({
            success: true,
            ...result,
            gameState: {
              ...result.gameState,
              targetPlayer: result.gameState.gameWon || result.gameState.gameLost 
                ? result.gameState.targetPlayer 
                : undefined
            }
          });
        } catch (error) {
          return NextResponse.json({ error: (error as Error).message }, { status: 400 });
        }

      case 'get_game_state':
        const currentState = gameLogic.getGameState();
        return NextResponse.json({
          success: true,
          gameState: {
            ...currentState,
            targetPlayer: currentState.gameWon || currentState.gameLost 
              ? currentState.targetPlayer 
              : undefined
          }
        });

      case 'get_player_suggestions':
        const { query } = data;
        const suggestions = gameLogic.getPlayerSuggestions(query);
        return NextResponse.json({
          success: true,
          suggestions
        });


      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Game API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  const allPlayers = playerDB.getAllPlayers();
  return NextResponse.json({
    success: true,
    players: allPlayers.map(player => ({
      id: player.id,
      name: player.name,
      team: player.team,
      nationality: player.nationality
    }))
  });
}