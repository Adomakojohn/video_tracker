import os
import json
import time
from datetime import datetime
import subprocess
import platform


class VideoTracker:
    def __init__(self, video_folder):
        """
        Initialize the video tracker for a specific folder

        :param video_folder: Path to the folder containing video files
        """
        self.video_folder = os.path.abspath(video_folder)
        self.tracking_file = os.path.join(self.video_folder, '.tracker.json')
        self.history = self.load_history()

    def load_history(self):
        """
        Load viewing history from JSON file

        :return: Dictionary of video tracking information
        """
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_history(self):
        """
        Save viewing history to JSON file
        """
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except IOError as e:
            print(f"Error saving tracking file: {e}")

    def track_video(self, video_file, timestamp=None, watched_percentage=0):
        """
        Track a video's viewing progress

        :param video_file: Name of the video file
        :param timestamp: Last watched timestamp (optional)
        :param watched_percentage: Percentage of video watched (optional)
        """
        # Ensure the video file is in the tracked folder
        if not os.path.isabs(video_file):
            video_file = os.path.join(self.video_folder, video_file)

        # Validate file exists
        if not os.path.exists(video_file):
            print(f"File not found: {video_file}")
            return

        # Use current time if no timestamp provided
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Update history
        # self.history[os.path.basename(video_file)] = {
        #     'last_watched': timestamp,
        #     'watched_percentage': watched_percentage,
        #     'full_path': video_file
        # }

        self.history = {
            os.path.basename(video_file): {
                'last_watched': timestamp,
                'watched_percentage': watched_percentage,
                'full_path': video_file
            }
        }

        # Save updated history
        self.save_history()

    def get_last_watched(self, video_file=None):
        """
        Retrieve last watched information

        :param video_file: Optional specific video file to retrieve
        :return: Viewing information or full history
        """
        if video_file:
            # Normalize file name
            video_file = os.path.basename(video_file)
            return self.history.get(video_file)

        return self.history

    def play_video(self, video_file):
        """
        Play a video file using the system's default video player

        :param video_file: Name or path of the video file
        """
        # Ensure full path
        if not os.path.isabs(video_file):
            video_file = os.path.join(self.video_folder, video_file)

        # Detect operating system and use appropriate command
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["open", video_file], check=True)
            elif system == "Windows":
                os.startfile(video_file)
            elif system == "Linux":
                subprocess.run(["xdg-open", video_file], check=True)
            else:
                print(f"Unsupported operating system: {system}")
        except Exception as e:
            print(f"Error playing video: {e}")

        # Track the video after playing
        self.track_video(video_file)

    def list_videos(self):
        """
        List all video files in the tracked folder

        :return: List of video files
        """
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
        return [
            f for f in os.listdir(self.video_folder)
            if os.path.splitext(f)[1].lower() in video_extensions
        ]


def main():
    #ask user for folder path
    video_folder = input('Input your file path eg. ' r'C:\Users\HP\celluloid\Anime\Dan Da Dan: ')

    # Create tracker
    tracker = VideoTracker(video_folder)

    # List available videos
    print("Contents:")
    videos = tracker.list_videos()

    # Sort videos to ensure chronological order
    videos.sort()

    for i, video in enumerate(videos, 1):
        # Check if this video has been watched before
        last_watched = tracker.get_last_watched(video)
        watched_status = " (Previously Watched)" if last_watched else ""
        print(f"{i}. {video}{watched_status}")

    # Prompt user to select a video
    while True:
        try:
            choice = input("\nEnter the number of the episode you want to watch (or 'q' to quit): ")

            if choice.lower() == 'q':
                break

            index = int(choice) - 1
            if 0 <= index < len(videos):
                selected_video = videos[index]
                print(f"\nPlaying: {selected_video}")
                tracker.play_video(selected_video)

                # Retrieve last watched info
                last_watched = tracker.get_last_watched(selected_video)
                print("\nLast Watched Info:")
                print(json.dumps(last_watched, indent=2))
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number or 'q'.")


if __name__ == "__main__":
    main()