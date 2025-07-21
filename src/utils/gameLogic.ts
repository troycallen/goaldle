import { Player, playerDB } from './playerDatabase';
import { ImageAnalysisResult } from './imageAnalysis';

export interface GameState {
  targetPlayer: Player | null;
  attempts: GuessAttempt[];
  gameWon: boolean;
  gameLost: boolean;
  maxAttempts: number;
  hints: string[];
  imageAnalysis: ImageAnalysisResult | null;
}

export interface GuessAttempt {
  playerName: string;
  player: Player | null;
  isCorrect: boolean;
  similarity: SimilarityCheck;
  timestamp: Date;
}

export interface SimilarityCheck {
  team: 'correct' | 'wrong' | 'league_match' | 'country_match';
  position: 'correct' | 'wrong' | 'similar';
  nationality: 'correct' | 'wrong';
  age: 'correct' | 'close' | 'wrong';
  height: 'correct' | 'close' | 'wrong';
}

export class GameLogic {
  private gameState: GameState;

  constructor() {
    this.gameState = this.initializeGame();
  }

  private initializeGame(): GameState {
    return {
      targetPlayer: null,
      attempts: [],
      gameWon: false,
      gameLost: false,
      maxAttempts: 6,
      hints: [],
      imageAnalysis: null
    };
  }

  startNewGame(isDailyChallenge: boolean = false): GameState {
    this.gameState = this.initializeGame();
    
    if (isDailyChallenge) {
      this.gameState.targetPlayer = playerDB.getDailyPlayer();
    } else {
      this.gameState.targetPlayer = playerDB.getRandomPlayer();
    }
    
    return this.gameState;
  }

  setImageAnalysis(analysis: ImageAnalysisResult): void {
    this.gameState.imageAnalysis = analysis;
    this.generateHintsFromAnalysis(analysis);
  }

  private generateHintsFromAnalysis(analysis: ImageAnalysisResult): void {
    const hints: string[] = [];
    
    if (analysis.playerFeatures.jersey_color) {
      hints.push(`The player is wearing a ${analysis.playerFeatures.jersey_color} jersey`);
    }
    
    if (analysis.playerFeatures.estimated_height) {
      hints.push(`The player appears to be ${analysis.playerFeatures.estimated_height} in height`);
    }
    
    if (analysis.playerFeatures.hair_color) {
      hints.push(`The player has ${analysis.playerFeatures.hair_color} hair`);
    }

    this.gameState.hints = hints;
  }

  makeGuess(playerName: string): { 
    gameState: GameState; 
    guessResult: GuessAttempt;
    additionalHints?: string[];
  } {
    if (this.gameState.gameWon || this.gameState.gameLost) {
      throw new Error('Game is already finished');
    }

    if (!this.gameState.targetPlayer) {
      throw new Error('Game not started');
    }

    const guessedPlayer = playerDB.getPlayerByName(playerName);
    const isCorrect = guessedPlayer?.id === this.gameState.targetPlayer.id;
    
    const similarity = this.calculateSimilarity(
      guessedPlayer || null, 
      this.gameState.targetPlayer
    );

    const guessAttempt: GuessAttempt = {
      playerName,
      player: guessedPlayer || null,
      isCorrect,
      similarity,
      timestamp: new Date()
    };

    this.gameState.attempts.push(guessAttempt);

    if (isCorrect) {
      this.gameState.gameWon = true;
    } else if (this.gameState.attempts.length >= this.gameState.maxAttempts) {
      this.gameState.gameLost = true;
    }

    // Generate additional hints based on guess
    const additionalHints = this.generateHintsFromGuess(guessAttempt);

    return {
      gameState: this.gameState,
      guessResult: guessAttempt,
      additionalHints
    };
  }

