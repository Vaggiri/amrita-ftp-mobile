import os
import threading
from ftplib import FTP

# --- 1. REMOVE RED DOTS ---
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.storage.jsonstore import JsonStore  # <--- FOR SAVING LOGIN

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
# Standard 1.2.0 Snackbar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.filemanager import MDFileManager

# --- KV LAYOUT ---
KV = '''
#:import hex kivy.utils.get_color_from_hex

<InputDialogContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "50dp"

    MDTextField:
        id: text_input
        hint_text: root.hint_text
        text: root.initial_text
        mode: "rectangle"

<FileCard>:
    orientation: "vertical"
    size_hint: None, None
    size: dp(100), dp(130)
    radius: [12]
    elevation: 1
    line_color: hex("#E2E8F0")
    md_bg_color: 1, 1, 1, 1
    on_release: root.on_click()
    padding: dp(8)
    spacing: dp(5)

    MDIcon:
        icon: root.icon
        halign: "center"
        font_size: dp(40)
        theme_text_color: "Custom"
        text_color: root.icon_color
        pos_hint: {"center_x": .5}
        size_hint_y: None
        height: dp(50)
    
    MDLabel:
        text: root.filename
        halign: "center"
        valign: "top"
        font_style: "Caption"
        bold: True
        shorten: True
        shorten_from: 'right'
        color: hex("#334155")
        size_hint_y: None
        height: dp(40)

# --- PIN SCREEN (New) ---
<PinScreen>:
    name: "pin"
    md_bg_color: hex("#F8FAFC")

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(20)
        pos_hint: {"center_y": .5}
        size_hint_y: None
        height: dp(500)

        MDIcon:
            icon: "lock"
            halign: "center"
            font_size: dp(48)
            theme_text_color: "Custom"
            text_color: hex("#2563EB")
        
        MDLabel:
            text: "Welcome Back"
            halign: "center"
            font_style: "H5"
            bold: True
            color: hex("#0F172A")
        
        MDLabel:
            id: user_label
            text: "User"
            halign: "center"
            font_style: "Subtitle1"
            color: hex("#64748B")

        # Dots to show PIN entry
        MDBoxLayout:
            id: dots_box
            orientation: "horizontal"
            size_hint: None, None
            size: self.minimum_size
            spacing: dp(15)
            pos_hint: {"center_x": .5}
            
            MDIcon:
                id: dot_1
                icon: "circle-outline"
                font_size: dp(15)
                color: hex("#94A3B8")
            MDIcon:
                id: dot_2
                icon: "circle-outline"
                font_size: dp(15)
                color: hex("#94A3B8")
            MDIcon:
                id: dot_3
                icon: "circle-outline"
                font_size: dp(15)
                color: hex("#94A3B8")
            MDIcon:
                id: dot_4
                icon: "circle-outline"
                font_size: dp(15)
                color: hex("#94A3B8")

        # Number Pad
        MDGridLayout:
            cols: 3
            spacing: dp(15)
            size_hint: None, None
            size: dp(240), dp(320)
            pos_hint: {"center_x": .5}
            
            PinButton:
                text: "1"
            PinButton:
                text: "2"
            PinButton:
                text: "3"
            PinButton:
                text: "4"
            PinButton:
                text: "5"
            PinButton:
                text: "6"
            PinButton:
                text: "7"
            PinButton:
                text: "8"
            PinButton:
                text: "9"
            
            MDIconButton:
                icon: "account-off"
                on_release: app.reset_login()
                theme_text_color: "Error"

            PinButton:
                text: "0"

            MDIconButton:
                icon: "backspace-outline"
                on_release: app.backspace_pin()

<PinButton@MDRaisedButton>:
    font_size: "24sp"
    size_hint: None, None
    size: dp(60), dp(60)
    elevation: 0
    md_bg_color: hex("#FFFFFF")
    text_color: hex("#0F172A")
    on_release: app.add_pin_digit(self.text)
    # Add border
    line_color: hex("#E2E8F0")
    line_width: 1

<LoginScreen>:
    name: "login"
    md_bg_color: hex("#F8FAFC")

    MDCard:
        size_hint: None, None
        size: dp(300), dp(380)
        pos_hint: {"center_x": .5, "center_y": .5}
        radius: [16]
        padding: dp(20)
        orientation: "vertical"
        spacing: dp(15)
        elevation: 2

        MDLabel:
            text: "Amrita FTP"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: hex("#0F172A")
            size_hint_y: None
            height: dp(30)
        
        MDLabel:
            text: "Workspace Login"
            halign: "center"
            font_style: "Caption"
            color: hex("#64748B")
            size_hint_y: None
            height: dp(20)

        MDTextField:
            id: user_field
            hint_text: "Roll Number"
            mode: "rectangle"
            icon_right: "account"
        
        MDTextField:
            id: pass_field
            hint_text: "Password"
            password: True
            mode: "rectangle"
            icon_right: "lock"

        MDRaisedButton:
            text: "CONNECT"
            pos_hint: {"center_x": .5}
            size_hint_x: 1
            md_bg_color: hex("#2563EB")
            on_release: app.login(user_field.text, pass_field.text)

        # HIGHLIGHTED DEVELOPER NAME
        MDLabel:
            text: "Designed by [b][color=#2563EB]Girisudhan V[/color][/b]\\n2nd Year ECE"
            markup: True
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: hex("#94A3B8")

<DashboardScreen>:
    name: "dashboard"
    md_bg_color: hex("#F8FAFC")

    MDBoxLayout:
        orientation: "vertical"

        # --- HEADER ---
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            md_bg_color: 1, 1, 1, 1
            padding: dp(15)
            spacing: dp(10)
            elevation: 1

            MDIcon:
                icon: "cloud"
                theme_text_color: "Custom"
                text_color: hex("#2563EB")
                size_hint_x: None
                width: dp(30)
            
            MDLabel:
                text: "Amrita Box"
                bold: True
                font_style: "H6"
                color: hex("#0F172A")

            MDCard:
                size_hint: None, None
                size: dp(100), dp(28)
                radius: [14]
                md_bg_color: hex("#EFF6FF")
                elevation: 0
                pos_hint: {"center_y": .5}
                padding: dp(5)
                
                MDLabel:
                    id: user_badge
                    text: "Guest"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: hex("#2563EB")
                    font_style: "Caption"
                    bold: True

        # --- TOOLBAR ---
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(10)
            spacing: dp(10)

            MDIconButton:
                id: back_btn
                icon: "chevron-left"
                on_release: app.nav_up()
                disabled: True
                opacity: 0 if self.disabled else 1
            
            MDLabel:
                id: breadcrumb
                text: "/ Root"
                font_style: "Subtitle2"
                color: hex("#64748B")

            MDIconButton:
                icon: "folder-plus"
                on_release: app.show_create_folder_dialog()

            MDIconButton:
                icon: "upload"
                on_release: app.open_file_manager()

            MDIconButton:
                icon: "refresh"
                on_release: app.refresh_list()

        # --- FILE AREA ---
        ScrollView:
            do_scroll_x: False
            MDGridLayout:
                id: file_grid
                cols: 3
                padding: dp(15)
                spacing: dp(15)
                adaptive_height: True
                row_default_height: dp(140)
                row_force_default: True

# --- ROOT WIDGET ---
ScreenManager:
    PinScreen:
    LoginScreen:
    DashboardScreen:
'''

