from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
import sys
import glob

minCut = 300

for i in glob.glob("*.mp4"):
	print(i)
	video = VideoFileClip(i)
	ffmpeg_extract_subclip(i, minCut, video.duration, targetname="n"+i)
