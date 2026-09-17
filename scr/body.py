import sys
import plyer
import os.path
import threading
import pystray
import pandas as pd
from ctypes import windll

import customtkinter as ctk
import queue
import tkinter as tk

from PIL import Image
from CTkMenuBar import CustomDropdownMenu
from tkinter import filedialog, END

from scr.aggregato import AggregatoMainLogic
from scr.database_assets.sqlite_database.handling_database.handler_sqlite_database_program import \
    ReceiverDataBase as ProgramDatabase
from scr.config_assets.handling_config.handler_aggregato_config import ConfigAggregato


def info_database():
    sqlite_database_program = ProgramDatabase()
    print(sqlite_database_program.get_program_data('Aggregato'))


def open_fils_to_path(name: str) -> list:
    filepaths = filedialog.askopenfilenames(
        title=f"Выберите Excel файл для {name}",
        filetypes=(("Excel files", "*.xlsx *.xls *.xlsm"), ("All files", "*.*"))
    )
    if not filepaths:
        return []
    return list(filepaths)


def send_notification(title, message, settime=15):
    plyer.notification.notify(title=title, message=message, app_name="Aggregato", timeout=settime,
                              app_icon=resource_path(r"static/img/ico/aggregato.ico"))


def resource_path(relative_path):
    def refactor_path(refactored_path):
        if hasattr(sys, '_MEIPASS'):
            # noinspection PyProtectedMember
            base_path = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(current_dir)

        return os.path.normpath(os.path.join(base_path, refactored_path))

    try:
        from PIL import Image
        name_without_ext, ext = os.path.splitext(os.path.basename(relative_path))
        source_png = refactor_path(os.path.join(os.path.normpath("static/img/png/"), f'{name_without_ext}.png'))

        img = Image.open(source_png)

        icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
        img.save(refactor_path(f"static/img/ico/{os.path.basename(relative_path)}"), sizes=icon_sizes)
        relative_path = refactor_path(f"static/img/ico/{os.path.basename(relative_path)}")
    except:
        print("Не удалось создать иконку")
    return refactor_path(relative_path)


