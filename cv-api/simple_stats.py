"""
Simple Personal Stats System for Goaldle
Tracks basic player statistics and game history
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class SimpleStatsManager:
    """Simple stats manager that tracks personal game statistics"""
    
    def __init__(self, stats_file: str = None):
        if stats_file is None:
            stats_file = os.path.join(os.path.dirname(__file__), "data/player_stats.json")
        self.stats_file = stats_file
        os.makedirs(os.path.dirname(stats_file), exist_ok=True)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load stats from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading stats: {e}")
        
        return {
            "total_games": 0,
            "games_won": 0,
            "total_guesses": 0,
            "best_time": None,
            "current_streak": 0,
            "max_streak": 0,
            "guess_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
            "game_history": [],
            "favorite_players": {},
            "daily_stats": {}
        }
    
    def _save_stats(self):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def record_game(self, player_name: str, is_winner: bool, total_guesses: int, time_taken: int = None):
        """Record a completed game"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update basic stats
        self.stats["total_games"] += 1
        self.stats["total_guesses"] += total_guesses
        
        if is_winner:
            self.stats["games_won"] += 1
            self.stats["current_streak"] += 1
            self.stats["max_streak"] = max(self.stats["max_streak"], self.stats["current_streak"])
            
            # Update guess distribution
            if 1 <= total_guesses <= 6:
                self.stats["guess_distribution"][total_guesses] += 1
            
            # Update best time
            if time_taken and (self.stats["best_time"] is None or time_taken < self.stats["best_time"]):
                self.stats["best_time"] = time_taken
        else:
            self.stats["current_streak"] = 0
        
        # Track favorite players (correct answers)
        if player_name not in self.stats["favorite_players"]:
            self.stats["favorite_players"][player_name] = 0
        self.stats["favorite_players"][player_name] += 1
        
        # Add to game history (keep last 20 games)
        game_record = {
            "date": today,
            "player": player_name,
            "won": is_winner,
            "guesses": total_guesses,
            "time": time_taken
        }
        
        self.stats["game_history"].insert(0, game_record)
        if len(self.stats["game_history"]) > 20:
            self.stats["game_history"] = self.stats["game_history"][:20]
        
        # Update daily stats
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {"games": 0, "wins": 0}
        
        self.stats["daily_stats"][today]["games"] += 1
        if is_winner:
            self.stats["daily_stats"][today]["wins"] += 1
        
        self._save_stats()
    
    def get_stats_summary(self) -> Dict:
        """Get formatted stats summary"""
        if self.stats["total_games"] == 0:
            return {
                "total_games": 0,
                "win_rate": 0,
                "current_streak": 0,
                "max_streak": 0,
                "average_guesses": 0,
                "guess_distribution": self.stats["guess_distribution"],
                "message": "Play your first game to see stats!"
            }
        
        win_rate = (self.stats["games_won"] / self.stats["total_games"]) * 100
        avg_guesses = self.stats["total_guesses"] / self.stats["total_games"]
        
        # Get most played players
        sorted_players = sorted(self.stats["favorite_players"].items(), 
                               key=lambda x: x[1], reverse=True)
        top_players = sorted_players[:3]
        
        return {
            "total_games": self.stats["total_games"],
            "games_won": self.stats["games_won"],
            "win_rate": round(win_rate, 1),
            "current_streak": self.stats["current_streak"],
            "max_streak": self.stats["max_streak"],
            "average_guesses": round(avg_guesses, 1),
            "best_time": self.stats["best_time"],
            "guess_distribution": self.stats["guess_distribution"],
            "top_players": top_players,
            "recent_games": self.stats["game_history"][:5]
        }
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed stats including history and trends"""
        summary = self.get_stats_summary()
        
        # Calculate recent performance (last 7 days)
        recent_days = []
        today = datetime.now()
        
        for i in range(7):
            date = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            daily_data = self.stats["daily_stats"].get(date, {"games": 0, "wins": 0})
            recent_days.append({
                "date": date,
                "games": daily_data["games"],
                "wins": daily_data["wins"],
                "win_rate": (daily_data["wins"] / daily_data["games"] * 100) if daily_data["games"] > 0 else 0
            })
        
        return {
            **summary,
            "recent_performance": recent_days,
            "all_game_history": self.stats["game_history"],
            "all_players": dict(sorted(self.stats["favorite_players"].items(), 
                                     key=lambda x: x[1], reverse=True))
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            "total_games": 0,
            "games_won": 0,
            "total_guesses": 0,
            "best_time": None,
            "current_streak": 0,
            "max_streak": 0,
            "guess_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
            "game_history": [],
            "favorite_players": {},
            "daily_stats": {}
        }
        self._save_stats()
    
    def export_stats(self) -> str:
        """Export stats as formatted text"""
        summary = self.get_stats_summary()
        
        if summary["total_games"] == 0:
            return "No games played yet!"
        
        export_text = f"""
🎯 GOALDLE PERSONAL STATS 🎯

📊 OVERVIEW
Games Played: {summary['total_games']}
Games Won: {summary['games_won']}
Win Rate: {summary['win_rate']}%
Current Streak: {summary['current_streak']}
Best Streak: {summary['max_streak']}
Average Guesses: {summary['average_guesses']}

🎲 GUESS DISTRIBUTION
1 guess: {summary['guess_distribution'][1]} games
2 guesses: {summary['guess_distribution'][2]} games  
3 guesses: {summary['guess_distribution'][3]} games
4 guesses: {summary['guess_distribution'][4]} games
5 guesses: {summary['guess_distribution'][5]} games
6 guesses: {summary['guess_distribution'][6]} games

⭐ TOP PLAYERS
"""
        
        for player, count in summary['top_players']:
            export_text += f"{player}: {count} games\n"
        
        return export_text.strip()