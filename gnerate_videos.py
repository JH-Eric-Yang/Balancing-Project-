import os
import subprocess
# from pydub import AudioSegment
import soundfile as sf
# import noisereduce as nr
import numpy as np
# from pydub.effects import high_pass_filter, low_pass_filter
import shutil
from moviepy.editor import VideoFileClip
import pandas as pd
import glob




### distribute amplified audio files to trials
def distribute_audio_files():
    # Root data directory
    data_dir = "Data"
    
    # Walk through all directories in Data
    for root, dirs, files in os.walk(data_dir):
        # Check if current directory is named 'audio_amplified'
        if os.path.basename(root) == 'audio':
            parent_dir = os.path.dirname(root)  # Get the parent directory
            # Process each audio file
            for audio_file in files:
                try:
                    # Extract trial number from filename (4th element after splitting by underscore)
                    parts = audio_file.split('_')
                    if len(parts) >= 4:
                        # Get the trial number from the filename
                        file_trial_num = parts[3].split('.')[0]  # Remove file extension if present
                        
                        # Create trial directory if it doesn't exist (in parent directory)
                        trial_dir = os.path.join(parent_dir, f"Trial_{file_trial_num}")
                        print(f"Creating trial directory: {trial_dir}")
                        os.makedirs(trial_dir, exist_ok=True)
                        
                        # Copy file to trial directory
                        source_path = os.path.join(root, audio_file)
                        dest_path = os.path.join(trial_dir, audio_file)
                        shutil.copy2(source_path, dest_path)  # Using copy2 to preserve metadata
                        print(f"Copied {audio_file} to Trial_{file_trial_num} directory")
                        
                except Exception as e:
                    print(f"Error processing {audio_file}: {str(e)}")

def merge_video_audio(video_path, audio_path, output_path):
    """
    Merge a video file with an audio file using ffmpeg.
    If audio is longer than video, slow down the video to match audio length.
    
    Args:
        video_path (str): Path to the input video file
        audio_path (str): Path to the input audio file
        output_path (str): Path where the merged video will be saved
    """
    try:
        # Check if input files exist
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get video duration
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration
        video_clip.close()
        
        # Get audio duration
        # audio = AudioSegment.from_file(audio_path)
        # audio_duration = len(audio) / 1000.0  # Convert milliseconds to seconds
        
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ]
    

        # if audio_duration > video_duration:
        #     # Calculate the speed factor needed to slow down the video
        #     speed_factor = video_duration / audio_duration
            
        #     # FFmpeg command to merge video and audio with adjusted video speed
        #     command = [
        #         "ffmpeg", "-y",
        #         "-i", video_path,
        #         "-i", audio_path,
        #         "-filter_complex", f"[0:v]setpts={1/speed_factor}*PTS[v]",
        #         "-map", "[v]",
        #         "-map", "1:a",
        #         "-c:v", "libx264",
        #         "-c:a", "aac",
        #         "-strict", "experimental",
        #         output_path
        #     ]
        # else:
        #     # If video is longer or equal, use normal merge
        #     command = [
        #         "ffmpeg", "-y",
        #         "-i", video_path,
        #         "-i", audio_path,
        #         "-c:v", "copy",
        #         "-c:a", "aac",
        #         "-strict", "experimental",
        #         output_path
        #     ]
        
        # Execute the command
        subprocess.run(command, check=True, capture_output=True)
        print(f"Successfully merged video and audio to: {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error merging video and audio: {str(e)}")
        raise

