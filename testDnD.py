import os
import stat
import time
import wx
from ObjectListView import ObjectListView, ColumnDefn
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
import datetime


########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, window):
        """Constructor"""
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ----------------------------------------------------------------------
    def OnDropFiles(self, x, y, filenames):
        """
        When files are dropped, update the display
        """
        self.window.updateDisplay(filenames)

########################################################################


class FileInfo(object):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, path, minutes_lenght, size):
        """Constructor"""
        self.name = os.path.basename(path)
        self.path = path
        self.minutes_lenght = minutes_lenght
        self.size = size

########################################################################


class MainPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        self.file_list = []

        file_drop_target = MyFileDropTarget(self)
        self.olv = ObjectListView(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.olv.SetDropTarget(file_drop_target)
        self.setFiles()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.olv, 1, wx.EXPAND)
        self.SetSizer(sizer)
    
    # ----------------------------------------------------------------------
    def updateDisplay(self, file_list):
        """"""
        print(file_list)
        for path in file_list:
            file_stats = os.stat(path)
            clip = VideoFileClip(path)
            minutes_lenght = str(datetime.timedelta(seconds=int(clip.duration)))
            file_size = file_stats[stat.ST_SIZE]
            if file_size > 1024:
                file_size = file_size / 1024.0
                file_size = "%.2f KB" % file_size

            self.file_list.append(FileInfo(path,
                                           minutes_lenght,
                                           file_size))

        self.olv.SetObjects(self.file_list)

    # ----------------------------------------------------------------------
    def setFiles(self):
        """"""
        self.olv.SetColumns([
            ColumnDefn("Name", "left", 250, "name"),
            ColumnDefn("Minutes Lenght", "left", 150, "minutes_lenght"),
            ColumnDefn("Size", "left", 150, "size")
        ])
        self.olv.SetObjects(self.file_list)

########################################################################


class MainFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Test DnD", size=(600, 400))
        panel = MainPanel(self)
        self.Show()

# ----------------------------------------------------------------------


def main():
    """"""
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()


if __name__ == "__main__":
    main()
