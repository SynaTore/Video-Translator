from moviepy.editor import VideoFileClip, AudioFileClip, vfx
import gc

def mixing(video_file, audio_file, output_file):
    try:
        # Load the video and audio files
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)
        
        # Get durations (in seconds)
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration
        print(f"Original video duration: {video_duration} seconds")
        print(f"Original audio duration: {audio_duration} seconds")
        
        # Define the target duration as the average of the two durations
        target_duration = (video_duration + audio_duration) / 2
        print(f"Target merged duration: {target_duration} seconds")
        
        # Calculate speed factors
        video_speed_factor = video_duration / target_duration
        audio_speed_factor = audio_duration / target_duration
        print(f"Video speed factor: {video_speed_factor}")
        print(f"Audio speed factor: {audio_speed_factor}")
        
        try:
            # Apply the speed change in chunks to reduce memory usage
            adjusted_video = video_clip.fx(vfx.speedx, factor=video_speed_factor).without_audio()
            adjusted_audio = audio_clip.fx(vfx.speedx, factor=audio_speed_factor)
            
            # Combine the adjusted video and audio
            final_clip = adjusted_video.set_audio(adjusted_audio)
            
            # Write the result to a new file with optimized settings
            final_clip.write_videofile(
                output_file,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                threads=4,
                preset='medium'  # Balance between speed and quality
            )
            return True
            
        except Exception as e:
            print(f"Error during video processing: {str(e)}")
            return False
            
    finally:
        # Explicit cleanup to free memory
        try:
            video_clip.close()
            audio_clip.close()
            final_clip.close()
        except:
            pass
        
        # Force garbage collection
        gc.collect()