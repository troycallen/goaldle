import json
import random
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from video_manager import VideoManager

@dataclass
class ComparisonResult:
    attribute: str
    guess_value: str
    target_value: str
    status: str  # "exact", "partial", "none"
    hint: str = ""

class GoaldleGame:
    def __init__(self, players_db_path: str = "data/players_db.json"):
        with open(players_db_path, 'r', encoding='utf-8') as f:
            self.players = json.load(f)
        
        # Initialize video manager
        self.video_manager = VideoManager()
        
        # Team to league mapping for partial matches
        self.team_leagues = {
            # Premier League
            "Chelsea": "Premier League",
            "Liverpool": "Premier League", 
            "Tottenham": "Premier League",
            "Manchester City": "Premier League",
            "Manchester United": "Premier League",
            "Arsenal": "Premier League",
            "West Ham": "Premier League",
            "Leicester": "Premier League",
            "Everton": "Premier League",
            "Aston Villa": "Premier League",
            "Crystal Palace": "Premier League",
            "Newcastle": "Premier League",
            "Southampton": "Premier League",
            "Watford": "Premier League",
            "Brighton": "Premier League",
            "Fulham": "Premier League",
            "Brentford": "Premier League",
            "Wolves": "Premier League",
            "Southampton": "Premier League",
            "West Brom": "Premier League",
            "Norwich": "Premier League",
            
            # La Liga
            "Barcelona": "La Liga",
            "Real Madrid": "La Liga",
            "Atletico Madrid": "La Liga",
            
            # Bundesliga
            "Bayern Munich": "Bundesliga",
            "Borussia Dortmund": "Bundesliga",
            "Bayer Leverkusen": "Bundesliga",
            "Eintracht Frankfurt": "Bundesliga",
            
            # Serie A
            "AC Milan": "Serie A",
            "Inter Milan": "Serie A",
            "Juventus": "Serie A",
            "Napoli": "Serie A",
            "AS Roma": "Serie A",
            
            # Ligue 1
            "PSG": "Ligue 1",
            "Lyon": "Ligue 1",
            "Marseille": "Ligue 1",
            "Nice": "Ligue 1",
            "Rennes": "Ligue 1",
            "Saint-Etienne": "Ligue 1",
            "Toulouse": "Ligue 1",
            "Nantes": "Ligue 1",
            
            # Other leagues
            "Inter Miami": "MLS",
            "LAFC": "MLS",
            "Toronto FC": "MLS",
            "Kawasaki Frontale": "J1 League",
            "PSV Eindhoven": "Eredivisie",
            "Real Sociedad": "La Liga",
            "Valencia": "La Liga",
            "Porto": "Primeira Liga",
            "Fenerbahçe": "Süper Lig",
            "Besiktas": "Süper Lig",
            "Plymouth Argyle": "Championship",
            "Vissel Kobe": "J1 League",
            
            # Saudi League
            "Al-Hilal": "Saudi Pro League",
            "Al-Nassr": "Saudi Pro League",
            "Al-Ittihad": "Saudi Pro League",
            "Al-Ahli": "Saudi Pro League",
            "Al-Ettifaq": "Saudi Pro League",
            
            # South American
            "Boca Juniors": "Primera División",
            "São Paulo": "Brasileirão",
            "Millonarios": "Liga BetPlay",
            "Santos": "Brasileirão",
            "Flamengo": "Brasileirão",
            "Palmeiras": "Brasileirão",
            "Corinthians": "Brasileirão",
            "Fluminense": "Brasileirão",
            "Botafogo": "Brasileirão",
            
            # Turkish League
            "Adana Demirspor": "Süper Lig",
            
            # American MLS
            "New York City FC": "MLS", 
            "New York Red Bulls": "MLS",
            "New England Revolution": "MLS",
            "Philadelphia Union": "MLS",
            "Atlanta United": "MLS",
            "Columbus Crew": "MLS",
            "D.C. United": "MLS",
            "Toronto FC": "MLS",
        }
        
        # Country to continent mapping
        self.country_continents = {
            # Europe
            "England": "Europe",
            "Spain": "Europe",
            "France": "Europe",
            "Germany": "Europe",
            "Italy": "Europe",
            "Portugal": "Europe",
            "Netherlands": "Europe",
            "Belgium": "Europe",
            "Croatia": "Europe",
            "Czech Republic": "Europe",
            "Norway": "Europe",
            "Poland": "Europe",
            "Sweden": "Europe",
            "Wales": "Europe",
            "Georgia": "Europe",
            "Serbia": "Europe",
            
            # South America
            "Argentina": "South America",
            "Brazil": "South America",
            "Uruguay": "South America",
            "Colombia": "South America",
            "Chile": "South America",
            "Peru": "South America",
            "Ecuador": "South America",
            "Bolivia": "South America",
            "Paraguay": "South America",
            "Costa Rica": "North America",
            "Honduras": "North America",
            
            # Africa
            "Egypt": "Africa",
            "Ivory Coast": "Africa",
            "Nigeria": "Africa",
            "Algeria": "Africa",
            "Senegal": "Africa",
            "Morocco": "Africa",
            "Tunisia": "Africa",
            "Ghana": "Africa",
            "Cameroon": "Africa",

            # Asia
            "South Korea": "Asia",
            "Japan": "Asia",
            "China": "Asia",
            "Thailand": "Asia",
            "Vietnam": "Asia",
            
            # North America
            "United States": "North America",
            "Mexico": "North America",
            "Canada": "North America"
        }
        
        self.target_player = None
        self.current_goal = None
        self.guesses = []
        self.max_guesses = 6
        
    def start_new_game(self) -> Dict[str, Any]:
        """Start a new game with a random target player and corresponding video"""
        # Get a random goal
        available_goals = self.video_manager.get_all_goals()
        self.current_goal = random.choice(available_goals)
        
        # Find the corresponding player
        target_player_name = self.current_goal["scorer"]
        self.target_player = self.get_player_by_name(target_player_name)
        
        if not self.target_player:
            raise ValueError(f"Player {target_player_name} not found in players database")
        
        self.guesses = []
        
        return {
            "message": "New game started!",
            "max_guesses": self.max_guesses,
            "attributes": ["name", "team", "position", "nationality", "age", "height"],
            "goal_info": {
                "id": self.current_goal["id"],
                "player_name": self.current_goal["scorer"]
            }
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
        elif abs(guess_age - target_age) == 1:
            direction = "higher" if target_age > guess_age else "lower"
            return ComparisonResult("age", str(guess_age), str(target_age), "partial", f"Target is {direction} by 1 year")
        elif abs(guess_age - target_age) <= 3:
            direction = "higher" if target_age > guess_age else "lower"
            diff = abs(guess_age - target_age)
            return ComparisonResult("age", str(guess_age), str(target_age), "partial", f"Target is {direction} by {diff} years")
        elif abs(guess_age - target_age) <= 8:
            direction = "higher" if target_age > guess_age else "lower"
            return ComparisonResult("age", str(guess_age), str(target_age), "none", f"Target is {direction}")
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

        attacking_positions = ["Striker", "Winger"]
        defensive_positions = ["Centre Back", "Wing Back"]
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
    
    def get_current_video(self) -> Optional[Dict[str, Any]]:
        """Get the current goal's blurred video for gameplay"""
        if not self.current_goal:
            return None
        
        return self.video_manager.get_game_video(self.current_goal)
    
    def get_video_reveal(self) -> Optional[Dict[str, Any]]:
        """Get both blurred and original videos for reveal"""
        if not self.current_goal:
            return None
            
        video_pair = self.video_manager.get_video_pair(self.current_goal)
        return {
            "goal_info": {
                "id": self.current_goal["id"],
                "player_name": self.current_goal["scorer"]
            },
            "videos": video_pair
        }