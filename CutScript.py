import os
import time
import psutil
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip


# ----------------------------------------------------------------------
def get_video_duration(path):
    """Get the duration of the passed file and returns it if valid or raise an exception if invalid"""
    try:
        clip = VideoFileClip(path)
    except:
        clip.reader.close()
        clip.audio.reader.close_proc()
        clip.close()
        raise Exception
    else:
        clip.reader.close()
        clip.audio.reader.close_proc()
        clip.close()
        return int(clip.duration)


# ----------------------------------------------------------------------
def cut_video(beginning, end, file):
    """Cut seconds to the passed video in the beginning and in the end, returns True if all OK or False if fails"""
    try:
        video = VideoFileClip(file.path)
        ffmpeg_extract_subclip(
            file.path.replace('\\', '/'), int(beginning), video.duration-int(end),
            targetname=file.path.replace('\\', '/')[:-4]+'n' +
            file.path[len(file.path)-4:])

        video.reader.close()
        video.audio.reader.close_proc()
        video.close()

        return {'state': True}
    except:
        video.reader.close()
        video.audio.reader.close_proc()
        video.close()
        return {'state': False}


# ----------------------------------------------------------------------
def delete_files(files_delete):
    """Delete all files in the passed list, killing FFMPEG before because of write permission"""
    kill_ffmpeg()
    time.sleep(0.5)
    for i in files_delete:
        try:
            os.remove(i.path)
        except:
            return False
    return True


# ----------------------------------------------------------------------
def kill_ffmpeg():
    """Kill FFMPEG process because of write permission"""
    for proc in psutil.process_iter():
        if 'ffmpeg' in proc.name():
            print(proc.name)
            proc.kill()
