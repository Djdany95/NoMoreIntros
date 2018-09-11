import os


# ----------------------------------------------------------------------
def copy_ffmpeg():
    """Copy ffmpeg file directly without downloading for windows users"""
    os.system('xcopy /E /I /Y "bin/imageio" "' +
              os.getenv('LOCALAPPDATA')+'/imageio"')


# ----------------------------------------------------------------------
def remove_duplicated(x, y):
    """Get two lists and remove duplications in Y (filenames)"""
    for a in x:
        for b in y:
            if (a == b):
                y.remove(b)
