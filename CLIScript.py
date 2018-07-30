from imageio.plugins.ffmpeg import download
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
from os import remove
from psutil import process_iter
from time import sleep
from glob import glob


def check_list(file_list):
    if not file_list:
        return False
    else:
        return True


def cut_video(begin, end, file_list):

    c = 0

    for i in file_list:
        try:
            video = VideoFileClip(i.path)
        except Exception as e:
            continue
        ffmpeg_extract_subclip(
            i.path.replace('\\', '/'), int(begin), video.duration-int(end), targetname=i.path.replace('\\', '/')[:-4]+'n'+i.path[len(i.path)-4:])

        video.reader.close()
        video.audio.reader.close_proc()
        video.close()

        c = c+1

    return {'state': True, 'num': str(c)}


def delete_files(files_delete):
    kill_ffmpeg()
    sleep(0.5)
    for i in files_delete:
        try:
            remove(i.path)
        except:
            return False
    return True


def kill_ffmpeg():
    for proc in process_iter():
        if 'ffmpeg' in proc.name():
            print(proc.name)
            proc.kill()

############# If want to use it only in COMMAND LINE #############


def cut_video_CLI(begin, end, delete):

    c = 0
    files_delete = list()

    for i in glob("*"):

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


def delete_files_CLI(file_list):
    for i in file_list:
        remove(i)
        print("Se ha borrado "+i+"\n")


def main():
    download()
    cut_video_CLI(300, 0, True)

main()
