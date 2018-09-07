import nmiConfig
import datetime
import multiprocessing
import os
import stat
import i18n
import wx
from imageio.plugins import ffmpeg
from ObjectListView import ColumnDefn, FastObjectListView


########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    """Class who defines the FileDropTarget and removes the duplicated files"""

    # ----------------------------------------------------------------------
    def __init__(self, window):
        """Constructor"""
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.all_filenames = []

    # ----------------------------------------------------------------------
    def OnDropFiles(self, x, y, filenames):
        """When files are dropped, update the display """
        self.RemoveDuplicated(self.all_filenames, filenames)
        self.all_filenames += filenames
        self.window.updateDisplay(filenames)
        return True

    # ----------------------------------------------------------------------
    def RemoveDuplicated(self, X, Y):
        """Get two lists and remove duplications in Y (filenames)"""
        for A in X:
            for B in Y:
                if A == B:
                    Y.remove(B)

########################################################################


class FileInfo(object):
    """Class who defines de FileInfo object used in dropped items"""

    # ----------------------------------------------------------------------
    def __init__(self, path, minutes_lenght, size):
        """Constructor"""
        self.name = os.path.basename(path)
        self.path = path
        self.minutes_lenght = minutes_lenght
        self.size = size

########################################################################


class MainPanel(wx.Panel):
    """Main Panel of the application"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, theme):
        """
        Constructor
        Defines the ObjectListView for dropped items
        and the layout for its components
        """
        wx.Panel.__init__(self, parent=parent)
        self.file_list = []

        self.primaryBackgroundColor = theme.get("primaryBackgroundColor")
        self.secondaryBackgroundColor = theme.get("secondaryBackgroundColor")
        self.foregroundColor = theme.get("foregroundColor")

        self.SetBackgroundColour(self.primaryBackgroundColor)
        self.SetForegroundColour(self.foregroundColor)

        file_drop_target = MyFileDropTarget(self)
        self.olv = FastObjectListView(
            self, style=wx.LC_REPORT | wx.BORDER_NONE)
        self.olv.SetEmptyListMsg(i18n.t('i18n.emptyList'))
        self.olv.SetDropTarget(file_drop_target)
        self.olv.cellEditMode = FastObjectListView.CELLEDIT_NONE
        self.setFiles()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.olv.Bind(wx.EVT_KEY_UP, self.OnDelete)
        self.sizer.Add(self.olv, 1, wx.EXPAND)

        grid1 = wx.GridSizer(1, 3, 1, 10)
        grid2 = wx.GridSizer(1, 3, 1, 10)

        self.lblCutInitSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutInitSec'))
        self.lblCutInitSec.SetFont(wx.Font(wx.FontInfo(pointSize=12)))

        self.txtCutInitSec = wx.TextCtrl(
            self, -1, "0", size=(175, -1), style=wx.BORDER_STATIC)
        self.txtCutInitSec.SetBackgroundColour(self.secondaryBackgroundColor)
        self.txtCutInitSec.SetForegroundColour(self.foregroundColor)
        self.txtCutInitSec.SetFont(wx.Font(wx.FontInfo(pointSize=12)))

        self.lblCutEndSec = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutEndSec'))
        self.lblCutEndSec.SetFont(wx.Font(wx.FontInfo(pointSize=12)))

        self.txtCutEndSec = wx.TextCtrl(
            self, -1, "0", size=(175, -1), style=wx.BORDER_STATIC)
        self.txtCutEndSec.SetBackgroundColour(self.secondaryBackgroundColor)
        self.txtCutEndSec.SetForegroundColour(self.foregroundColor)
        self.txtCutEndSec.SetFont(wx.Font(wx.FontInfo(pointSize=12)))

        self.chkDelete = wx.CheckBox(self, -1, i18n.t('i18n.chkDelete'))
        self.chkDelete.SetFont(wx.Font(wx.FontInfo(pointSize=12)))

        grid1.AddMany([self.lblCutInitSec, self.lblCutEndSec])
        grid1.AddSpacer(0)
        grid2.AddMany([self.txtCutInitSec, self.txtCutEndSec, self.chkDelete])

        self.btnCut = wx.Button(
            self, -1, i18n.t('i18n.btnCut'), size=(100, 50), style=wx.BORDER_NONE)
        self.btnCut.Bind(wx.EVT_BUTTON, self.OnCut)
        self.btnCut.SetBackgroundColour(self.secondaryBackgroundColor)
        self.btnCut.SetForegroundColour(self.foregroundColor)
        self.btnCut.SetFont(wx.Font(wx.FontInfo(pointSize=30)))

        self.sizer.AddSpacer(20)
        self.sizer.Add(grid1, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 10)
        self.sizer.Add(grid2, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.btnCut, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

    # ----------------------------------------------------------------------
    def updateDisplay(self, file_list):
        """
        Triggered when dropped items,
        get the item and transform it into FileInfo with parameters
        to use it in ObjectListView
        """
        import nmiVideoUtils
        for path in file_list:
            file_stats = os.stat(path)
            try:
                clip_duration = nmiVideoUtils.get_video_duration(path)
            except:
                wx.MessageBox(i18n.t('i18n.onlyVideosError'), "Error")
                return
            minutes_lenght = str(datetime.timedelta(
                seconds=clip_duration))
            file_size = file_stats[stat.ST_SIZE]
            if file_size > 1024:
                file_size = file_size / 1024.0
                file_size = "%.2f KB" % file_size

            self.file_list.append(FileInfo(path, minutes_lenght, file_size))

        self.olv.SetObjects(self.file_list)

    # ----------------------------------------------------------------------
    def setFiles(self):
        """Set the columns for items dropped"""
        self.olv.SetColumns([
            ColumnDefn(i18n.t('i18n.colName'), "left",
                       250, "name", isSpaceFilling=True),
            ColumnDefn(i18n.t('i18n.colMinutes'),
                       "right", 150, "minutes_lenght"),
            ColumnDefn(i18n.t('i18n.colSize'), "right", 150, "size")
        ])
        self.olv.SetObjects(self.file_list)

    # ----------------------------------------------------------------------
    def OnCut(self, event):
        """
        Trigger when click on CUT Button,
        Get parameters and in a for loop cut videos calling the function
        """
        import nmiVideoUtils
        try:
            beginning = int(self.txtCutInitSec.GetLineText(1))
            end = int(self.txtCutEndSec.GetLineText(1))
            delete = self.chkDelete.GetValue()
            delete_file_list = list()
        except:
            wx.MessageBox(
                i18n.t('i18n.onlyNumberError'), "Error")
            return

        if self.file_list:
            c = 0
            list_count = len(self.file_list)
            dialog = wx.ProgressDialog(i18n.t('i18n.cutProgressTitle'),
                                       i18n.t('i18n.cutProgress') +
                                       str(c)+'/'+str(list_count),
                                       maximum=list_count, style=wx.PD_SMOOTH |
                                       wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE)
            for file in self.file_list:
                cut = nmiVideoUtils.cut_video(beginning, end, file)
                if(cut.get('state')):
                    delete_file_list.append(file)
                    c += 1
                    if dialog.WasCancelled() is True:
                        wx.MessageBox(i18n.t('i18n.cutCancel'), "Error")
                        break
                    dialog.Update(c, i18n.t('i18n.cutProgress') +
                                  str(c+1)+'/'+str(list_count))
            for file in delete_file_list:
                self.file_list.remove(file)
            self.olv.RemoveObjects(delete_file_list)
            self.olv.SetObjects(self.file_list)
            wx.MessageBox(str(c) +
                          i18n.t('i18n.cutVideos'), "OK")
        else:
            wx.MessageBox(i18n.t('i18n.noCutVideosError'), "Error")
            return

        if(delete is True):
            try:
                nmiVideoUtils.delete_files(delete_file_list)
                wx.MessageBox(i18n.t('i18n.deletedOld'), "OK")
            except:
                wx.MessageBox(i18n.t('i18n.permisionError'), "Error")

    # ----------------------------------------------------------------------
    def OnDelete(self, event):
        """Trigger the event when user delete item from list with SUPR"""
        if(event.GetUnicodeKey() == 127 and
           self.olv.GetSelectedItemCount() > 0):
            for i in self.olv.GetSelectedObjects():
                self.file_list.remove(i)
            self.olv.RemoveObjects(self.olv.GetSelectedObjects())
            self.olv.SetObjects(self.file_list)

########################################################################


class MainFrame(wx.Frame):
    """Main window of the application"""

    # ----------------------------------------------------------------------
    def __init__(self, theme):
        """
        Constructor
        Sets width, name and icon of the window
        """
        wx.Frame.__init__(self, None, title="NoMoreIntros", size=(570, 400))

        menuBar = wx.MenuBar()
        configMenu = wx.Menu()

        themeMenu = wx.Menu()

        lightItem = wx.MenuItem(themeMenu, 1, text=i18n.t(
            'i18n.lightTheme'), kind=wx.ITEM_NORMAL)
        themeMenu.Append(lightItem)

        darkItem = wx.MenuItem(themeMenu, 2, text=i18n.t(
            'i18n.darkTheme'), kind=wx.ITEM_NORMAL)
        themeMenu.Append(darkItem)

        configMenu.Append(wx.ID_ANY, i18n.t('i18n.themeMenu'), themeMenu)
        configMenu.AppendSeparator()

        langMenu = wx.Menu()

        es = wx.MenuItem(langMenu, 3, text="Español", kind=wx.ITEM_NORMAL)
        langMenu.Append(es)

        en = wx.MenuItem(langMenu, 4, text="English", kind=wx.ITEM_NORMAL)
        langMenu.Append(en)

        configMenu.Append(wx.ID_ANY, i18n.t('i18n.langMenu'), langMenu)
        configMenu.AppendSeparator()

        checkUpdates = wx.MenuItem(configMenu, 5, text=i18n.t(
            'i18n.checkUpdatesMenu'), kind=wx.ITEM_NORMAL)

        configMenu.Append(checkUpdates)

        menuBar.Append(configMenu, i18n.t('i18n.menu1Title'))

        quit = wx.MenuItem(configMenu, wx.ID_EXIT, i18n.t('i18n.quit'))

        configMenu.Append(quit)

        panel = MainPanel(self, theme)

        ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)

        self.SetIcon(ico)
        self.SetMinSize(wx.Size(570, 400))
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.menuhandler)
        self.Show()

    # ----------------------------------------------------------------------
    def menuhandler(self, event):
        id = event.GetId()
        print(id)
        if(id == wx.ID_EXIT):
            raise SystemExit
        elif(id == 1):
            if(nmiConfig.setTheme("lightTheme") == True):
                self.reloadApp()
        elif(id == 2):
            if(nmiConfig.setTheme("darkTheme") == True):
                self.reloadApp()
        elif(id == 3):
            if(nmiConfig.setLanguage("es") == True):
                self.reloadApp()
        elif(id == 4):
            if(nmiConfig.setLanguage("en") == True):
                self.reloadApp()
        elif(id == 5):
            if(nmiConfig.setVersion(1.0) == True):
                print("Ahora es 1.0")
            else:
                print("Ya era 1.0")

    # ----------------------------------------------------------------------
    def reloadApp(self):
        self.Close()
        main(nmiConfig.getLanguage(), nmiConfig.getTheme())
        raise SystemExit

########################################################################


def check_ffmpeg():
    """Checks before all if user has FFMPEG dependency, if not downloads it"""
    try:
        import nmiVideoUtils
    except:
        wx.MessageBox(i18n.t('i18n.ffmpegNotFound'), "Error")
        if(os.path.isdir(os.getenv('LOCALAPPDATA'))):
            thread = multiprocessing.Process(target=copy_ffmpeg)
        else:
            thread = multiprocessing.Process(target=ffmpeg.download)
        progressDialog(thread, i18n.t('i18n.ffmpegProgressTitle'), i18n.t(
            'i18n.ffmpegProgressMsg'), i18n.t('i18n.ffmpegCancel'))


def progressDialog(thread, title, msg, error):
    thread.start()
    dialog = wx.ProgressDialog(
        title,
        msg,
        maximum=1, style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT)
    while thread.is_alive():
        dialog.Pulse()
        if dialog.WasCancelled() is True:
            thread.terminate()
            wx.MessageBox(error, "Error")
            return
    else:
        dialog.Update(1)
        wx.MessageBox(i18n.t('i18n.ffmpegDownloaded'), "OK")


def copy_ffmpeg():
    """Copy ffmpeg file directly without downloading for windows users"""
    os.system('xcopy /E /I /Y "bin/imageio" "' +
              os.getenv('LOCALAPPDATA')+'/imageio"')


def main(lang, theme):
    """
    Main loop
    Sets i18n, check FFMPEG dependency and init the MainWindow
    """
    i18n.set('locale', lang)
    i18n.set('fallback', 'en')
    i18n.load_path.append('./lang/')
    app = wx.App(False)
    frame = MainFrame(theme)
    check_ffmpeg()
    app.MainLoop()


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Needed to use multiprocessing with pyinstaller
    nmiConfig.getConfig()
    main(nmiConfig.getLanguage(), nmiConfig.getTheme())