  private calculateSimilarity(guessedPlayer: Player | null, targetPlayer: Player): SimilarityCheck {
    if (!guessedPlayer) {
      return {
        team: 'wrong',
        position: 'wrong',
        nationality: 'wrong',
        age: 'wrong',
        height: 'wrong'
      };
    }

    return {
      team: this.compareTeams(guessedPlayer.team, targetPlayer.team),
      position: this.comparePositions(guessedPlayer.position, targetPlayer.position),
      nationality: guessedPlayer.nationality === targetPlayer.nationality ? 'correct' : 'wrong',
      age: this.compareAges(guessedPlayer.age, targetPlayer.age),
      height: this.compareHeights(guessedPlayer.height, targetPlayer.height)
    };
  }

  private compareTeams(guessedTeam: string, targetTeam: string): 'correct' | 'wrong' | 'league_match' | 'country_match' {
    if (guessedTeam === targetTeam) return 'correct';
    
    // Simple league matching (in production, you'd have proper league data)
    const premierLeagueTeams = ['Liverpool', 'Manchester City', 'Chelsea', 'Arsenal'];
    const laLigaTeams = ['Real Madrid', 'Barcelona', 'Atletico Madrid'];
    const bundesligaTeams = ['Bayern Munich', 'Borussia Dortmund'];
    
    const isInSameLeague = (
      (premierLeagueTeams.includes(guessedTeam) && premierLeagueTeams.includes(targetTeam)) ||
      (laLigaTeams.includes(guessedTeam) && laLigaTeams.includes(targetTeam)) ||
      (bundesligaTeams.includes(guessedTeam) && bundesligaTeams.includes(targetTeam))
    );
    
    return isInSameLeague ? 'league_match' : 'wrong';
  }

  private comparePositions(guessedPos: string, targetPos: string): 'correct' | 'wrong' | 'similar' {
    if (guessedPos === targetPos) return 'correct';
    
    // Group similar positions
    const forwards = ['Forward', 'Striker', 'Winger'];
    const midfielders = ['Midfielder', 'Attacking Midfielder', 'Defensive Midfielder'];
    const defenders = ['Defender', 'Centre-back', 'Full-back'];
    
    const isSimilar = (
      (forwards.includes(guessedPos) && forwards.includes(targetPos)) ||
      (midfielders.includes(guessedPos) && midfielders.includes(targetPos)) ||
      (defenders.includes(guessedPos) && defenders.includes(targetPos))
    );
    
    return isSimilar ? 'similar' : 'wrong';
  }

  private compareAges(guessedAge: number, targetAge: number): 'correct' | 'close' | 'wrong' {
    if (guessedAge === targetAge) return 'correct';
    if (Math.abs(guessedAge - targetAge) <= 2) return 'close';
    return 'wrong';
  }

  private compareHeights(guessedHeight: number, targetHeight: number): 'correct' | 'close' | 'wrong' {
    if (Math.abs(guessedHeight - targetHeight) <= 2) return 'correct';
    if (Math.abs(guessedHeight - targetHeight) <= 5) return 'close';
    return 'wrong';
  }

  private generateHintsFromGuess(attempt: GuessAttempt): string[] {
    const hints: string[] = [];
    
    if (!attempt.player || !this.gameState.targetPlayer) return hints;

    const { similarity } = attempt;
    const target = this.gameState.targetPlayer;

    if (similarity.nationality === 'correct') {
      hints.push(`✅ Correct nationality: ${target.nationality}`);
    }

    if (similarity.position === 'correct') {
      hints.push(`✅ Correct position: ${target.position}`);
    } else if (similarity.position === 'similar') {
      hints.push(`🟡 Similar position to ${target.position}`);
    }

    if (similarity.age === 'close') {
      hints.push(`🟡 Close age (within 2 years of ${target.age})`);
    }

    if (similarity.team === 'league_match') {
      hints.push(`🟡 Same league as the target player`);
    }

    return hints;
  }

  getGameState(): GameState {
    return { ...this.gameState };
  }

  getPlayerSuggestions(query: string): string[] {
    if (query.length < 2) return [];
    
    const players = playerDB.searchPlayers(query);
    return players.map(player => player.name).slice(0, 5);
  }
}

export const gameLogic = new GameLogic();