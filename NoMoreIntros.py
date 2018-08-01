import datetime
import os
import stat
import multiprocessing
import i18n
import wx
from ObjectListView import ColumnDefn, ObjectListView
from imageio.plugins import ffmpeg


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

        grid1 = wx.GridSizer(1, 3, 1, 10)
        grid2 = wx.GridSizer(1, 3, 1, 10)
        self.lblCutInitSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutInitSec'))
        self.txtCutInitSec = wx.TextCtrl(self, -1, "0", size=(175, -1))
        self.lblCutEndSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutEndSec'))
        self.txtCutEndSec = wx.TextCtrl(self, -1, "0", size=(175, -1))
        self.chkDelete = wx.CheckBox(self, -1, i18n.t('i18n.chkDelete'))
        grid1.AddMany([self.lblCutInitSec, self.lblCutEndSec])
        grid1.AddSpacer(0)
        grid2.AddMany([self.txtCutInitSec, self.txtCutEndSec, self.chkDelete])

        self.btnCut = wx.Button(
            self, -1, i18n.t('i18n.btnCut'), size=(100, 50))
        self.btnCut.Bind(wx.EVT_BUTTON, self.OnCut)
        sizer.AddSpacer(20)
        sizer.Add(grid1, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 10)
        sizer.Add(grid2, 0, wx.EXPAND | wx.LEFT, 10)
        sizer.AddSpacer(20)
        sizer.Add(self.btnCut, 0, wx.EXPAND)
        self.SetSizer(sizer)

    # ----------------------------------------------------------------------
    def updateDisplay(self, file_list):
        import CutScript
        """"""
        for path in file_list:
            file_stats = os.stat(path)
            try:
                clip_duration = CutScript.get_video_duration(path)
            except Exception as e:
                print(e)
                wx.MessageBox(i18n.t('i18n.onlyVideosError'), "Error")
                return
            minutes_lenght = str(datetime.timedelta(
                seconds=clip_duration))
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
        import CutScript
        try:
            begin = int(self.txtCutInitSec.GetLineText(1))
            end = int(self.txtCutEndSec.GetLineText(1))
            delete = self.chkDelete.GetValue()
            delete_file_list = self.file_list.copy()
        except:
            wx.MessageBox(
                i18n.t('i18n.onlyNumberError'), "Error")
            return

        if self.file_list:
            cutted = CutScript.cut_video(begin, end, self.file_list)
            if(cutted.get('state')):
                self.file_list.clear()
                self.updateDisplay(self.file_list)
                wx.MessageBox(cutted.get('num') +
                              i18n.t('i18n.cutVideos'), "OK")
        else:
            wx.MessageBox(i18n.t('i18n.noCutVideosError'), "Error")
            return

        if(delete is True and cutted.get('state') is True):
            try:
                CutScript.delete_files(delete_file_list)
                wx.MessageBox(i18n.t('i18n.deletedOld'), "OK")
            except:
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
        ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.SetMinSize(wx.Size(570, 400))
        self.Show()

# ----------------------------------------------------------------------


def check_ffmpeg():
    try:
        import CutScript
    except:
        wx.MessageBox(i18n.t('i18n.ffmpegError'), "Error")
        threadDownload = multiprocessing.Process(target=ffmpeg.download)
        threadDownload.start()
        dialog = wx.ProgressDialog(
            i18n.t('i18n.progressTitle'), i18n.t('i18n.progressMsg'), style=wx.PD_SMOOTH | wx.PD_CAN_ABORT)
        while threadDownload.is_alive():
            dialog.Pulse()
            if dialog.WasCancelled() is True:
                # TODO Test this
                threadDownload.terminate()
                return
        else:
            dialog.Destroy()
            wx.MessageBox(i18n.t('i18n.ffmpegDownloaded'), "OK")


def main():
    """"""
    i18n.set('locale', 'es')
    i18n.set('fallback', 'en')
    i18n.load_path.append('./lang/')
    app = wx.App(False)
    frame = MainFrame()
    check_ffmpeg()
    app.MainLoop()


if __name__ == "__main__":
    main()
