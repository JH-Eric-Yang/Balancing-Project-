import os
import shutil
import subprocess
from Pose2Sim import Pose2Sim
from trc import TRCData
import pandas as pd
# import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation


def organize_files_by_trial(current_dir="Data"):
    # Make sure the directory exists
    if not os.path.exists(current_dir):
        print(f"Error: {current_dir} directory not found")
        return

    # Get all items in the current directory
    items = os.listdir(current_dir)
    
    # Create audio and video directories only if this is not the root Data directory
    if current_dir != "Data":
        audio_dir = os.path.join(current_dir, "audio")
        video_dir = os.path.join(current_dir, "video")
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
    
    # First, process all files in current directory
    for item in items:
        full_path = os.path.join(current_dir, item)
        
        # Skip if it's a directory
        if os.path.isdir(full_path):
            continue
            
        # Get trial number from filename
        try:
            trial_num = item.split('_')[-4]
            # Create trial directory if it doesn't exist
            trial_dir = os.path.join(current_dir, f"Trial_{trial_num}")
            if not os.path.exists(trial_dir):
                os.makedirs(trial_dir)
            
            # Copy file to appropriate trial directory
            source = full_path
            destination = os.path.join(trial_dir, item)
            shutil.copy2(source, destination)  # Keep original in trial directory
            print(f"Copied {item} to {trial_dir}")
            
            # Copy file to appropriate media directory if not in root Data directory
            if current_dir != "Data":
                if item.lower().endswith(('.wav', '.mp3', '.aac')):
                    media_dest = os.path.join(audio_dir, item)
                    shutil.move(source, media_dest)
                    print(f"Copied {item} to {audio_dir}")
                elif item.lower().endswith(('.mp4', '.avi', '.mov')):
                    media_dest = os.path.join(video_dir, item)
                    shutil.move(source, media_dest)
                    print(f"Copied {item} to {video_dir}")
            
        except IndexError:
            print(f"Skipping {item}: Could not extract trial number")

    # Then recursively process all subdirectories
    for item in items:
        full_path = os.path.join(current_dir, item)
        if os.path.isdir(full_path) and not item.startswith(("Trial_", "audio", "video")):
            organize_files_by_trial(full_path)  # Recursively process subdirectories

def tidy_video_files():
    data_dir = "data"
    # Iterate through folders in data directory
    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        print(f"Processing folder: {folder}")
        for item in os.listdir(folder_path):
            print(f"Processing item: {item}")
            item_path = os.path.join(folder_path, item)
            if item.startswith("Trial_") and os.path.isdir(item_path):
                print(f"Processing Trail folder: {item}")
                video_files = [f for f in os.listdir(item_path) if f.endswith(('.mp4', '.avi', '.mov'))]  # Add more video extensions if needed
                
                if len(video_files) == 6:
                    # Create subfolders including video folders
                    print(f"Creating subfolders")
                    p1_folder = os.path.join(item_path, "clue_giver")
                    p2_folder = os.path.join(item_path, "guesser")
                    p1_video_folder = os.path.join(p1_folder, "videos")
                    p2_video_folder = os.path.join(p2_folder, "videos")
                    os.makedirs(p1_video_folder, exist_ok=True)
                    os.makedirs(p2_video_folder, exist_ok=True)
                    
                    # Move files to appropriate video folders
                    for video in video_files:
                        source = os.path.join(item_path, video)
                        if any(cam in video.lower() for cam in ["cam0", "cam1", "cam2"]):
                            destination = os.path.join(p1_video_folder, video)
                        else:
                            destination = os.path.join(p2_video_folder, video)
                        shutil.move(source, destination)
                    
                    print(f"Organized videos in {item}")


## this is an optional function to swap the name of the video file

