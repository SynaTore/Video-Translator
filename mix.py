from moviepy.editor import VideoFileClip, AudioFileClip, vfx

def mixing(video_file, audio_file, output_file):
    
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
    # Note: new_duration = original_duration / factor, so factor = original_duration / target_duration
    video_speed_factor = video_duration / target_duration
    audio_speed_factor = audio_duration / target_duration
    print(f"Video speed factor: {video_speed_factor}")
    print(f"Audio speed factor: {audio_speed_factor}")
    # Apply the speed change; this will alter the duration to approximately the target duration.
    # For video: also remove its original audio using without_audio()
    adjusted_video = video_clip.fx(vfx.speedx, factor=video_speed_factor).without_audio()
    # For audio: adjust its speed
    adjusted_audio = audio_clip.fx(vfx.speedx, factor=audio_speed_factor)
    # Combine the adjusted video and audio
    # The video is already muted (using without_audio()), so we overlay our adjusted audio.
    final_clip = adjusted_video.set_audio(adjusted_audio)
    # Write the result to a new file
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    # Close clips to free resources
    video_clip.close()
    audio_clip.close()
    final_clip.close()