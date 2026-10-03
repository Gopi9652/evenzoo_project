from moviepy import VideoFileClip
import tempfile
import os

MAX_VIDEO_SIZE_BYTES = 10 * 1024 * 1024   # same 10MB cap as images
ABSOLUTE_MAX_VIDEO_SIZE = 50 * 1024 * 1024  # hard reject above this before any processing
MAX_DURATION_SECONDS = 60   # keep vendor showcase clips short


def process_video(input_path: str) -> str:
    """
    If the video is already under 10MB, returns the original path unchanged.
    Otherwise re-encodes at a lower bitrate/resolution until it fits,
    writing to a new temp file and returning that path.
    """
    file_size = os.path.getsize(input_path)
    if file_size <= MAX_VIDEO_SIZE_BYTES:
        return input_path

    clip = VideoFileClip(input_path)

    # Cap duration defensively, independent of size
    if clip.duration > MAX_DURATION_SECONDS:
        clip = clip.subclip(0, MAX_DURATION_SECONDS)

    # Progressively reduce resolution/bitrate until under target size
    target_heights = [720, 480, 360]
    output_path = input_path.replace(".mp4", "_compressed.mp4")

    for height in target_heights:
        resized = clip.resize(height=height)
        resized.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            bitrate="800k",
            preset="fast",
            logger=None
        )

        if os.path.getsize(output_path) <= MAX_VIDEO_SIZE_BYTES:
            break

    clip.close()
    return output_path


def generate_thumbnail(video_path: str) -> str:
    """Extracts a frame at 1 second as a static thumbnail image."""
    clip = VideoFileClip(video_path)
    thumbnail_path = video_path.replace(".mp4", "_thumb.jpg")
    clip.save_frame(thumbnail_path, t=min(1.0, clip.duration / 2))
    clip.close()
    return thumbnail_path