class AppGui(ctk.CTk):
    def __init__(self):
        self.geomitri_constants()

        super().__init__()

        self.title("Aggregato")
        self.geometry(f"{self.window_main_x}x{self.window_main_y}")
        ctk.set_appearance_mode("dark")
        self.overrideredirect(True)
        self.after(10, self.set_appwindow())

        self.iconbitmap(resource_path(r"static/img/ico/aggregato.ico"))

        self.config_aggregato = ConfigAggregato()

        self.drop_down_menu()
        self.management_window()

        self.path_outfile = None

        self.log_queue = queue.Queue()
        self.table_queue = queue.Queue()

        self.check_log_queue()

    def set_appwindow(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = windll.user32.GetParent(self.winfo_id())

        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW

        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())

    def drop_down_menu(self):
        self.size_global_menu_program = 50
        self.size_menu_program = 20
        menu_frame = ctk.CTkFrame(
            self
            , width=self.window_main_x
            , height=self.height_row_in_frame
            , fg_color='#2b2b2b'
            , corner_radius=0
        )
        menu_frame.place(x=0, y=0)

        def minimize_window():
            """Сворачивает в трей вместо панели задач"""
            self.withdraw()

            # noinspection PyShadowingNames
            def show_window(icon):
                self.deiconify()
                icon.stop()

            image = Image.open(resource_path(r"static/img/ico/aggregato.ico"))
            menu = pystray.Menu(pystray.MenuItem("Развернуть", show_window))
            icon = pystray.Icon("BamManager", image, "Bam Manager", menu)

            threading.Thread(target=icon.run, daemon=True).start()

        img = Image.open(resource_path(r"static/img/ico/aggregato.ico"))

        ctk_icon = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(self.height_row_in_frame, self.height_row_in_frame)
        )

        self.button_ico_from_global_menu = ctk.CTkButton(
            menu_frame,
            text="",
            width=self.size_global_menu_program - self.size_menu_program,
            height=self.size_global_menu_program - self.size_menu_program,
            corner_radius=0,
            border_spacing=0,
            image=ctk_icon,
            fg_color="#000000",
            hover_color="#000000"
        )
        self.button_ico_from_global_menu.place(x=0, y=0)

        """Кнопки обработки окна"""
        button_exit = ctk.CTkButton(
            menu_frame,
            width=self.width_button_menu_frame,
            text='⨉',
            height=self.height_row_in_frame,
            corner_radius=0,
            fg_color="#2b2b2b",
            hover_color="red",
            command=lambda: [self.destroy(), sys.exit(0)]
        )
        button_exit.place(x=self.window_main_x - self.width_button_menu_frame, y=0)
        button_change_size = ctk.CTkButton(
            menu_frame,
            width=self.width_button_menu_frame,
            text='▢',
            height=self.height_row_in_frame,
            corner_radius=0,
            fg_color="#2b2b2b",
            hover_color="#414141"
        )
        button_change_size.place(x=self.window_main_x - self.width_button_menu_frame * 2, y=0)
        button_close = ctk.CTkButton(
            menu_frame,
            width=self.width_button_menu_frame,
            text='—',
            height=self.height_row_in_frame,
            corner_radius=0,
            fg_color="#2b2b2b",
            hover_color="#414141",
            command=minimize_window
        )
        button_close.place(x=self.window_main_x - self.width_button_menu_frame * 3, y=0)

        def do_something(action):
            print(f"Выполнено действие: {action}")

        """Меню бар"""
        menu_button = ctk.CTkButton(
            self
            , text="Меню"
            , width=self.width_button_menu_frame
            , height=self.height_row_in_frame
            , corner_radius=0
            , fg_color='#2b2b2b'
            , hover_color='#414141'
        )
        menu_button.place(x=self.width_button_menu_frame, y=0)
        dropdown = CustomDropdownMenu(widget=menu_button)

        dropdown.add_option(option="Создать новый файл", command=lambda: do_something("Новый файл"))
        dropdown.add_option(option="Открыть...", command=lambda: do_something("Открыть"))

        dropdown.add_separator()

        submenu = dropdown.add_submenu("Настройки конфига")
        submenu.add_option(option="Настроить", command=self._run_configuration_settings)
        submenu.add_option(option="Open in explorer",
                           command=lambda: os.startfile(self.config_aggregato.path_to_config))

        # dropdown.add_option(option="Выход", command=self.quit)

    # noinspection PyAttributeOutsideInit
    def geomitri_constants(self):
        self.window_main_x = 700
        self.window_main_y = 420

        """ indent's """
        self.indent_self = 15
        self.indent_frame = 5

        """ menu frame """
        self.width_button_menu_frame = 36

        """ main frame """
        self.position_main_frame_x = 0
        self.position_main_frame_y = 30
        self.height_main_frame = 80
        self.height_row_in_frame = 30

        self.width_path_entry = 435
        self.width_name_entry = 149

        self.width_open_button = 50

        """selection button frame"""
        self.width_selection_frame = 120
        # self.height_selection_frame = 2 * self.height_row_in_frame + 1 * self.indent_frame
        self.height_selection_frame = self.window_main_y - 3 * self.indent_self - self.height_main_frame - self.position_main_frame_y

        self.location_x_selection_frame = self.indent_self
        self.location_y_selection_frame = self.position_main_frame_y + self.height_main_frame + 2 * self.indent_self

        """log frame"""
        self.width_log_frame = self.window_main_x - 3 * self.indent_self - self.width_selection_frame
        self.height_log_frame = self.window_main_y - 3 * self.indent_self - self.height_main_frame - self.position_main_frame_y

        self.location_x_log_frame = self.width_selection_frame + 2 * self.indent_self
        self.location_y_log_frame = self.position_main_frame_y + self.height_main_frame + 2 * self.indent_self

        self.width_status_text = self.width_log_frame - 2 * self.indent_frame
        self.height_status_text = self.height_log_frame - 2 * self.indent_frame

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        if self.y <= self.size_global_menu_program - self.size_menu_program:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

    # noinspection PyAttributeOutsideInit
    def management_window(self):
        """Функция отрисовки gui"""
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        """ main frame """
        main_frame = ctk.CTkFrame(
            self
            , width=self.window_main_x - 2 * self.indent_self
            , height=self.height_main_frame
        )
        main_frame.place(
            x=self.position_main_frame_x + self.indent_self,
            y=self.position_main_frame_y + self.indent_self
        )

        self.reply_name_entry = ctk.CTkEntry(
            main_frame
            , width=self.width_name_entry
            , height=self.height_row_in_frame
            , corner_radius=4
            , placeholder_text='Имя файла'
            , state='readonly'
            , border_color='#788084'
        )
        self.reply_name_entry.place(x=5, y=5)
        self.reply_name_entry.configure(text_color='#9aa5aa', state='normal')
        self.reply_name_entry.delete(0, END)
        self.reply_name_entry.insert(0, 'Файл')
        self.reply_name_entry.configure(state='readonly')

        self.reply_path_entry = ctk.CTkEntry(
            main_frame
            , width=self.width_path_entry
            , height=self.height_row_in_frame
            , corner_radius=4
            , placeholder_text='Введите путь к файлу/файлам'
            , border_color='#788084'
        )
        self.reply_path_entry.place(
            x=self.width_name_entry + 2 * self.indent_frame
            , y=5
        )

        self.button_open_folder_reply = ctk.CTkButton(
            main_frame
            , text='Открыть'
            , width=self.width_open_button
            , height=self.height_row_in_frame
            , command=lambda: self.button_path_commands(label_batton='reply')
            , fg_color="#343638"
            , hover_color="#9aa5aa"
        )
        self.button_open_folder_reply.place(
            x=self.width_name_entry + self.width_path_entry + 3 * self.indent_frame,
            y=self.indent_frame
        )

        self.start_button = ctk.CTkButton(
            main_frame
            , width=72
            , height=self.height_row_in_frame
            , text="Начать"
            , fg_color="green"
            , hover_color="darkgreen"
            , command=self.run_manager_thread
        )
        self.start_button.place(
            x=self.width_name_entry + self.width_path_entry + 9
            , y=self.height_row_in_frame + 2 * self.indent_frame + 1
        )

        self.button_open_result_table = ctk.CTkButton(
            main_frame
            , width=100
            , height=self.height_row_in_frame
            , text="Открыть результат"
            , command=self.command_batton_open_result
            , fg_color='#b69765'
            , hover_color='#8f764f'
        )

        """selection button frame"""
        selection_frame = ctk.CTkFrame(
            self
            , width=self.width_selection_frame
            , height=self.height_selection_frame
        )
        selection_frame.place(
            x=self.location_x_selection_frame
            , y=self.location_y_selection_frame
        )

        self.checkbox_pivot_var = ctk.CTkCheckBox(
            selection_frame
            , checkbox_width=15
            , checkbox_height=15
            , border_width=1
            , text='Pivot fusion'
            , command=self.swith_main_frame
        )
        self.checkbox_pivot_var.place(
            x=self.indent_frame
            , y=self.indent_frame
        )
        self.checkbox_pivot_var.select()

        self.checkbox_construction_result_var = ctk.CTkCheckBox(
            selection_frame
            , checkbox_width=15
            , checkbox_height=15
            , border_width=1
            , text='Constr. result'
            , command=self.swith_main_frame
        )
        self.checkbox_construction_result_var.place(
            x=self.indent_frame
            , y=self.height_row_in_frame + 1 * self.indent_frame
        )
        self.checkbox_construction_result_var.select()

        """log frame"""
        logs_frame = ctk.CTkFrame(
            self
            , width=self.width_log_frame
            , height=self.height_log_frame
        )
        logs_frame.place(
            x=self.location_x_log_frame
            , y=self.location_y_log_frame
        )

        self.status_text = ctk.CTkTextbox(
            logs_frame
            , width=self.width_status_text
            , height=self.height_status_text
        )
        self.status_text.place(
            x=self.indent_frame,
            y=self.indent_frame
        )
        self.status_text.insert("0.0", "Готов к запуску...\n")

    def swith_main_frame(self):
        if not self.checkbox_pivot_var.get() and self.checkbox_construction_result_var.get():
            print('-->', end=' ')
        else:
            pass
        print(self.checkbox_pivot_var.get())

    def command_batton_open_result(self):
        if not self.path_outfile is None:
            self.start_button.configure(state="disabled")
            self.button_open_result_table.configure(fg_color='green', hover_color='darkgreen')

            def merge_color():
                self.button_open_result_table.configure(fg_color='#8f764f', hover_color='#5c4b32')

            # noinspection PyTypeChecker
            self.button_open_result_table.after(1000, merge_color)

            try:
                os.startfile(self.path_outfile)
                self.log("-Файл открыт", color_log="#788084")
            except Exception as e:
                self.log(f"Ошибка при открытии файла: {e}", color_log="red")
                self.start_button.configure(state="normal")
                return

            try:
                send_notification(f"Файл открыт: {os.path.basename(self.path_outfile).replace('.xlsx', '')}",
                                  "", 16)
            except:
                send_notification(f"Файл открыт: {os.path.basename(self.path_outfile)}", "", 16)

            # noinspection PyTypeChecker
            self.button_open_result_table.after(5000, self.start_button.configure(state="normal"))
        else:
            self.log("Ошибка при открытии файла, отсссуствует путь", color_log="red")
            self.button_open_result_table.place_forget()

    def button_path_commands(self, label_batton: str):
        if label_batton == 'reply':
            path_list_filr = list(open_fils_to_path(name='отчета'))
            if pd.isna(path_list_filr) or path_list_filr == []: return

            str_paths = ""
            for path in path_list_filr: str_paths += f"{path}, "
            str_paths = str_paths[:-2]

            self.reply_path_entry.delete(0, END)
            self.reply_path_entry.insert(0, str_paths)

            self.reply_name_entry.configure(text_color='#fff', state='normal')
            self.reply_name_entry.delete(0, END)
            self.reply_name_entry.insert(0, os.path.basename(str_paths))
            self.reply_name_entry.configure(state='readonly')

            self.start_button.configure(state="normal")
            self.log(f"<Установлен путь для файла отчетов>", color_log='#9aa5aa')
            self.reply_path_entry.configure(border_color='#788084')

    def table_callback(self, row_data):
        """Колбэк для передачи данных из фонового потока в очередь"""
        self.table_queue.put(row_data)

    def check_log_queue(self):
        """Проверяет очередь логов и выводит в GUI"""
        try:
            while True:
                message, color_log, line_target, mode = self.log_queue.get_nowait()
                self._log_to_gui(message, color_log, line_target, mode)
        except queue.Empty:
            pass
        finally:
            # noinspection PyTypeChecker
            self.after(50, self.check_log_queue)

    def _log_to_gui(self, message, color_log=None, line_target=None, mode='append'):
        if line_target is not None:
            line_pos = f"{line_target}.0"
            line_end = f"{line_target}.end"

            try:
                self.status_text.index(line_end)
            except tk.TclError:
                current_lines = int(self.status_text.index('end-1c').split('.')[0])
                for _ in range(line_target - current_lines + 1):
                    self.status_text.insert("end", "\n")

            if mode == 'replace':
                self.status_text.delete(line_pos, line_end)
                self.status_text.insert(line_pos, message)
            else:
                line_content = self.status_text.get(line_pos, line_end)
                if line_content.endswith('\n'):
                    insert_pos = f"{line_target}.{len(line_content) - 1}"
                else:
                    insert_pos = line_end
                self.status_text.insert(insert_pos, message)

            if color_log:
                tag_name = f"color_{color_log}_{line_target}"
                self.status_text.tag_config(tag_name, foreground=color_log)
                self.status_text.tag_add(tag_name, line_pos, line_end)
        else:
            self.status_text.insert("end", f"{message}\n")

            if color_log:
                end_index = self.status_text.index("end-1c")
                line_num = end_index.split('.')[0]
                start_pos = f"{int(line_num) - 1}.0"
                end_pos = f"{int(line_num) - 1}.end"
                tag_name = f"color_{color_log}"
                self.status_text.tag_config(tag_name, foreground=color_log)
                self.status_text.tag_add(tag_name, start_pos, end_pos)

        self.status_text.see("end")

    def log(self, message, color_log=None, line_target=None, mode='append'):
        """Потокобезопасный лог: кладет сообщение в очередь, чтобы GUI не зависал"""
        self.log_queue.put((message, color_log, line_target, mode))

    def run_manager_thread(self):
        """Запуск в отдельном потоке, чтобы GUI не зависал"""
        self.button_open_result_table.place_forget()
        self.start_button.configure(state="disabled")

        if (
                pd.isna(
                    self.reply_path_entry.get()) or self.reply_path_entry.get() == '') and not self.checkbox_pivot_var.get() and self.checkbox_construction_result_var.get():
            self.log("Ошибка, укажите путь к файлу", color_log="red")
            self.start_button.configure(state="normal")

            self.log("Введите путь к файлу", color_log='red')
            self.reply_path_entry.configure(border_color="red")
            self.start_button.configure(state="normal")
            return

        thread = threading.Thread(target=self.execute_logic, daemon=True)
        thread.start()

    def execute_logic(self):
        self.path_outfile = None

        self.log("Запуск программы...")

        self.path_outfile = None
        manager = AggregatoMainLogic(log_callback=self.log)

        manager.main(
            path_to_file=self.reply_path_entry.get()
            , run_pivot_fusion=bool(self.checkbox_pivot_var.get())
            , run_construction_result=bool(self.checkbox_construction_result_var.get())
        )
        self.path_outfile = self.reply_path_entry.get()

        self.button_open_result_table.place(
            x=self.width_path_entry + 22
            , y=self.height_row_in_frame + 2 * self.indent_frame + 1
        )
        self.log("Процесс успешно завершен.", color_log="green")
        send_notification("Программа завершена", "Программа завершена, проверте файл", 16)
        self.start_button.configure(state="normal")

    @staticmethod
    def _run_configuration_settings():
        _ConfigurationSettingsWindow()


