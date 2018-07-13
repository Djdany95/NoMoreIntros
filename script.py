from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
import sys
import glob

minCut = input("Segundos a cortar: ")
c=0

for i in glob.glob("*"):
	print(i)
	try:
		video = VideoFileClip(i)
	except Exception as e:
		continue
	
	ffmpeg_extract_subclip(i, int(minCut), video.duration, targetname="n"+i)

	video.reader.close()
	video.audio.reader.close_proc()
	c=c+1

print("Se han cortado "+str(c)+" videos.")
sys.exit()