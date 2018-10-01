import datetime
import multiprocessing
import os
import stat

import i18n
import wx
from imageio.plugins import ffmpeg
from ObjectListView import ColumnDefn, FastObjectListView

import nmi_config
import nmi_utils


########################################################################
class VideoDropTarget(wx.FileDropTarget):
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
        nmi_utils.remove_duplicated(self.all_filenames, filenames)
        self.all_filenames += filenames
        self.window.update_display(filenames)
        return True

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
        self.videos_list = []

        self.primary_background_color = theme.get("primaryBackgroundColor")
        self.secondary_background_color = theme.get("secondaryBackgroundColor")
        self.foreground_color = theme.get("foregroundColor")
        self.list_font = wx.Font(pointSize=11, family=wx.FONTFAMILY_SWISS, style=wx.FONTSTYLE_NORMAL,
                                 weight=wx.FONTWEIGHT_LIGHT, underline=False, faceName='Roboto')
        self.regular_font = wx.Font(pointSize=12, family=wx.FONTFAMILY_SWISS, style=wx.FONTSTYLE_NORMAL,
                                    weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName='Roboto')
        self.big_font = wx.Font(pointSize=32, family=wx.FONTFAMILY_SWISS, style=wx.FONTSTYLE_NORMAL,
                                weight=wx.FONTWEIGHT_BOLD, underline=False, faceName='Roboto')

        self.SetBackgroundColour(self.primary_background_color)
        self.SetForegroundColour(self.foreground_color)

        video_drop_target = VideoDropTarget(self)
        self.olv = FastObjectListView(
            self, style=wx.LC_REPORT | wx.BORDER_NONE)
        self.olv.SetEmptyListMsg(i18n.t('i18n.emptyList'))
        self.olv.SetDropTarget(video_drop_target)
        self.olv.cellEditMode = FastObjectListView.CELLEDIT_NONE
        self.olv.SetEmptyListMsgFont(self.big_font)
        self.olv.SetFont(self.list_font)
        self.set_files()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.olv.Bind(wx.EVT_KEY_UP, self.on_delete)
        self.sizer.Add(self.olv, 1, wx.EXPAND)

        grid1 = wx.GridSizer(1, 3, 1, 10)
        grid2 = wx.GridSizer(1, 3, 1, 10)

        self.lbl_cut_init = wx.StaticText(
            self, -1, i18n.t('i18n.lblCutInitSec'))
        self.lbl_cut_init.SetFont(self.regular_font)

        self.txt_cut_init = wx.TextCtrl(
            self, -1, "0", size=(175, -1), style=wx.BORDER_STATIC)
        self.txt_cut_init.SetBackgroundColour(self.secondary_background_color)
        self.txt_cut_init.SetForegroundColour(self.foreground_color)
        self.txt_cut_init.SetFont(self.regular_font)

        self.lbl_cut_end = wx.StaticText(self, -1, i18n.t('i18n.lblCutEndSec'))
        self.lbl_cut_end.SetFont(self.regular_font)

        self.txt_cut_end = wx.TextCtrl(
            self, -1, "0", size=(175, -1), style=wx.BORDER_STATIC)
        self.txt_cut_end.SetBackgroundColour(self.secondary_background_color)
        self.txt_cut_end.SetForegroundColour(self.foreground_color)
        self.txt_cut_end.SetFont(self.regular_font)

        self.chk_delete = wx.CheckBox(self, -1, i18n.t('i18n.chkDelete'))
        self.chk_delete.SetFont(self.regular_font)

        grid1.AddMany([self.lbl_cut_init, self.lbl_cut_end])
        grid1.AddSpacer(0)
        grid2.AddMany([self.txt_cut_init, self.txt_cut_end, self.chk_delete])

        self.btn_cut = wx.Button(
            self, -1, i18n.t('i18n.btnCut'), size=(100, 50), style=wx.BORDER_NONE)
        self.btn_cut.Bind(wx.EVT_BUTTON, self.on_cut)
        self.btn_cut.SetBackgroundColour(self.secondary_background_color)
        self.btn_cut.SetForegroundColour(self.foreground_color)
        self.btn_cut.SetFont(self.big_font)

        self.sizer.AddSpacer(20)
        self.sizer.Add(grid1, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 10)
        self.sizer.Add(grid2, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.btn_cut, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

    # ----------------------------------------------------------------------
    def update_display(self, videos_list):
        """
        Triggered when dropped items,
        get the item and transform it into VideoInfo with parameters
        to use it in ObjectListView
        """
        import nmi_video
        for path in videos_list:
            file_stats = os.stat(path)
            try:
                clip_duration = nmi_video.get_video_duration(path)
            except Exception as e:
                dialog = wx.RichMessageDialog(self, i18n.t('i18n.onlyVideosError'), "Error", wx.ICON_ERROR)
                dialog.ShowDetailedText("Error info:\n" + "\\" + str(e) + "\\")
                dialog.ShowModal()
                return
            minutes_lenght = str(datetime.timedelta(seconds=clip_duration))
            file_size = file_stats[stat.ST_SIZE]
            if (file_size > 1024):
                file_size = file_size / 1024.0
                if (file_size > 1024.0):
                    file_size = file_size / 1024.0
                    file_size = "%.2f MB" % file_size
                else:
                    file_size = "%.2f KB" % file_size

            self.videos_list.append(nmi_video.VideoInfo(
                path, minutes_lenght, file_size))

        self.olv.SetObjects(self.videos_list)

    # ----------------------------------------------------------------------
    def set_files(self):
        """Set the columns for items dropped"""
        self.olv.SetColumns([
            ColumnDefn(i18n.t('i18n.colName'), "left",
                       250, "name", isSpaceFilling=True),
            ColumnDefn(i18n.t('i18n.colMinutes'),
                       "right", 150, "minutes_lenght"),
            ColumnDefn(i18n.t('i18n.colSize'), "right", 150, "size")
        ])
        self.olv.SetObjects(self.videos_list)

    # ----------------------------------------------------------------------
    def on_cut(self, event):
        """
        Trigger when click on CUT Button,
        Get parameters and in a for loop cut videos calling the function
        """
        import nmi_video
        try:
            beginning = int(self.txt_cut_init.GetLineText(1))
            end = int(self.txt_cut_end.GetLineText(1))
            delete = self.chk_delete.GetValue()
            delete_videos_list = list()
        except Exception as e:
            dialog = wx.RichMessageDialog(self, i18n.t('i18n.onlyNumberError'), "Error", wx.ICON_ERROR)
            dialog.ShowDetailedText("Error info:\n" + "\\" + str(e) + "\\")
            dialog.ShowModal()
            return

        if (len(self.videos_list) > 0):
            c = 0
            list_count = len(self.videos_list)
            dialog = wx.ProgressDialog(i18n.t('i18n.cutProgressTitle'), i18n.t('i18n.cutProgress') + str(
                c)+'/'+str(list_count), maximum=list_count, style=wx.PD_SMOOTH | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE)
            for file in self.videos_list:
                cut = nmi_video.cut_video(beginning, end, file)
                if (cut.get('state') is True):
                    delete_videos_list.append(file)
                    c += 1
                    if (dialog.WasCancelled() is True):
                        dialog = wx.RichMessageDialog(self, i18n.t('i18n.cutCancel'), "Error", wx.ICON_ERROR)
                        dialog.ShowModal()
                        break
                    dialog.Update(c, i18n.t('i18n.cutProgress') +
                                  str(c+1)+'/'+str(list_count))
            for file in delete_videos_list:
                self.videos_list.remove(file)
            self.olv.RemoveObjects(delete_videos_list)
            self.olv.SetObjects(self.videos_list)
            wx.MessageBox(str(c) + i18n.t('i18n.cutVideos'),
                          "OK", wx.ICON_INFORMATION)
        else:
            dialog = wx.RichMessageDialog(self, i18n.t('i18n.noCutVideosError'), "Error", wx.ICON_ERROR)
            dialog.ShowModal()
            return

        if (delete is True):
            try:
                nmi_video.delete_videos(delete_videos_list)
                wx.MessageBox(i18n.t('i18n.deletedOld'),
                              "OK", wx.ICON_INFORMATION)
            except Exception as e:
                dialog = wx.RichMessageDialog(self, i18n.t('i18n.permisionError'), "Error", wx.ICON_ERROR)
                dialog.ShowDetailedText("Error info:\n" + "\\" + str(e) + "\\")
                dialog.ShowModal()

    # ----------------------------------------------------------------------
    def on_delete(self, event):
        """Trigger the event when user delete item from list with SUPR"""
        if (event.GetUnicodeKey() == 127 and self.olv.GetSelectedItemCount() > 0):
            for i in self.olv.GetSelectedObjects():
                self.videos_list.remove(i)
            self.olv.RemoveObjects(self.olv.GetSelectedObjects())
            self.olv.SetObjects(self.videos_list)

########################################################################


class MainFrame(wx.Frame):
    """Main window of the application"""

    # ----------------------------------------------------------------------
    def __init__(self, lang, theme, pos, size):
        """
        Constructor
        Sets width, name and icon of the window
        """
        wx.Frame.__init__(self, None, title="NoMoreIntros", pos=pos, size=size)

        menubar = wx.MenuBar()

        config_menu = wx.Menu()
        help_menu = wx.Menu()

        theme_menu = wx.Menu()

        light_theme = wx.MenuItem(theme_menu, 1, text=i18n.t(
            'i18n.lightTheme'), kind=wx.ITEM_RADIO)
        theme_menu.Append(light_theme)

        dark_theme = wx.MenuItem(theme_menu, 2, text=i18n.t(
            'i18n.darkTheme'), kind=wx.ITEM_RADIO)
        theme_menu.Append(dark_theme)

        if (theme.get("name") == 'lightTheme'):
            light_theme.Check()
        else:
            dark_theme.Check()

        config_menu.Append(wx.ID_ANY, i18n.t(
            'i18n.themeMenuTitle'), theme_menu)
        config_menu.AppendSeparator()

        lang_menu = wx.Menu()

        es_lang = wx.MenuItem(lang_menu, 3, text="Español", kind=wx.ITEM_RADIO)
        lang_menu.Append(es_lang)

        en_lang = wx.MenuItem(lang_menu, 4, text="English", kind=wx.ITEM_RADIO)
        lang_menu.Append(en_lang)

        if (lang == 'es'):
            es_lang.Check()
        else:
            en_lang.Check()

        config_menu.Append(wx.ID_ANY, i18n.t('i18n.langMenuTitle'), lang_menu)
        config_menu.AppendSeparator()

        quit = wx.MenuItem(config_menu, wx.ID_EXIT, i18n.t('i18n.quit'))

        config_menu.Append(quit)

        menubar.Append(config_menu, i18n.t('i18n.configMenuTitle'))

        check_updates = wx.MenuItem(help_menu, 5, text=i18n.t(
            'i18n.checkUpdatesMenu'), kind=wx.ITEM_NORMAL)
        help_menu.Append(check_updates)
        help_menu.AppendSeparator()
        openHelp = wx.MenuItem(help_menu, 6, text=i18n.t(
            'i18n.openHelpMenu'), kind=wx.ITEM_NORMAL)
        help_menu.Append(openHelp)
        help_menu.AppendSeparator()

        about = wx.MenuItem(help_menu, 7, text=i18n.t(
            'i18n.aboutMenuTitle'), kind=wx.ITEM_NORMAL)
        help_menu.Append(about)

        menubar.Append(help_menu, i18n.t('i18n.helpMenuTitle'))

        panel = MainPanel(self, theme)

        ico = wx.Icon('NoMoreIntros.ico', wx.BITMAP_TYPE_ICO)

        self.SetIcon(ico)
        self.SetMinSize(wx.Size(570, 400))
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.menu_handler)
        self.Show()

    # ----------------------------------------------------------------------
    def menu_handler(self, event):
        """Menu buttons event handler"""
        id = event.GetId()
        if (id == wx.ID_EXIT):
            raise SystemExit
        elif (id == 1):
            if (nmi_config.set_theme("lightTheme") is True):
                self.reload_app()
        elif (id == 2):
            if (nmi_config.set_theme("darkTheme") is True):
                self.reload_app()
        elif (id == 3):
            if (nmi_config.set_language("es") is True):
                self.reload_app()
        elif (id == 4):
            if (nmi_config.set_language("en") is True):
                self.reload_app()
        elif (id == 5):
            update = nmi_config.check_update()
            if (update is False):
                wx.MessageBox(i18n.t('i18n.noUpdates'),
                              "OK", wx.ICON_INFORMATION)
            else:
                dlg = wx.MessageDialog(self, i18n.t(
                    'i18n.updateDialog'), 'Updater', wx.YES_NO | wx.ICON_EXCLAMATION)
                result = dlg.ShowModal()

                if (result == wx.ID_YES):
                    thread = multiprocessing.Process(
                        target=nmi_config.download_latest_version)
                    create_progress_dialog(thread, i18n.t('i18n.updateProgressTitle'), i18n.t(
                        'i18n.updateProgressMsg'), i18n.t('i18n.updateCancel'), i18n.t('i18n.updateDownloaded'))
        elif (id == 6):
            about_info = wx.adv.AboutDialogInfo()
            about_info.SetName(i18n.t('i18n.helpTitle'))
            about_info.SetCopyright("(C) 2018 djdany01")
            about_info.SetDescription(i18n.t('i18n.helpDescription'))
            about_info.SetWebSite(
                "https://github.com/djdany01/NoMoreIntros/issues", "NoMoreIntros-Issues")

            wx.adv.AboutBox(about_info, self)
        elif (id == 7):
            about_info = wx.adv.AboutDialogInfo()
            about_info.SetName("NoMoreIntros")
            about_info.SetVersion(str(nmi_config.get_version()))
            about_info.SetDescription(i18n.t('i18n.aboutDescription'))
            about_info.SetCopyright("(C) 2018 djdany01")
            about_info.SetWebSite(
                "https://github.com/djdany01/NoMoreIntros", "NoMoreIntros-Github")

            wx.adv.AboutBox(about_info, self)

    # ----------------------------------------------------------------------
    def reload_app(self):
        """Reload the entire app closing it and creating a new instance with the new config"""
        pos = self.GetPosition()
        size = self.GetSize()
        self.Close()
        main(nmi_config.get_language(), nmi_config.get_theme(), pos, size)
        raise SystemExit