def swap_video_file_name():
    data_dir = "data"
    # Iterate through folders in data directory
    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        print(f"Processing folder: {folder}")
        for item in os.listdir(folder_path):
            print(f"Processing item: {item}")
            item_path = os.path.join(folder_path, item)
            if item.startswith("Trial_") and os.path.isdir(item_path):
                # Check if guesser folder exists
                guesser_path = os.path.join(item_path, "guesser")
               
                if os.path.exists(guesser_path):
                    print(f"Processing guesser folder in {item}")
                    video_path = os.path.join(guesser_path, "videos")
                    if os.path.exists(video_path):
                        for video in os.listdir(video_path):
                            if video.endswith(('.mp4', '.avi', '.mov')):
                                old_path = os.path.join(video_path, video)
                                
                                # Get file extension
                                file_extension = os.path.splitext(video)[1]
                                # Get the prefix part of the filename (before cam)
                                prefix = video.split('cam')[0]
                                # Get the suffix part of the filename (after cam number)
                                suffix = video.split(')')[1] if ')' in video else file_extension
                                
                                # Replace camera numbers while keeping the format
                                if "cam3" in video.lower():
                                    new_name = f"cam01.avi"
                                elif "cam4" in video.lower():
                                    new_name = f"cam02.avi"
                                elif "cam5" in video.lower():
                                    new_name = f"cam03.avi"
                                else:
                                    continue
                                
                                new_path = os.path.join(video_path, new_name)
                                print(f"Renaming {video} to {new_name}")
                                if old_path != new_path:
                                    os.rename(old_path, new_path)
                                    print(f"Renamed {video} to {new_name}")
                
                
                clue_giver_path = os.path.join(item_path, "clue_giver")
               
                if os.path.exists(clue_giver_path):
                    print(f"Processing clue_giver folder in {item}")
                    video_path = os.path.join(clue_giver_path, "videos")
                    if os.path.exists(video_path):
                        for video in os.listdir(video_path):
                            if video.endswith(('.mp4', '.avi', '.mov')):
                                old_path = os.path.join(video_path, video)
                                
                                # Get file extension
                                file_extension = os.path.splitext(video)[1]
                                # Get the prefix part of the filename (before cam)
                                prefix = video.split('cam')[0]
                                # Get the suffix part of the filename (after cam number)
                                suffix = video.split(')')[1] if ')' in video else file_extension
                                
                                # Replace camera numbers while keeping the format
                                if "cam0" in video.lower():
                                    new_name = f"cam01.avi"
                                elif "cam1" in video.lower():
                                    new_name = f"cam02.avi"
                                elif "cam2" in video.lower():
                                    new_name = f"cam03.avi"
                                else:
                                    continue
                                
                                new_path = os.path.join(video_path, new_name)
                                print(f"Renaming {video} to {new_name}")
                                if old_path != new_path:
                                    os.rename(old_path, new_path)
                                    print(f"Renamed {video} to {new_name}")