# --- CUSTOM WIDGETS ---
class InputDialogContent(BoxLayout):
    hint_text = StringProperty()
    initial_text = StringProperty("")

class FileCard(MDCard):
    filename = StringProperty("Loading...")
    icon = StringProperty("file")
    icon_color = ListProperty([0.5, 0.5, 0.5, 1])
    is_dir = ObjectProperty(False)
    
    def on_click(self):
        app = MDApp.get_running_app()
        if self.is_dir:
            app.navigate(self.filename)
        else:
            app.show_file_options(self.filename)

class MDIconItem(OneLineIconListItem):
    def __init__(self, icon, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(IconLeftWidget(icon=icon))

class LoginScreen(MDScreen):
    pass

class DashboardScreen(MDScreen):
    pass

class PinScreen(MDScreen):
    pass

# --- MAIN APP LOGIC ---
class AmritaFTPApp(MDApp):
    ftp = None
    current_path = "/"
    dialog = None
    input_dialog = None
    store = None
    current_pin_input = ""
    
    # --- CONFIG ---
    HOST = "ftp.amritanet.edu"
    PORT = 21
    
    def build(self):
        Window.size = (360, 750) 
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.store = JsonStore('auth.json') # Local storage
        return Builder.load_string(KV)

    def on_start(self):
        from kivy.utils import platform
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        # 1. Setup File Manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path_upload,
        )
        
        # 2. Check for saved credentials
        if self.store.exists('auth'):
            data = self.store.get('auth')
            self.root.get_screen('pin').ids.user_label.text = data['user']
            self.root.current = "pin" # Go to PIN screen
        else:
            self.root.current = "login"

    # --- PIN LOGIC ---
    def add_pin_digit(self, digit):
        if len(self.current_pin_input) < 4:
            self.current_pin_input += digit
            self.update_pin_dots()
            
            if len(self.current_pin_input) == 4:
                self.verify_pin()

    def backspace_pin(self):
        self.current_pin_input = self.current_pin_input[:-1]
        self.update_pin_dots()

    def update_pin_dots(self):
        screen = self.root.get_screen('pin')
        for i in range(1, 5):
            icon = "circle" if len(self.current_pin_input) >= i else "circle-outline"
            color = [0.15, 0.39, 0.92, 1] if len(self.current_pin_input) >= i else [0.58, 0.64, 0.72, 1]
            dot = getattr(screen.ids, f"dot_{i}")
            dot.icon = icon
            dot.text_color = color
            dot.theme_text_color = "Custom"

    def verify_pin(self):
        if not self.store.exists('auth'):
            self.show_toast("Error: No saved data")
            self.reset_login()
            return
            
        data = self.store.get('auth')
        if self.current_pin_input == data['pin']:
            self.show_toast("Unlocking...")
            # Auto-login with saved creds
            self.login(data['user'], data['password'], is_auto=True)
        else:
            self.show_toast("Wrong PIN")
            self.current_pin_input = ""
            self.update_pin_dots()

    def reset_login(self):
        self.store.delete('auth') if self.store.exists('auth') else None
        self.current_pin_input = ""
        self.update_pin_dots()
        self.root.current = "login"

    # --- FTP LOGIC ---
    def login(self, user, password, is_auto=False):
        if not user or not password:
            self.show_toast("Enter Credentials")
            return

        def _connect():
            try:
                self.ftp = FTP()
                self.ftp.connect(self.HOST, self.PORT)
                self.ftp.login(user, password)
                Clock.schedule_once(lambda dt: self._post_login(user, password, is_auto))
            except Exception as e:
                err = str(e)
                # If auto-login fails, reset
                if is_auto: Clock.schedule_once(lambda dt: self.reset_login())
                Clock.schedule_once(lambda dt: self.show_toast(f"Error: {err}"))

        threading.Thread(target=_connect).start()

    def _post_login(self, user, password, is_auto):
        # If this was a manual login (not via PIN), ask to set PIN
        if not is_auto and not self.store.exists('auth'):
            self.show_pin_setup_dialog(user, password)
        
        self.root.current = "dashboard"
        self.root.get_screen('dashboard').ids.user_badge.text = user
        self.refresh_list()

    def show_pin_setup_dialog(self, user, password):
        self.input_content = InputDialogContent(hint_text="Create 4-digit PIN")
        # Force numeric keyboard logic would go here, simpler to trust user for now
        self.input_dialog = MDDialog(
            title="Setup Quick Login",
            type="custom",
            content_cls=self.input_content,
            buttons=[
                MDFlatButton(text="SKIP", on_release=lambda x: self.input_dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=lambda x: self.save_pin(user, password, self.input_content.ids.text_input.text)),
            ],
        )
        self.input_dialog.open()

    def save_pin(self, user, password, pin):
        if len(pin) != 4 or not pin.isdigit():
            self.show_toast("PIN must be 4 digits")
            return
        
        self.store.put('auth', user=user, password=password, pin=pin)
        self.input_dialog.dismiss()
        self.show_toast("PIN Saved!")

    def refresh_list(self):
        def _fetch():
            print("--- FETCHING FILES ---")
            try:
                self.ftp.cwd(self.current_path)
                
                raw_list = []
                self.ftp.retrlines('LIST', raw_list.append)
                
                parsed_items = []
                for line in raw_list:
                    # IMPROVED PARSING
                    parts = line.split()
                    name = ""
                    is_dir = False

                    # Windows Server Logic
                    if '<DIR>' in line:
                        is_dir = True
                        try:
                            dir_index = parts.index('<DIR>')
                            name = " ".join(parts[dir_index+1:])
                        except:
                            name = parts[-1]
                    
                    # Unix Server Logic
                    elif line[0] in ['d', '-']:
                        is_dir = line.startswith('d')
                        if len(parts) >= 9:
                            name = " ".join(parts[8:])
                        else:
                            name = parts[-1]

                    # Fallback
                    elif len(parts) > 3:
                         if "DIR" in line or line.startswith("d"): is_dir = True
                         name = " ".join(parts[3:])
                    else:
                        name = line

                    if name and name not in ['.', '..']:
                        parsed_items.append({'name': name.strip(), 'is_dir': is_dir})
                
                Clock.schedule_once(lambda dt: self.update_grid(parsed_items))
                
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt: self.show_toast(f"List Error: {err}"))

        threading.Thread(target=_fetch).start()

    def update_grid(self, items):
        grid = self.root.get_screen('dashboard').ids.file_grid
        grid.clear_widgets()
        
        items.sort(key=lambda x: (not x['is_dir'], x['name']))
        
        for item in items:
            name = item['name']
            is_dir = item['is_dir']
            
            icon = "folder" if is_dir else "file"
            color = [0.96, 0.62, 0.04, 1] if is_dir else [0.58, 0.64, 0.72, 1]
            
            if not is_dir:
                ext = name.split('.')[-1].lower()
                if ext == 'pdf': 
                    icon = "file-pdf-box"
                    color = [0.94, 0.27, 0.27, 1] 
                elif ext in ['jpg', 'png', 'jpeg']:
                    icon = "image"
                    color = [0.06, 0.73, 0.51, 1] 
                elif ext in ['c', 'py', 'js', 'html', 'css']:
                    icon = "code-braces"
                    color = [0.15, 0.39, 0.92, 1] 
                elif ext in ['zip', 'rar']:
                    icon = "zip-box"
                    color = [1, 0.5, 0, 1]

            card = FileCard()
            card.filename = name
            card.icon = icon
            card.icon_color = color
            card.is_dir = is_dir
            grid.add_widget(card)

    def navigate(self, folder_name):
        self.current_path = os.path.join(self.current_path, folder_name).replace("\\", "/")
        screen = self.root.get_screen('dashboard')
        screen.ids.breadcrumb.text = f".../{folder_name}"
        screen.ids.back_btn.disabled = False
        self.refresh_list()

    def nav_up(self):
        if self.current_path == "/": return
        self.current_path = os.path.dirname(self.current_path).replace("\\", "/")
        if self.current_path == "": self.current_path = "/"
        
        screen = self.root.get_screen('dashboard')
        display = "/ Root" if self.current_path == "/" else f".../{os.path.basename(self.current_path)}"
        screen.ids.breadcrumb.text = display
        
        if self.current_path == "/":
            screen.ids.back_btn.disabled = True
            
        self.refresh_list()

    # --- DIALOGS ---
    def show_file_options(self, filename):
        self.dialog = MDDialog(
            title=filename,
            type="simple",
            items=[
                MDIconItem(text="Download", icon="download", on_release=lambda x: self.download_file(filename)),
                MDIconItem(text="Rename", icon="pencil", on_release=lambda x: self.show_rename_dialog(filename)),
                MDIconItem(text="Delete", icon="trash-can", on_release=lambda x: self.delete_item(filename)),
            ],
        )
        self.dialog.open()

    def show_create_folder_dialog(self):
        self.input_content = InputDialogContent(hint_text="Folder Name")
        self.input_dialog = MDDialog(
            title="Create Folder",
            type="custom",
            content_cls=self.input_content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.input_dialog.dismiss()),
                MDRaisedButton(text="CREATE", on_release=lambda x: self.do_create_folder(self.input_content.ids.text_input.text)),
            ],
        )
        self.input_dialog.open()

    def do_create_folder(self, folder_name):
        if not folder_name: return
        self.input_dialog.dismiss()
        def _mkd():
            try:
                self.ftp.mkd(folder_name)
                Clock.schedule_once(lambda dt: self.refresh_list())
                Clock.schedule_once(lambda dt: self.show_toast("Folder Created"))
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt: self.show_toast(f"Error: {err}"))
        threading.Thread(target=_mkd).start()

    def show_rename_dialog(self, old_name):
        if self.dialog: self.dialog.dismiss()
        self.input_content = InputDialogContent(hint_text="New Name", initial_text=old_name)
        self.input_dialog = MDDialog(
            title="Rename File",
            type="custom",
            content_cls=self.input_content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.input_dialog.dismiss()),
                MDRaisedButton(text="RENAME", on_release=lambda x: self.do_rename(old_name, self.input_content.ids.text_input.text)),
            ],
        )
        self.input_dialog.open()

    def do_rename(self, old_name, new_name):
        if not new_name or new_name == old_name: return
        self.input_dialog.dismiss()
        def _ren():
            try:
                self.ftp.rename(old_name, new_name)
                Clock.schedule_once(lambda dt: self.refresh_list())
                Clock.schedule_once(lambda dt: self.show_toast("Renamed"))
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt: self.show_toast(f"Error: {err}"))
        threading.Thread(target=_ren).start()

    # --- OPERATIONS ---
    def download_file(self, filename):
        if self.dialog: self.dialog.dismiss()
        def _dl():
            try:
                local_path = filename if os.name == 'nt' else f"/storage/emulated/0/Download/{filename}"
                with open(local_path, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {filename}", f.write)
                Clock.schedule_once(lambda dt: self.show_toast("Download Complete"))
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt: self.show_toast(f"DL Failed: {err}"))
        self.show_toast("Downloading...")
        threading.Thread(target=_dl).start()

    def delete_item(self, filename):
        if self.dialog: self.dialog.dismiss()
        def _del():
            try:
                self.ftp.delete(filename)
                Clock.schedule_once(lambda dt: self.refresh_list())
                Clock.schedule_once(lambda dt: self.show_toast("Deleted"))
            except:
                try:
                    self.ftp.rmd(filename)
                    Clock.schedule_once(lambda dt: self.refresh_list())
                except Exception as e:
                    err = str(e)
                    Clock.schedule_once(lambda dt: self.show_toast(f"Error: {err}"))
        threading.Thread(target=_del).start()

    # --- UTILS ---
    def show_toast(self, text):
        print(f"TOAST: {text}")
        try:
            # FIX: KivyMD 1.2.0 compatibility
            snackbar = Snackbar(
                bg_color=[0.2, 0.2, 0.2, 1],
                size_hint_x=0.9,
                pos_hint={'center_x': 0.5, 'y': 0.05},
                padding="20dp"
            )
            label = MDLabel(
                text=text,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
                shorten=True,
                shorten_from='right',
            )
            snackbar.add_widget(label)
            snackbar.open()
        except Exception as e:
            print(f"Snackbar Error: {e}")
        
    def open_file_manager(self):
        path = os.path.expanduser("~")
        self.file_manager.show(path)
    
    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path_upload(self, path):
        self.exit_manager()
        filename = os.path.basename(path)
        def _up():
            try:
                with open(path, 'rb') as f:
                    self.ftp.storbinary(f"STOR {filename}", f)
                Clock.schedule_once(lambda dt: self.refresh_list())
                Clock.schedule_once(lambda dt: self.show_toast("Uploaded"))
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt: self.show_toast(f"Upload Failed: {err}"))
        self.show_toast("Uploading...")
        threading.Thread(target=_up).start()

if __name__ == "__main__":
    AmritaFTPApp().run()
