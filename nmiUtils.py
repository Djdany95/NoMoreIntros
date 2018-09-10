import os

# ----------------------------------------------------------------------
def copy_ffmpeg():
    """Copy ffmpeg file directly without downloading for windows users"""
    os.system('xcopy /E /I /Y "bin/imageio" "' +
              os.getenv('LOCALAPPDATA')+'/imageio"')


# ----------------------------------------------------------------------
def RemoveDuplicated(self, X, Y):
    """Get two lists and remove duplications in Y (filenames)"""
    for A in X:
        for B in Y:
            if A == B:
                Y.remove(B)