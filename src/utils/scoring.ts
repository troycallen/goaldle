export interface GameScore {
  playerId: string;
  date: string;
  attempts: number;
  won: boolean;
  timeElapsed: number; // in seconds
  hintsUsed: number;
  score: number;
}

export interface DailyStats {
  date: string;
  totalPlayers: number;
  averageAttempts: number;
  winRate: number;
  distribution: { [attempts: number]: number };
}

export class ScoringSystem {
  private readonly MAX_SCORE = 1000;
  private readonly ATTEMPT_PENALTY = 100;
  private readonly TIME_BONUS_THRESHOLD = 120; // seconds
  private readonly HINT_PENALTY = 50;

  calculateScore(
    attempts: number,
    timeElapsed: number,
    hintsUsed: number,
    won: boolean
  ): number {
    if (!won) return 0;

    let score = this.MAX_SCORE;
    
    // Penalty for attempts (fewer attempts = higher score)
    score -= (attempts - 1) * this.ATTEMPT_PENALTY;
    
    // Time bonus (faster = higher score)
    if (timeElapsed < this.TIME_BONUS_THRESHOLD) {
      const timeBonus = (this.TIME_BONUS_THRESHOLD - timeElapsed) * 2;
      score += timeBonus;
    } else {
      const timePenalty = Math.min((timeElapsed - this.TIME_BONUS_THRESHOLD) * 1, 200);
      score -= timePenalty;
    }
    
    // Penalty for using hints
    score -= hintsUsed * this.HINT_PENALTY;
    
    return Math.max(0, Math.round(score));
  }

  getScoreRating(score: number): string {
    if (score >= 900) return 'Legendary';
    if (score >= 800) return 'Excellent';
    if (score >= 700) return 'Great';
    if (score >= 600) return 'Good';
    if (score >= 500) return 'Average';
    if (score >= 300) return 'Fair';
    return 'Poor';
  }

  getShareText(
    score: number,
    attempts: number,
    won: boolean,
    date: string
  ): string {
    const emoji = this.getScoreEmoji(score);
    const attemptSquares = this.generateAttemptSquares(attempts, won);
    
    return `⚽ Goaldle ${date}\n\n${attemptSquares}\n\nScore: ${score} ${emoji}\n\nPlay at: [Your Website URL]`;
  }

  private getScoreEmoji(score: number): string {
    if (score >= 900) return '🏆';
    if (score >= 800) return '🥇';
    if (score >= 700) return '🥈';
    if (score >= 600) return '🥉';
    if (score >= 500) return '⭐';
    if (score >= 300) return '👍';
    return '🤔';
  }

  private generateAttemptSquares(attempts: number, won: boolean): string {
    const squares = [];
    const maxAttempts = 6;
    
    for (let i = 1; i <= maxAttempts; i++) {
      if (i < attempts) {
        squares.push('🟥'); // Failed attempt
      } else if (i === attempts && won) {
        squares.push('🟩'); // Winning attempt
      } else if (i === attempts && !won) {
        squares.push('🟥'); // Final failed attempt
      } else {
        squares.push('⬜'); // Unused attempt
      }
    }
    
    return squares.join('');
  }
}

export class LocalStorageManager {
  private readonly SCORES_KEY = 'goaldle_scores';
  private readonly STATS_KEY = 'goaldle_stats';
  private readonly STREAK_KEY = 'goaldle_streak';

  saveScore(score: GameScore): void {
    const scores = this.getScores();
    scores.push(score);
    
    // Keep only last 100 scores
    if (scores.length > 100) {
      scores.splice(0, scores.length - 100);
    }
    
    localStorage.setItem(this.SCORES_KEY, JSON.stringify(scores));
    this.updateStats(score);
  }

  getScores(): GameScore[] {
    const stored = localStorage.getItem(this.SCORES_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  getTodayScore(date: string): GameScore | null {
    const scores = this.getScores();
    return scores.find(score => score.date === date) || null;
  }

  getStats(): {
    gamesPlayed: number;
    gamesWon: number;
    winRate: number;
    averageAttempts: number;
    bestScore: number;
    currentStreak: number;
    maxStreak: number;
  } {
    const scores = this.getScores();
    const wonGames = scores.filter(score => score.won);
    
    const currentStreak = this.getCurrentStreak();
    const maxStreak = this.getMaxStreak();
    
    return {
      gamesPlayed: scores.length,
      gamesWon: wonGames.length,
      winRate: scores.length > 0 ? (wonGames.length / scores.length) * 100 : 0,
      averageAttempts: wonGames.length > 0 
        ? wonGames.reduce((sum, score) => sum + score.attempts, 0) / wonGames.length 
        : 0,
      bestScore: wonGames.length > 0 
        ? Math.max(...wonGames.map(score => score.score)) 
        : 0,
      currentStreak,
      maxStreak
    };
  }

  private updateStats(newScore: GameScore): void {
    this.updateStreak(newScore.won);
  }

  private updateStreak(won: boolean): void {
    const streakData = this.getStreakData();
    
    if (won) {
      streakData.current++;
      streakData.max = Math.max(streakData.max, streakData.current);
    } else {
      streakData.current = 0;
    }
    
    localStorage.setItem(this.STREAK_KEY, JSON.stringify(streakData));
  }

  private getStreakData(): { current: number; max: number } {
    const stored = localStorage.getItem(this.STREAK_KEY);
    return stored ? JSON.parse(stored) : { current: 0, max: 0 };
  }

  private getCurrentStreak(): number {
    return this.getStreakData().current;
  }

  private getMaxStreak(): number {
    return this.getStreakData().max;
  }
}

export const scoringSystem = new ScoringSystem();
export const localStorageManager = new LocalStorageManager();