########################################################################


# ----------------------------------------------------------------------
def check_ffmpeg():
    """Checks before all if user has FFMPEG dependency, if not downloads it"""
    try:
        import nmi_video
    except Exception as e:
        dialog = wx.RichMessageDialog(self, i18n.t('i18n.ffmpegNotFound'), "Error", wx.ICON_ERROR)
        dialog.ShowDetailedText("Error info:\n" + "\\" + str(e) + "\\")
        dialog.ShowModal()
        if (os.path.isdir(os.getenv('LOCALAPPDATA')) is True):
            thread = multiprocessing.Process(target=nmi_utils.copy_ffmpeg)
        else:
            thread = multiprocessing.Process(target=ffmpeg.download)
        create_progress_dialog(thread, i18n.t('i18n.ffmpegProgressTitle'), i18n.t(
            'i18n.ffmpegProgressMsg'), i18n.t('i18n.ffmpegCancel'), i18n.t('i18n.ffmpegDownloaded'))


# ----------------------------------------------------------------------
def create_progress_dialog(thread, title, msg, error, ok):
    """
    Create a new progress Dialog with the given thread and messages passed for:
     Window title, Window message, Error message and ok message
    """
    thread.start()
    dialog = wx.ProgressDialog(
        title,
        msg,
        maximum=1, style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT)
    while thread.is_alive():
        dialog.Pulse()
        if (dialog.WasCancelled() is True):
            thread.terminate()
            dialog = wx.RichMessageDialog(self, error, "Error", wx.ICON_ERROR)
            dialog.ShowModal()
            return
    else:
        dialog.Update(1)
        wx.MessageBox(ok, "OK", wx.ICON_INFORMATION)


# ----------------------------------------------------------------------
def main(lang, theme, pos, size):
    """
    Main loop
    Sets i18n, check FFMPEG dependency and init the MainWindow
    """
    i18n.set('locale', lang)
    i18n.set('fallback', 'en')
    i18n.load_path.append('./lang/')
    app = wx.App(False)
    frame = MainFrame(lang, theme, pos, size)
    check_ffmpeg()
    app.MainLoop()


if (__name__ == "__main__"):
    multiprocessing.freeze_support()  # Needed to use multiprocessing with pyinstaller
    nmi_config.get_config()
    main(nmi_config.get_language(), nmi_config.get_theme(), (200, 200), (570, 400))