def merge_videos_grid(video_paths, output_path):
    """
    Merge 6 videos into a 2x3 grid layout (2 columns, 3 rows).
    The first column contains clue_giver videos, second column contains guesser videos.
    
    Args:
        video_paths (list): List of 6 video file paths (3 clue_giver + 3 guesser)
        output_path (str): Path where the merged video will be saved
    """
    print("Merging videos into grid layout")
    try:
        # Check if we have exactly 6 videos
        if len(video_paths) != 6:
            raise ValueError("Exactly 6 video paths must be provided")

        # Check if all input files exist
        for path in video_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video file not found: {path}")

        # FFmpeg filter complex command to create 2x3 grid
        filter_complex = (
            # Scale all videos to 640x360 (adjust these dimensions as needed)
            "[0:v]scale=640:360[v0];"
            "[1:v]scale=640:360[v1];"
            "[2:v]scale=640:360[v2];"
            "[3:v]scale=640:360[v3];"
            "[4:v]scale=640:360[v4];"
            "[5:v]scale=640:360[v5];"
            # Stack first column (videos 0,2,4)
            "[v0][v1][v2]vstack=inputs=3[col1];"
            # Stack second column (videos 1,3,5)
            "[v3][v4][v5]vstack=inputs=3[col2];"
            # Combine columns side by side
            "[col1][col2]hstack=inputs=2[v]"
        )

        # Construct FFmpeg command
        command = ["ffmpeg", "-y"]
        
        # Add input files
        for video_path in video_paths:
            command.extend(["-i", video_path])
        
        # Add filter complex and output options
        command.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",  # Map the video output
            "-c:v", "libx264",  # Use H.264 codec
            "-preset", "medium",  # Encoding preset
            "-crf", "23",  # Quality setting
            output_path
        ])

        # Execute the command
        subprocess.run(command, check=True, capture_output=True)
        print(f"Successfully merged videos into grid layout: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error merging videos: {str(e)}")
        raise


def merge_videos_grid_8(video_paths, output_path):
    """
    Merge 8 videos into a 2x4 grid layout (2 rows, 4 columns).
    First row contains clue_giver videos + plot, second row contains guesser videos + plot.
    
    Args:
        video_paths (list): List of 8 video file paths (3 clue_giver + 1 plot + 3 guesser + 1 plot)
        output_path (str): Path where the merged video will be saved
    """
    print("Merging videos into 2x4 grid layout")
    try:
        # Check if we have exactly 8 videos
        if len(video_paths) != 8:
            raise ValueError("Exactly 8 video paths must be provided")

        # Check if all input files exist
        for path in video_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video file not found: {path}")

        # FFmpeg filter complex command to create 2x4 grid
        filter_complex = (
            # Scale all videos to 640x360
            "[0:v]scale=640:360[v0];"
            "[1:v]scale=640:360[v1];"
            "[2:v]scale=640:360[v2];"
            "[3:v]scale=640:360[v3];"
            "[4:v]scale=640:360[v4];"
            "[5:v]scale=640:360[v5];"
            "[6:v]scale=640:360[v6];"
            "[7:v]scale=640:360[v7];"
            # Stack first row (videos 0,1,2,3)
            "[v0][v1][v2][v3]hstack=inputs=4[row1];"
            # Stack second row (videos 4,5,6,7)
            "[v4][v5][v6][v7]hstack=inputs=4[row2];"
            # Combine rows vertically
            "[row1][row2]vstack=inputs=2[v]"
        )

        # Rest of the function remains the same
        command = ["ffmpeg", "-y"]
        for video_path in video_paths:
            command.extend(["-i", video_path])
        
        command.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            output_path
        ])

        subprocess.run(command, check=True, capture_output=True)
        print(f"Successfully merged videos into grid layout: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error merging videos: {str(e)}")
        raise