class _ConfigurationSettingsWindow(ctk.CTkToplevel):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None or not cls._instance.winfo_exists():
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            self.lift()
            self.focus_force()

        super().__init__()
        self._initialized = True

        self.geomitri_constants()

        self.title("Configuration settings window")
        self.geometry(f"{self.width_window}x{self.height_window}")
        ctk.set_appearance_mode("dark")
        self.iconbitmap(resource_path(r"static/img/ico/aggregato.ico"))

        self.config_aggregato = ConfigAggregato()

        self.management_window()

    # noinspection PyAttributeOutsideInit
    def geomitri_constants(self):
        """Функция определения констант"""
        self.width_window = 900
        self.height_window = 300

        self.row_height = 30

        """ indent's """
        self.indent_self = 15
        self.indent_frame = 5

        """main frame"""
        self.width_main_frame = self.width_window - 2 * self.indent_self
        self.height_main_frame = self.height_window - 2 * self.indent_self

    # noinspection PyAttributeOutsideInit
    def management_window(self):
        """Функция отрисовки gui"""
        main_frame = ctk.CTkFrame(
            self
            , width=self.width_main_frame
            , height=self.height_main_frame
        )
        main_frame.place(
            x=self.indent_self
            , y=self.indent_self
        )

        dict_designation_row_config = {
            'link to directory reports': 'Путь к директории с  отчетами по УП БАМ'
            , 'name bam report tabel': 'Название файлов отчетов (не и не полные названия)'
            , 'name work central': 'Имена листов с рц в отчетах'
            , 'name dse': 'Доп. обозначение колонки дсе'
            , 'name directory database save reports': 'Директория для сохранения базы данных отчетов'
            , 'path to directory database save reports': 'Путь к директории базы данных'
        }

        width_label = max(len(text) for text in dict_designation_row_config.values()) + 2 * self.indent_frame

        label_keys = [
            'link to directory reports',
            'name bam report tabel',
            'name work central',
            'name dse',
            'name directory database save reports',
            'path to directory database save reports'
        ]

        self.labels = {}

        for row, key in enumerate(label_keys):
            label = ctk.CTkLabel(
                main_frame
                , width=width_label
                , height=self.row_height
                , text=dict_designation_row_config.get(key, '')
            )
            label.grid(row=row, column=0)

            entry = ctk.CTkEntry(
                main_frame
                , width=532
                , height=self.row_height
            )
            entry.insert(0, self.config_aggregato.get_all_config_program().get(key, ''))
            entry.grid(row=row, column=1, padx=self.indent_frame, pady=self.indent_frame)

            self.labels[key] = [label, entry]

        button_save = ctk.CTkButton(
            self
            , width=40
            , height=30
            , text='save'
            , fg_color='green'
            , hover_color='darkgreen'
            , command=self.save_param
        )
        button_save.place(x=15, y=self.height_window - 40)

    def save_param(self):
        for key, label_ in self.labels.items():
            print(key, self.labels[key][1].get())
            self.config_aggregato.set_config_progrm(key=key, data=self.labels[key][1].get())
        self.destroy()
        # sys.exit(0)


# class _ConfigurationSettingsWindow(ctk.CTkToplevel):


#     _instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None or not cls._instance.winfo_exists():
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(self, parent=None, main_window_geomitri_constants=None):
#         if getattr(self, "_initialized", False):
#             self.lift()
#             self.focus_force()
#
#         super().__init__()
#         self._initialized = True  # Помечаем, что инициализация прошла
#
#         self.title("Configuration settings window")
#         self.geometry(f"500x300")
#         ctk.set_appearance_mode("dark")
#         self.iconbitmap(resource_path(r"static/img/ico/aggregato.ico"))


if __name__ == "__main__":
    app = AppGui()
    # _ConfigurationSettingsWindow().mainloop()
    app.mainloop()
