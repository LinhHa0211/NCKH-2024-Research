from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from math import ceil

import os


def mkdir(parent_folder_path: str, tail: str=None) -> str:
    output_path = parent_folder_path
            
    if tail is not None:
        output_path = os.path.join(output_path, tail)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    return output_path


def split_video(video_path: str, cut_videos_save_path: str, segment_duration: int) -> None:
    # Load the video
    video = VideoFileClip(video_path)
    video_duration = int(video.duration)
    num_total_segments = ceil(video_duration / min(segment_duration, video_duration))

    # Split video into segments
    for i in range(num_total_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, video_duration)
 
        if end_time - start_time < 10:
            continue
 
        # Extract the segment
        output_path = os.path.join(cut_videos_save_path, f"{os.path.basename(video_path)}_segment_{i + 1}.mp4")
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_path)
        print(f"Segment {i + 1} saved to {output_path}")


def cut_frames(video_path: str, output_frames_path: str, num_frames: int, start_time: int, end_time: int=-1) -> None:
    video = VideoFileClip(video_path)

    if start_time > end_time and end_time != -1:
        raise ValueError("Start time must be less than or equal to end time.")
    if start_time < 0 or (end_time < 0 and end_time != -1):
        raise ValueError("Start time and end time must be non-negative.")

    if end_time == -1:
        duration_in_seconds = int(video.duration) - start_time
    else:
        duration_in_seconds = min(int(video.duration), end_time) - start_time

    # Calculate the frames per second to capture the desired number of frames over the duration
    fps = num_frames / duration_in_seconds

    # Construct the output frame path
    oframes_path = os.path.join(output_frames_path, 'frame_%04d.png')

    # Execute the ffmpeg command
    os.system(f'ffmpeg -i "{video_path}" -vf "fps={fps}" -ss {start_time} -t {duration_in_seconds} "{oframes_path}"')


def extract_frames_from_video(video_path: str, cut_frames_save_path: str, num_frames_per_seg: int) -> None:
    if video_path.endswith('.mp4'):
        tail = os.path.basename(video_path).replace('.mp4', '')
        output_frames_path = mkdir(cut_frames_save_path, tail=tail)
        cut_frames(video_path, output_frames_path, num_frames=num_frames_per_seg, start_time=0)
        
        
        

    