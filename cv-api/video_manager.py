import json
import os
import base64
from typing import Dict, List, Any, Optional
import random

class VideoManager:
    def __init__(self, goals_db_path: str = None, goals_dir: str = None):
        if goals_db_path is None:
            # Try multiple possible paths for robustness
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "data/goals_db.json"),
                os.path.join(os.getcwd(), "data/goals_db.json"),
                "data/goals_db.json"
            ]
            goals_db_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    goals_db_path = path
                    break

            if goals_db_path is None:
                # Create the data directory and raise a more helpful error
                data_dir = os.path.join(os.path.dirname(__file__), "data")
                os.makedirs(data_dir, exist_ok=True)
                raise FileNotFoundError(f"goals_db.json not found. Searched paths: {possible_paths}. Current working directory: {os.getcwd()}")

        if goals_dir is None:
            goals_dir = os.path.join(os.path.dirname(__file__), "goals")

        print(f"VideoManager looking for goals_db at: {goals_db_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"__file__ directory: {os.path.dirname(__file__)}")

        self.goals_db_path = goals_db_path
        self.goals_dir = goals_dir
        self.blurred_dir = os.path.join(os.path.dirname(__file__), "goals/blurred")
        
        # Create blurred directory if it doesn't exist
        os.makedirs(self.blurred_dir, exist_ok=True)
        
        # Load goals database
        with open(goals_db_path, 'r', encoding='utf-8') as f:
            self.goals_db = json.load(f)
    
    def get_random_goal(self) -> Dict[str, Any]:
        """Get a random goal from the database"""
        return random.choice(self.goals_db)
    
    def get_goal_by_player(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get goal by player name"""
        for goal in self.goals_db:
            if goal["scorer"].lower() == player_name.lower():
                return goal
        return None
    
    def get_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get goal by ID"""
        for goal in self.goals_db:
            if goal["id"] == goal_id:
                return goal
        return None
    
    def read_video_as_base64(self, video_path: str) -> str:
        """Read video file and return as base64 string"""
        try:
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
            return base64.b64encode(video_bytes).decode()
        except FileNotFoundError:
            raise FileNotFoundError(f"Video file not found: {video_path}")
    
    def get_blurred_video_path(self, goal: Dict[str, Any]) -> str:
        """Get the path for the blurred version of a video"""
        return goal["blurred_video"].replace("cv-api/", "")
    
    def has_blurred_video(self, goal: Dict[str, Any]) -> bool:
        """Check if blurred version exists"""
        blurred_path = goal["blurred_video"].replace("cv-api/", "")
        return os.path.exists(blurred_path)
    
    def save_blurred_video(self, goal: Dict[str, Any], blurred_video_bytes: bytes) -> str:
        """Save blurred video and update database"""
        blurred_path = self.get_blurred_video_path(goal)
        
        # Save the blurred video file
        with open(blurred_path, 'wb') as f:
            f.write(blurred_video_bytes)
        
        
        return blurred_path
    
    def get_video_pair(self, goal: Dict[str, Any]) -> Dict[str, str]:
        """Get both original and blurred video URLs - used for reveal"""
        result = {
            "goal_id": goal["id"],
            "player_name": goal["scorer"]
        }

        # Get original video URL for reveal
        original_path = goal["original_video"].replace("cv-api/", "")
        if os.path.exists(original_path):
            relative_path = original_path.replace("\\", "/")
            if relative_path.startswith("goals/"):
                relative_path = relative_path[6:]  # Remove "goals/" prefix
            video_url = "/videos/" + relative_path
            result["original_video_url"] = video_url
        else:
            result["original_video_url"] = None
            result["error"] = f"Original video not found: {original_path}"

        # Get blurred video URL
        blurred_path = self.get_blurred_video_path(goal)
        if os.path.exists(blurred_path):
            relative_path = blurred_path.replace("\\", "/")
            if relative_path.startswith("goals/"):
                relative_path = relative_path[6:]  # Remove "goals/" prefix
            video_url = "/videos/" + relative_path
            result["blurred_video_url"] = video_url
        else:
            result["blurred_video_url"] = None

        return result
    
    def get_game_video(self, goal: Dict[str, Any]) -> Dict[str, str]:
        """Get the blurred video URL for gameplay - ALWAYS return blurred video"""
        result = {
            "goal_id": goal["id"],
            "player_name": goal["scorer"]
        }

        # ALWAYS return blurred video for gameplay
        blurred_path = self.get_blurred_video_path(goal)

        # Check if file exists
        if os.path.exists(blurred_path):
            # Return URL path instead of base64
            relative_path = blurred_path.replace("\\", "/")
            if relative_path.startswith("goals/"):
                relative_path = relative_path[6:]  
            video_url = "/videos/" + relative_path
            result["video_url"] = video_url
            result["video_type"] = "url"
        else:
            result["video_url"] = None
            result["error"] = f"Blurred video not found: {blurred_path}"

        return result
    
    def get_all_goals(self) -> List[Dict[str, Any]]:
        """Get all goals in the database"""
        return self.goals_db.copy()
    
