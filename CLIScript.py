from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
import glob
import os


def cut_video(begin, end, delete):

    c = 0
    files_delete = list()

    for i in glob.glob("*"):

        try:
            video = VideoFileClip(i)
            print("\n"+i)
        except Exception as e:
            continue

        ffmpeg_extract_subclip(
            i, int(begin), video.duration-int(end), targetname="n"+i)

        video.reader.close()
        video.audio.reader.close_proc()

        files_delete.append(i)

        c = c+1

    print("\nSe han cortado "+str(c)+" videos.\n")

    if int(delete) == 1:
        delete_files(files_delete)


def delete_files(file_list):
    for i in file_list:
        os.remove(i)
        print("Se ha borrado "+i+"\n")


def main():
    print("")
    begin = input("Segundos a cortar del inicio: ")
    end = input("Segundos del final: ")
    delete = input("Borrar archivos viejos? (0-1): ")
    cut_video(begin, end, delete)


main()