def run_pose2sim():
    data_dir = "data"
    guesser_material_dir = "pose2sim_material/Guesser"
    clue_giver_material_dir = "pose2sim_material/Clue_giver"
    
    # Create list to store errors
    errors = []
     
    # Run test.py in guesser folder
    test_script = "test.py"
    env_python = 'C:/Users/Test/.conda/envs/Pose2Sim/python'
    # Iterate through folders in data directory
    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        print(f"Processing folder: {folder}")
        for item in os.listdir(folder_path):
            print(f"Processing item: {item}")
            item_path = os.path.join(folder_path, item)
            if item.startswith("Trial_") and os.path.isdir(item_path):
                clue_giver_path = os.path.join(item_path, "clue_giver")
                if os.path.exists(clue_giver_path):
                    print(f"Processing clue_giver folder in {item}")
                    # Copy entire directory tree from pose2sim_material/Clue_giver to clue_giver_path
                    for root, dirs, files in os.walk(clue_giver_material_dir):
                        # Get the relative path from material_dir
                        relative_path = os.path.relpath(root, clue_giver_material_dir)
                        # Create corresponding directory in destination
                        dest_dir = os.path.join(clue_giver_path, relative_path)
                        os.makedirs(dest_dir, exist_ok=True)

                        # Copy all files in current directory
                        for file in files:
                            source = os.path.join(root, file)
                            destination = os.path.join(dest_dir, file)
                            shutil.copy2(source, destination)
                            # print(f"Copied {file} to {dest_dir}")
                    
                    # Run test.py in clue_giver folder
                    try:
                        subprocess.run([env_python, test_script], 
                                    check=True,
                                    cwd=clue_giver_path)
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Error in {item} (clue_giver): {str(e)}"
                        print(error_msg)
                        errors.append({
                            'trial': item,
                            'role': 'clue_giver',
                            'error': str(e)
                        })
                        continue

                    # after running pose2sim, create trc video
                    trc_video_path = os.path.join(clue_giver_path, 'pose-3d')
                    if os.path.exists(trc_video_path):
                        trc_files = [f for f in os.listdir(trc_video_path) 
                                   if f.endswith('.trc') 
                                   and not any(suffix in f for suffix in ['LSTM', 'butterworth'])]
                        
                        for trc_file in trc_files:
                            trc_file_path = os.path.join(trc_video_path, trc_file)
                            # Create output CSV filename
                            csv_filename = os.path.splitext(trc_file)[0] + '.csv'
                            csv_output_path = os.path.join(clue_giver_path, csv_filename)
                            
                            # Convert TRC to CSV
                            trc_to_csv(trc_file_path, csv_output_path)
                            print(f"Converted {trc_file} to CSV")

                            # Plot the TRC file
                            trc_plot(csv_output_path, os.path.join(clue_giver_path, 'plot.mp4'), 'clue')
                            print(f"Plotted {trc_file}")

                    



                # Check if guesser folder exists
                guesser_path = os.path.join(item_path, "guesser")
               
                if os.path.exists(guesser_path):
                    print(f"Processing guesser folder in {item}")
                    # Copy entire directory tree from pose2sim_material/Guesser to guesser_path
                    
                    for root, dirs, files in os.walk(guesser_material_dir):
                        # Get the relative path from material_dir
                        relative_path = os.path.relpath(root, guesser_material_dir)
                        # Create corresponding directory in destination
                        dest_dir = os.path.join(guesser_path, relative_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        
                        # Copy all files in current directory
                        for file in files:
                            source = os.path.join(root, file)
                            destination = os.path.join(dest_dir, file)
                            shutil.copy2(source, destination)
                            # print(f"Copied {file} to {dest_dir}")
                   

                    try:
                        # Set working directory to guesser_path when running the script
                        subprocess.run([env_python, test_script], 
                                    check=True,
                                    cwd=guesser_path)
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Error in {item} (guesser): {str(e)}"
                        print(error_msg)
                        errors.append({
                            'trial': item,
                            'role': 'guesser',
                            'error': str(e)
                        })
                        continue

    # Save errors to CSV if any occurred
    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv('errors.csv', index=False)
        print("Errors have been saved to errors.csv")


def trc_to_csv(file_path,output_path):
    mocap_data = TRCData()
    mocap_data.load(file_path)

    num_frames = mocap_data['NumFrames']
    markernames = mocap_data['Markers'] # the marker names are not

    # convert movap_data to pandas dataframe
    mocap_data_df = pd.DataFrame(mocap_data, columns=mocap_data['Markers'])
    # each value within the dataframe consists a list of x,y,z coordinates, we want to seperate these out so that each marker and dimension has its own column
    # first we create a list of column names
    colnames = []
    for marker in markernames:
        colnames.append(marker + '_x') 
        colnames.append(marker + '_y')
        colnames.append(marker + '_z')

    # Create a new DataFrame to store separated values
    new_df = pd.DataFrame()

    # Iterate through each column in the original DataFrame
    for column in mocap_data_df.columns:
        # Extract the x, y, z values from each cell
        xyz = mocap_data_df[column].tolist()
        # Create a new DataFrame with the values in the cell separated into their own columns
        xyz_df = pd.DataFrame(xyz, columns=[column + '_x', column + '_y', column + '_z']) 
        # Add the new columns to the new DataFrame
        new_df = pd.concat([new_df, xyz_df], axis=1)

    # add a new time column to the new dataframe assuming the framerate was 60fps
    time = []
    ts = 0
    for i in range(0, int(num_frames)):
        ts = ts + 1/30
        time.append(ts)

    # add the time column to the new dataframe
    new_df['Time'] = time

    #write pd dataframe to csv
    new_df.to_csv(output_path, index=False)


def trc_plot(file_path,output_path,type):
    MT_tracking = pd.read_csv(file_path)

    # Create a figure and axis
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d', computed_zorder=False)

    # Define the number of frames
    num_frames = len(MT_tracking)

    # Define the scatter plot
    scatter = ax.scatter([], [], [], marker='o')

    # Update function for animation
    def update_clue(frame):
        ax.clear()
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        ax.set_title('3D Animation')
        
        # Set the viewing angle
        ax.view_init(elev=2, azim=89)
            # Set the limits of the axes
        ax.set_xlim3d(-1, 0.5)
        ax.set_ylim3d(1.5, -1.5)
        ax.set_zlim3d(1.2, -0.6)
            # Plot the data for the current frame
        frame_data = MT_tracking.iloc[frame]
        x = frame_data.filter(like='_x')
        y = frame_data.filter(like='_y')
        z = frame_data.filter(like='_z')
        
        # Mirror options (uncomment the ones you want to use):
        scatter = ax.scatter(x * -1,  # mirror X axis
                            y,        # original Y axis
                            z * -1,   # mirror Z axis
                            marker='o')
        return scatter,


    def update_guesser(frame):
        ax.clear()
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        ax.set_title('3D Animation')
        
    
        ax.view_init(elev=0, azim=90) 

        # Set the limits of the axes
        ax.set_xlim3d(0.1, 1.4)
        ax.set_ylim3d(1.5, -1.5)
        ax.set_zlim3d(-2, 0)
        
        # Plot the data for the current frame
        frame_data = MT_tracking.iloc[frame]
        x = frame_data.filter(like='_x')
        y = frame_data.filter(like='_y')
        z = frame_data.filter(like='_z')
        
        # Mirror options (uncomment the ones you want to use):
        scatter = ax.scatter(x * 1,  # mirror X axis
                            y,        # original Y axis
                            z * - 1,   # mirror Z axis
                            marker='o')
        return scatter,

 
    # Create the animation
    # Instead of creating an animation, just show the first frame
    # update(190)  # Call update function with frame 0
    # plt.show()  # Display the plot
    if (type == "clue"):
        ani = FuncAnimation(fig, update_clue, frames=num_frames,interval=1000/30)
    else:
        ani = FuncAnimation(fig, update_guesser, frames=num_frames,interval=1000/30)

    # Save the animation as a video
    ani.save(output_path, writer='ffmpeg')
    print('saved the animation!')



def run_visualize_trc():
    data_dir = "data"
    
    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        print(f"Processing folder: {folder}")
        for item in os.listdir(folder_path):
            print(f"Processing item: {item}")
            item_path = os.path.join(folder_path, item)
            if item.startswith("Trial_") and os.path.isdir(item_path):
                clue_giver_path = os.path.join(item_path, "clue_giver")
                if os.path.exists(clue_giver_path):
                    print(f"Processing clue_giver folder in {item}")
                    pose_path = os.path.join(clue_giver_path, 'pose-3d')
                    if os.path.exists(pose_path):
                        # Find TRC files that don't end with LSTM or butterworth
                        trc_files = [f for f in os.listdir(pose_path) 
                                   if f.endswith('.trc') 
                                   and not any(suffix in f for suffix in ['LSTM', 'butterworth'])]
                        
                        for trc_file in trc_files:
                            trc_file_path = os.path.join(pose_path, trc_file)
                            # Create output CSV filename
                            csv_filename = os.path.splitext(trc_file)[0] + '.csv'
                            csv_output_path = os.path.join(clue_giver_path, csv_filename)
                            
                            # Convert TRC to CSV
                            trc_to_csv(trc_file_path, csv_output_path)
                            print(f"Converted {trc_file} to CSV")

                            # Plot the TRC file
                            trc_plot(csv_output_path, os.path.join(clue_giver_path, 'plot.mp4'), 'clue')
                            print(f"Plotted {trc_file}")

                # Similar process for guesser path
                guesser_path = os.path.join(item_path, "guesser")
                if os.path.exists(guesser_path):
                    print(f"Processing guesser folder in {item}")
                    pose_path = os.path.join(guesser_path, 'pose-3d')
                    if os.path.exists(pose_path):
                        trc_files = [f for f in os.listdir(pose_path) 
                                   if f.endswith('.trc') 
                                   and not any(suffix in f for suffix in ['LSTM', 'butterworth'])]
                        
                        for trc_file in trc_files:
                            trc_file_path = os.path.join(pose_path, trc_file)
                            csv_filename = os.path.splitext(trc_file)[0] + '.csv'
                            csv_output_path = os.path.join(guesser_path, csv_filename)
                            
                            # Convert TRC to CSV
                            trc_to_csv(trc_file_path, csv_output_path)
                            print(f"Converted {trc_file} to CSV")

                            # Plot the TRC file
                            trc_plot(csv_output_path, os.path.join(guesser_path, 'plot.mp4'), 'guess')
                            print(f"Plotted {trc_file}")


if __name__ == "__main__":
    # the pipeline will process the data in the data folder, the data should be copy from the data_condition_pair_with_board folder directly. 
    organize_files_by_trial() # organize the files by trial
    tidy_video_files() # tidy the video files, creating subfodlers for guesser and clue_giver
    swap_video_file_name() # changed the video names into cam01, cam02, cam03 etc for guesser and clue_giver
    run_pose2sim() # run the pose2sim pipeline
    run_visualize_trc() # visualize the trc file
