import json
import random
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class ComparisonResult:
    attribute: str
    guess_value: str
    target_value: str
    status: str  # "exact", "partial", "none"
    hint: str = ""

class GoaldleGame:
    def __init__(self, players_db_path: str = "data/players_database.json"):
        with open(players_db_path, 'r', encoding='utf-8') as f:
            self.players = json.load(f)
        
        # Team to league mapping for partial matches
        self.team_leagues = {
            "Chelsea": "Premier League",
            "Liverpool": "Premier League", 
            "Tottenham": "Premier League",
            "Barcelona": "La Liga",
            "Inter Miami": "MLS",
            "Hamburger SV": "2. Bundesliga"
        }
        
        # Country to continent mapping
        self.country_continents = {
            "Argentina": "South America",
            "Egypt": "Africa",
            "South Korea": "Asia",
            "Japan": "Asia", 
            "Spain": "Europe",
            "Ivory Coast": "Africa"
        }
        
        self.target_player = None
        self.guesses = []
        self.max_guesses = 6
        
    def start_new_game(self) -> Dict[str, Any]:
        """Start a new game with a random target player"""
        self.target_player = random.choice(self.players)
        self.guesses = []
        return {
            "message": "New game started!",
            "max_guesses": self.max_guesses,
            "attributes": ["name", "team", "position", "nationality", "age", "height"]
        }
    
    def get_player_by_name(self, name: str) -> Dict[str, Any]:
        """Find player by name (case-insensitive)"""
        for player in self.players:
            if player["name"].lower() == name.lower():
                return player
        return None
    
    def compare_age(self, guess_age: int, target_age: int) -> ComparisonResult:
        """Compare ages with directional hints"""
        if guess_age == target_age:
            return ComparisonResult("age", str(guess_age), str(target_age), "exact")
        elif abs(guess_age - target_age) <= 3:
            direction = "higher" if target_age > guess_age else "lower"
            return ComparisonResult("age", str(guess_age), str(target_age), "partial", f"Target is {direction}")
        else:
            direction = "much higher" if target_age > guess_age else "much lower"
            return ComparisonResult("age", str(guess_age), str(target_age), "none", f"Target is {direction}")
    
    def compare_height(self, guess_height: str, target_height: str) -> ComparisonResult:
        """Compare heights with directional hints"""
        guess_cm = int(guess_height.replace("cm", ""))
        target_cm = int(target_height.replace("cm", ""))
        
        if guess_cm == target_cm:
            return ComparisonResult("height", guess_height, target_height, "exact")
        elif abs(guess_cm - target_cm) <= 5:
            direction = "taller" if target_cm > guess_cm else "shorter"
            return ComparisonResult("height", guess_height, target_height, "partial", f"Target is {direction}")
        else:
            direction = "much taller" if target_cm > guess_cm else "much shorter"
            return ComparisonResult("height", guess_height, target_height, "none", f"Target is {direction}")
    
    def compare_team(self, guess_team: str, target_team: str) -> ComparisonResult:
        """Compare teams with league hints"""
        if guess_team == target_team:
            return ComparisonResult("team", guess_team, target_team, "exact")
        
        guess_league = self.team_leagues.get(guess_team, "Unknown")
        target_league = self.team_leagues.get(target_team, "Unknown")
        
        if guess_league == target_league and guess_league != "Unknown":
            return ComparisonResult("team", guess_team, target_team, "partial", f"Same league ({target_league})")
        else:
            return ComparisonResult("team", guess_team, target_team, "none")
    
    def compare_nationality(self, guess_country: str, target_country: str) -> ComparisonResult:
        """Compare nationalities with continent hints"""
        if guess_country == target_country:
            return ComparisonResult("nationality", guess_country, target_country, "exact")
        
        guess_continent = self.country_continents.get(guess_country, "Unknown")
        target_continent = self.country_continents.get(target_country, "Unknown")
        
        if guess_continent == target_continent and guess_continent != "Unknown":
            return ComparisonResult("nationality", guess_country, target_country, "partial", f"Same continent ({target_continent})")
        else:
            return ComparisonResult("nationality", guess_country, target_country, "none")
    
    def compare_position(self, guess_pos: str, target_pos: str) -> ComparisonResult:
        """Compare positions with attacking/defensive hints"""
        if guess_pos == target_pos:
            return ComparisonResult("position", guess_pos, target_pos, "exact")
        
        attacking_positions = ["Forward", "Striker"]
        defensive_positions = ["Defender", "Goalkeeper"]
        midfield_positions = ["Midfielder"]
        
        guess_type = "attacking" if guess_pos in attacking_positions else \
                    "defensive" if guess_pos in defensive_positions else "midfield"
        target_type = "attacking" if target_pos in attacking_positions else \
                     "defensive" if target_pos in defensive_positions else "midfield"
        
        if guess_type == target_type:
            return ComparisonResult("position", guess_pos, target_pos, "partial", f"Same type ({target_type})")
        else:
            return ComparisonResult("position", guess_pos, target_pos, "none")
    
    def make_guess(self, player_name: str) -> Dict[str, Any]:
        """Process a player guess and return comparison results"""
        if len(self.guesses) >= self.max_guesses:
            return {"error": "Maximum guesses reached"}
        
        if not self.target_player:
            return {"error": "No active game. Start a new game first."}
        
        guessed_player = self.get_player_by_name(player_name)
        if not guessed_player:
            return {"error": f"Player '{player_name}' not found in database"}
        
        # Check if already guessed
        if any(guess["player"]["name"] == guessed_player["name"] for guess in self.guesses):
            return {"error": "Player already guessed"}
        
        # Compare all attributes
        comparisons = []
        
        # Name comparison
        if guessed_player["name"] == self.target_player["name"]:
            comparisons.append(ComparisonResult("name", guessed_player["name"], self.target_player["name"], "exact"))
        else:
            comparisons.append(ComparisonResult("name", guessed_player["name"], self.target_player["name"], "none"))
        
        # Other attributes
        comparisons.append(self.compare_team(guessed_player["team"], self.target_player["team"]))
        comparisons.append(self.compare_position(guessed_player["position"], self.target_player["position"]))
        comparisons.append(self.compare_nationality(guessed_player["nationality"], self.target_player["nationality"]))
        comparisons.append(self.compare_age(guessed_player["age"], self.target_player["age"]))
        comparisons.append(self.compare_height(guessed_player["height"], self.target_player["height"]))
        
        # Create guess result
        guess_result = {
            "player": guessed_player,
            "comparisons": [
                {
                    "attribute": comp.attribute,
                    "guess_value": comp.guess_value,
                    "target_value": comp.target_value,
                    "status": comp.status,
                    "hint": comp.hint
                } for comp in comparisons
            ],
            "guess_number": len(self.guesses) + 1
        }
        
        self.guesses.append(guess_result)
        
        # Check if won
        is_winner = guessed_player["name"] == self.target_player["name"]
        game_over = is_winner or len(self.guesses) >= self.max_guesses
        
        result = {
            "guess_result": guess_result,
            "is_winner": is_winner,
            "game_over": game_over,
            "guesses_remaining": self.max_guesses - len(self.guesses),
            "total_guesses": len(self.guesses)
        }
        
        if game_over and not is_winner:
            result["target_player"] = self.target_player
        
        return result
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return {
            "has_active_game": self.target_player is not None,
            "guesses": self.guesses,
            "guesses_remaining": self.max_guesses - len(self.guesses) if self.target_player else 0,
            "game_over": len(self.guesses) >= self.max_guesses if self.target_player else False,
            "target_revealed": len(self.guesses) >= self.max_guesses and self.target_player,
            "target_player": self.target_player if len(self.guesses) >= self.max_guesses else None
        }
    
    def get_available_players(self) -> List[str]:
        """Get list of all player names for autocomplete"""
        return [player["name"] for player in self.players]