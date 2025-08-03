import requests
import json
import os
import base64

def process_video_file(video_path, output_path):
    """Process a single video file through the CV API"""
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return False
    
    print(f"Processing {video_path}...")
    
    try:
        # Read the video file
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        # Create multipart form data
        files = {
            'file': ('video.mp4', video_data, 'video/mp4')
        }
        
        # Send to CV API
        response = requests.post('http://localhost:8001/process-video', files=files, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # Decode and save the blurred video
                blurred_video_data = base64.b64decode(result['blurred_video'])
                
                # Create output directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(blurred_video_data)
                
                print(f"Successfully processed: {output_path}")
                return True
            else:
                print(f"Processing failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"API request failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return False

def main():
    """Process all videos from the goals database"""
    
    # Load goals database
    with open('data/goals_db.json', 'r', encoding='utf-8') as f:
        goals = json.load(f)
    
    processed_goals = []
    
    for goal in goals:
        goal_id = goal['id']
        original_path = goal['video']
        scorer = goal['scorer']
        
        # Fix the path - remove cv-api/ prefix since we're running from cv-api directory
        actual_path = original_path.replace("cv-api/", "")
        
        # Create blurred video path
        original_filename = os.path.basename(actual_path)
        name_without_ext = os.path.splitext(original_filename)[0]
        blurred_path = f"goals/blurred/{name_without_ext}_blurred.mp4"
        
        print(f"\nProcessing Goal {goal_id} - {scorer}")
        
        # Process the video
        success = process_video_file(actual_path, blurred_path)
        
        if success:
            # Update the goal entry
            updated_goal = {
                "id": goal_id,
                "original_video": original_path,
                "blurred_video": f"cv-api/{blurred_path}",
                "scorer": scorer
            }
            processed_goals.append(updated_goal)
        else:
            # Keep original format if processing failed
            processed_goals.append(goal)
    
    # Save updated goals database
    with open('data/goals_db.json', 'w', encoding='utf-8') as f:
        json.dump(processed_goals, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessing complete!")
    print(f"Updated database saved as: data/goals_db.json")
    print(f"Successfully processed {len([g for g in processed_goals if 'blurred_video' in g])} out of {len(goals)} videos")

if __name__ == "__main__":
    main()