def run_merge_videos_grid(input_path):
    """
    Process all trial directories in the input path to merge videos in a 2x3 grid.
    Looks for clue_giver and guesser directories containing exactly 3 videos each.
    
    Args:
        input_path (str): Root directory containing trial folders
    """
    for root, dirs, files in os.walk(input_path):
        # Get the current directory name
        current_dir = os.path.basename(root)
        
        # Only process if directory starts with "Trial"
        if current_dir.startswith("Trial"):
            # Check for clue_giver and guesser directories
            clue_giver_dir = os.path.join(root, "clue_giver","videos")
            guesser_dir = os.path.join(root, "guesser","videos")
            check_every_thing = True
            # Check if both directories exist
            if not (os.path.exists(clue_giver_dir) and os.path.exists(guesser_dir)):
                print(f"Missing required directories in {current_dir}")
                check_every_thing = False
                continue
            
            # Get video files from each directory
            clue_giver_videos = [f for f in os.listdir(clue_giver_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            guesser_videos = [f for f in os.listdir(guesser_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            
            # Check if each directory has exactly 3 videos
            if len(clue_giver_videos) != 3:
                print(f"Error: {current_dir}/clue_giver has {len(clue_giver_videos)} videos (expected 3)")
                check_every_thing = False
                continue
                
            if len(guesser_videos) != 3:
                print(f"Error: {current_dir}/guesser has {len(guesser_videos)} videos (expected 3)")
                check_every_thing = False
                continue
                
            print(f"Found correct number of videos in {current_dir}")
            
            # Create video_paths list with full paths
            video_paths = []
            
            # Add clue_giver videos (first column)
            for video in sorted(clue_giver_videos):
                video_paths.append(os.path.join(clue_giver_dir, video))
                
            # Add guesser videos (second column)
            for video in sorted(guesser_videos):
                video_paths.append(os.path.join(guesser_dir, video))
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(root, "merged")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create output path for merged video
            output_path = os.path.join(output_dir, f"{current_dir}_merged.mp4")
            
            if check_every_thing:
                try:
                    # Merge videos into grid
                    merge_videos_grid(video_paths, output_path)
                    print(f"Successfully created merged video for {current_dir}")
                except Exception as e:
                    print(f"Error merging videos for {current_dir}: {str(e)}")

def run_merge_videos_grid_8(input_path):
    """
    Process all trial directories in the input path to merge videos in a 2x4 grid.
    Includes plot videos along with clue_giver and guesser videos.
    
    Args:
        input_path (str): Root directory containing trial folders
    """
    for root, dirs, files in os.walk(input_path):
        # Get the current directory name
        current_dir = os.path.basename(root)
        
        # Only process if directory starts with "Trial"
        if current_dir.startswith("Trial"):
            # Check for clue_giver and guesser directories
            clue_giver_dir = os.path.join(root, "clue_giver","videos")
            plot_clue_giver = os.path.join(root,"clue_giver","plot.mp4")
            guesser_dir = os.path.join(root, "guesser","videos")
            plot_guesser = os.path.join(root,"guesser","plot.mp4")
            check_every_thing = True
            # Check if both directories exist
            if not (os.path.exists(clue_giver_dir) and os.path.exists(guesser_dir)):
                print(f"Missing required directories in {current_dir}")
                check_every_thing = False
                continue
            
            # Get video files from each directory
            clue_giver_videos = [f for f in os.listdir(clue_giver_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            guesser_videos = [f for f in os.listdir(guesser_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            
            # Check if each directory has exactly 3 videos
            if len(clue_giver_videos) != 3:
                print(f"Error: {current_dir}/clue_giver has {len(clue_giver_videos)} videos (expected 3)")
                check_every_thing = False
                continue
                
            if len(guesser_videos) != 3:
                print(f"Error: {current_dir}/guesser has {len(guesser_videos)} videos (expected 3)")
                check_every_thing = False
                continue
                
            print(f"Found correct number of videos in {current_dir}")
            
            # Create video_paths list with full paths
            video_paths = []
            
            # Add clue_giver videos (first column)
            for video in sorted(clue_giver_videos):
                video_paths.append(os.path.join(clue_giver_dir, video))

            video_paths.append(plot_clue_giver)
            
                
            # Add guesser videos (second column)
            for video in sorted(guesser_videos):
                video_paths.append(os.path.join(guesser_dir, video))
            
            video_paths.append(plot_guesser)
            # Create output directory if it doesn't exist
            output_dir = os.path.join(root, "merged")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create output path for merged video
            output_path = os.path.join(output_dir, f"{current_dir}_merged.mp4")
            
            if check_every_thing:
                try:
                    # Merge videos into grid
                    merge_videos_grid_8(video_paths, output_path)
                    print(f"Successfully created merged video for {current_dir}")
                except Exception as e:
                    print(f"Error merging videos for {current_dir}: {str(e)}")



def run_merge_audio_video(input_path):
    """
    Merge audio files with their corresponding merged video files for each trial.
    Looks for audio files in trial directory and merged videos in the merged subdirectory.
    
    Args:
        input_path (str): Root directory containing trial folders
    """
    for root, dirs, files in os.walk(input_path):
        # Get the current directory name
        current_dir = os.path.basename(root)
        
        # Only process if directory starts with "Trial"
        if current_dir.startswith("Trial"):
            try:
                # Find audio and video files
                audio_files = [f for f in os.listdir(root) if f.endswith(('.wav', '.mp3', '.m4a'))]
                if not audio_files:
                    print(f"No audio files found in {current_dir}")
                    continue
                first_audio_file = audio_files[0]
                audio_path = os.path.join(root, first_audio_file)
                
                # Check merged directory for video files
                merged_dir = os.path.join(root, "merged")
                if not os.path.exists(merged_dir):
                    print(f"Merged directory not found in {current_dir}")
                    continue
                
                video_files = [f for f in os.listdir(merged_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
                if not video_files:
                    print(f"No video files found in {current_dir}/merged")
                    continue
                first_video_file = video_files[0]
                video_path = os.path.join(merged_dir, first_video_file)
                
                # Create output directory for final videos if it doesn't exist
                final_dir = os.path.join(root)
                
                # Create output path for the merged video with audio
                output_path = os.path.join(final_dir, f"{current_dir}_final.mp4")
                
                # Remove existing file if it exists
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                        print(f"Removed existing file: {output_path}")
                    except Exception as e:
                        print(f"Error removing existing file {output_path}: {str(e)}")
                # Merge video and audi
                merge_video_audio(video_path, audio_path, output_path)
                print(f"Successfully merged audio and video for {current_dir}")
                
            except Exception as e:
                print(f"Error processing {current_dir}: {str(e)}")


def add_target_word_into_final_video(input_path):
    """
    Read target words from Excel file and rename final videos to include target words.
    Updates Excel file with trial numbers if needed.
    
    Args:
        input_path (str): Root directory containing trial folders and stimuli Excel file
    """
    # Define trial numbers used in the experiment
    trial_Number = [12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,
                   34,35,36,37,38,39,40,41,42,43,45,46,47,48,49,50,51,52,53,54]
    for root, dirs, files in os.walk(input_path):
        # Get the current directory name
        current_dir = os.path.basename(root)
        
        # Find excel files in the current directory
        excel_files = glob.glob(os.path.join(root, '*_stimuli*.xlsx'))
        if not excel_files:
            continue
            
        # Read the excel file
        df = pd.read_excel(excel_files[0])
        
        # Add trial_Number column if it doesn't exist
        if 'trial_Number' not in df.columns:
            # Create a mapping dictionary from index position to trial number
            trial_mapping = {i+1: num for i, num in enumerate(trial_Number)}
            # Map the trial numbers using their position
            df['trial_Number'] = df.index.map(lambda x: trial_mapping.get(x+1, 0))
            
            # Save the updated Excel file
            df.to_excel(excel_files[0], index=False)
            print(f"Updated Excel file with trial_Number column: {excel_files[0]}")
        
        # Iterate through each row in the dataframe
        for index, row in df.iterrows():
            try:
                trial_number = str(row['trial_Number'])
                target_word = str(row['target_word'])
                
                # Construct trial directory path
                trial_dir = os.path.join(root, f"Trial_{trial_number}")
                
                if not os.path.exists(trial_dir):
                    print(f"Trial directory not found: {trial_dir}")
                    continue
                
                # Find final video file
                final_videos = [f for f in os.listdir(trial_dir) if '_final' in f and f.endswith(('.mp4', '.avi', '.mov'))]
                
                if not final_videos:
                    print(f"No final video found in {trial_dir}")
                    continue
                
                for video in final_videos:
                    # Construct new filename with target word
                    old_path = os.path.join(trial_dir, video)
                    new_filename = f"{os.path.splitext(video)[0]}_{target_word}{os.path.splitext(video)[1]}"
                    new_path = os.path.join(trial_dir, new_filename)
                    
                    # Rename the file
                    os.rename(old_path, new_path)
                    print(f"Renamed {video} to {new_filename}")
                    
            except Exception as e:
                print(f"Error processing trial {trial_number}: {str(e)}")


def merge_video_and_names(input_path, type="normal"):
    """
    Main processing function that coordinates the video merging workflow.
    
    Args:
        input_path (str): Root directory containing trial folders
        type (str): Processing type - "normal" for 2x3 grid, "estimation" for 2x4 grid with plots
    """
    processing_folder_path = input_path
    if (type == "estimation"):
        run_merge_videos_grid_8(processing_folder_path)
    else:
        run_merge_videos_grid(processing_folder_path)
    run_merge_audio_video(processing_folder_path)
    add_target_word_into_final_video(processing_folder_path)
    

if __name__ == "__main__":
    # Use current directory as base directory
    base_directory = os.getcwd()
    
    # Get all subdirectories in the base directory, excluding 'pb103_pb104'
    subdirs = [d for d in os.listdir(base_directory) 
              if os.path.isdir(os.path.join(base_directory, d)) 
              and d != 'pb103_pb104']
    
    # Process each subdirectory
    for subdir in subdirs:
        input_directory = os.path.join(base_directory, subdir)
        print(f"\nProcessing folder: {subdir}")
        # Use "estimation" type to include plot videos in the merged output
        merge_video_and_names(input_directory, type="estimation")
    