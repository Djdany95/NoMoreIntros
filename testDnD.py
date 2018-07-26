import os
import stat
import datetime
import wx
from ObjectListView import ObjectListView, ColumnDefn
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
import cutScript
import i18n


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
        return True

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
        self.olv.SetEmptyListMsg(i18n.t('i18n.emptyList'))
        self.olv.SetDropTarget(file_drop_target)
        self.olv.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.setFiles()

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.olv.Bind(wx.EVT_KEY_UP, self.OnDelete)
        sizer.Add(self.olv, 1, wx.EXPAND)
        self.lblCutInitSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutInitSec'))
        self.lblCutEndSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutEndSec'))
        self.txtCutInitSec = wx.TextCtrl(self, -1, "0", size=(175, -1))
        self.txtCutEndSec = wx.TextCtrl(self, -1, "0", size=(175, -1))
        self.chkDelete = wx.CheckBox(self, -1, i18n.t('i18n.chkDelete'))
        self.btnCut = wx.Button(
            self, -1, i18n.t('i18n.btnCut'), size=(100, 50))
        self.btnCut.Bind(wx.EVT_BUTTON, self.OnCut)
        sizer.AddMany([self.lblCutInitSec, self.txtCutInitSec,
                       self.lblCutEndSec, self.txtCutEndSec, self.chkDelete])
        sizer.Add(self.btnCut, 0, wx.EXPAND)
        self.SetSizer(sizer)

    # ----------------------------------------------------------------------
    def updateDisplay(self, file_list):
        """"""
        for path in file_list:
            file_stats = os.stat(path)
            try:
                clip = VideoFileClip(path)
            except:
                wx.MessageBox(i18n.t('i18n.onlyVideosError'), "Error")
                return
            minutes_lenght = str(datetime.timedelta(
                seconds=int(clip.duration)))
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
            ColumnDefn(i18n.t('i18n.colName'), "left", 250, "name"),
            ColumnDefn(i18n.t('i18n.colMinutes'),
                       "left", 150, "minutes_lenght"),
            ColumnDefn(i18n.t('i18n.colSize'), "left", 150, "size")
        ])
        self.olv.SetObjects(self.file_list)

    def OnCut(self, event):
        try:
            begin = int(self.txtCutInitSec.GetLineText(1))
            end = int(self.txtCutEndSec.GetLineText(1))
            delete = self.chkDelete.GetValue()
            delete_file_list = self.file_list.copy()
        except:
            wx.MessageBox(
                i18n.t('i18n.onlyNumberError'), "Error")
            return

        if(cutScript.check_list(self.file_list) == True):
            cutted = cutScript.cut_video(begin, end, self.file_list)
            if(cutted.get('state')):
                self.file_list.clear()
                self.updateDisplay(self.file_list)
                wx.MessageBox(cutted.get('num') +
                              i18n.t('i18n.cutVideos'), "OK")
        else:
            wx.MessageBox(i18n.t('i18n.noCutVideosError'), "Error")
            return

        if(delete == True and cutted.get('state') == True):
            deleted = cutScript.delete_files(delete_file_list)

        if(deleted):
            wx.MessageBox(i18n.t('i18n.deletedOld'), "OK")
        else:
            wx.MessageBox(i18n.t('i18n.permisionError'), "Error")

    def OnDelete(self, event):
        if(event.GetUnicodeKey() == 127 and self.olv.GetSelectedItemCount() > 0):
            for i in self.olv.GetSelectedObjects():
                self.file_list.remove(i)
            self.olv.RemoveObjects(self.olv.GetSelectedObjects())
            self.updateDisplay(self.file_list)

########################################################################


class MainFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="NoMoreIntros", size=(570, 400))
        panel = MainPanel(self)
        self.Show()

# ----------------------------------------------------------------------


def main():
    """"""
    i18n.set('locale', 'es')
    i18n.set('fallback', 'en')
    i18n.load_path.append('./i18n/')
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()


if __name__ == "__main__":
    main()
