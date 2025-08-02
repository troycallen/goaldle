import json
import os
import base64
from typing import Dict, List, Any, Optional
import random

class VideoManager:
    def __init__(self, goals_db_path: str = "data/goals_db.json", goals_dir: str = "goals"):
        self.goals_db_path = goals_db_path
        self.goals_dir = goals_dir
        self.blurred_dir = "goals/blurred"
        
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
        original_filename = os.path.basename(goal["video"])
        name, ext = os.path.splitext(original_filename)
        return os.path.join(self.blurred_dir, f"{name}_blurred{ext}")
    
    def has_blurred_video(self, goal: Dict[str, Any]) -> bool:
        """Check if blurred version exists"""
        blurred_path = self.get_blurred_video_path(goal)
        return os.path.exists(blurred_path)
    
    def save_blurred_video(self, goal: Dict[str, Any], blurred_video_bytes: bytes) -> str:
        """Save blurred video and update database"""
        blurred_path = self.get_blurred_video_path(goal)
        
        # Save the blurred video file
        with open(blurred_path, 'wb') as f:
            f.write(blurred_video_bytes)
        
        # Note: For this simple format, we don't update the database with blurred paths
        # Blurred videos are stored in the blurred/ directory with predictable names
        
        
        return blurred_path
    
    def get_video_pair(self, goal: Dict[str, Any]) -> Dict[str, str]:
        """Get both original and blurred video as base64"""
        result = {
            "goal_id": goal["id"],
            "player_name": goal["scorer"]
        }
        
        # Get original video - fix path format
        video_path = goal["video"].replace("cv-api/", "")  # Remove cv-api prefix
        try:
            result["original_video"] = self.read_video_as_base64(video_path)
        except FileNotFoundError:
            result["original_video"] = None
            result["error"] = f"Original video not found: {video_path}"
        
        # Get blurred video if it exists
        if self.has_blurred_video(goal):
            blurred_path = self.get_blurred_video_path(goal)
            try:
                result["blurred_video"] = self.read_video_as_base64(blurred_path)
            except FileNotFoundError:
                result["blurred_video"] = None
        else:
            result["blurred_video"] = None
        
        return result
    
    def get_all_goals(self) -> List[Dict[str, Any]]:
        """Get all goals in the database"""
        return self.goals_db.copy()
    
