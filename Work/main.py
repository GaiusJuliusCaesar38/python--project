import tkinter as tk
from tkinter import ttk
import Library.report as report
import Library.parsing as parsing
import Library.database as database

class ReportWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__()
        self.title("Отчет")
        self.length = tk.StringVar()
        self.root = root
        self.initUI()

    def initUI(self):
        self.datetime_frame = tk.Frame(self)
    
        self.date1_frame = tk.Frame(self.datetime_frame)
        self.date1_label = tk.Label(self.date1_frame, text = "Начало 1 периода: ")
        self.date1_label.pack(side='left', padx=5)
        self.date1_cal = tk.Entry(self.date1_frame)
        self.date1_cal.pack(side='left', padx=5)
        self.date1_frame.pack(side='top', pady=5)
    
        self.date2_frame = tk.Frame(self.datetime_frame)
        self.date2_label = tk.Label(self.date2_frame, text = "Начало 2 периода: ")
        self.date2_label.pack(side='left', padx=5)
        self.date2_cal = tk.Entry(self.date2_frame)
        self.date2_cal.pack(side='left', padx=5)
        self.date2_frame.pack(side='top', pady=5)

        self.datetime_frame.pack(side='top')
        
        self.length_frame = tk.Frame(self)
        self.length_label = tk.Label(self.length_frame, text = "Длительность: ")
        self.length_label.pack(side='left', padx=5)
        self.length_entry = tk.Entry(self.length_frame, textvariable=self.length)
        self.length_entry.pack(side='left', padx=5)
        self.length_frame.pack(side='top', pady=5)

        self.apply_button = tk.Button(self, text="Отчет", command=self.report)
        self.apply_button.pack(side='top', pady=5)

    def report(self):
        length = self.length.get()
        date1 = self.date1_cal.get()
        date2 = self.date2_cal.get()
        
        if length and length.isdigit():
            length = int(length)
            records1 = self.root.db.get_interval(date1, length)
            records2 = self.root.db.get_interval(date2, length)
            count1 = [0 for i in range(len(parsing.types.keys()))]
            count2 = [0 for i in range(len(parsing.types.keys()))]
            for i in records1:
                count1[list(parsing.types.keys()).index(i[3])] += 1
            for i in records2:
                count2[list(parsing.types.keys()).index(i[3])] += 1
        report.create_report(count1, count2)

class UpdateWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__()
        self.title("Обновить")
        self.root = root
        self.types_vars = [tk.IntVar() for i in parsing.types.keys()]
        self.initUI()

    def initUI(self):
        types = list(parsing.types.keys())
        self.mode_frame = tk.Frame(self)
        self.mode_label = tk.Label(self.mode_frame, text="Режим:")
        self.mode_combobox = ttk.Combobox(self.mode_frame,
                                          values = ["Все",                                                  "",
                                                    "Выборочно",
                                                    "Актуализация"],
                                          width=20)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.updateUI)
        self.mode_combobox.pack(side='right', padx=10, pady=10)
        self.mode_label.pack(side='left', padx=10, pady=10)
        self.mode_frame.pack(side='top', padx=10, pady=10)
        
        self.datetime_frame = tk.Frame(self)
        self.date_from_label = tk.Label(self.datetime_frame, text = "С: ")
        self.date_from_label.pack(side='left', padx=5)
        self.date_from_cal = tk.Entry(self.datetime_frame)
        self.date_from_cal.pack(side='left', padx=5)
        self.date_to_label = tk.Label(self.datetime_frame, text = "До: ")
        self.date_to_label.pack(side='left', padx=5)
        self.date_to_cal = tk.Entry(self.datetime_frame)
        self.date_to_cal.pack(side='left', padx=5)

        self.select_mode_frame = tk.Frame(self)
        self.checkbuttons = []
        for n, i in enumerate(parsing.types.items()):
            cb = tk.Checkbutton(self.select_mode_frame,
                                text=i[0],
                                variable=self.types_vars[n],
                                onvalue=i[1],
                                offvalue=0)
            self.checkbuttons.append(cb)
        for i in self.checkbuttons:
            i.pack(side='top', anchor='w')

        self.apply_button = tk.Button(self,
                                      text="Обновить",
                                      command=self.update)
        self.apply_button.pack(side='bottom', pady=10)

        
    def update(self):
        p = parsing.Parser()
        mode = self.mode_combobox.get()
        if mode:
            if mode == "Все":
                for i in p.get_all_news():
                    self.root.db.add_record(*i)
            else:
                date_from = self.date_from_cal.get()
                date_to = self.date_to_cal.get()
                if mode == "Актуализация":
                    for i in p.get_news(date_from, date_to):
                        self.root.db.add_record(*i)
                elif mode == "Выборочно":
                    types = []
                    for i in self.types_vars:
                        if i.get():
                            types.append(i.get())
                    for i in p.get_news(date_from, date_to, types):
                        self.root.db.add_record(*i)
        p.close()
        self.root.updateUI()
        self.destroy()
        

    def updateUI(self, e):
        mode = self.mode_combobox.get()
        if self.select_mode_frame.winfo_ismapped() and (mode != "Выборочно" or not mode):
            self.select_mode_frame.pack_forget()
        if self.datetime_frame.winfo_ismapped() and (mode == "Все" or not mode):
            self.datetime_frame.pack_forget()

        if mode:
            if mode != "Все":
                self.datetime_frame.pack(side='top', padx=5, pady=5)
            if mode == "Выборочно":
                self.select_mode_frame.pack(side='top', padx=5, pady=5)

        


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = database.Database()
        self.title("Сводка МЧС")
        self.geometry('800x600')
        self.initUI()
        self.updateUI()
        self.mainloop()

    def initUI(self):
        self.items_frame = ttk.Frame(self)
        
        self.scroll_canvas = tk.Canvas(self.items_frame)
        self.scroll_frame = tk.Frame(self.scroll_canvas)
        self.scroll = tk.Scrollbar(self.items_frame,
                                   orient = 'vertical',
                                   command = self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand = self.scroll.set)
        self.scroll.pack(side = 'right', fill = 'y')
        self.scroll_canvas.pack(side = 'left')
        self.scroll_canvas.create_window((0, 0),
                                         window = self.scroll_frame,
                                         anchor = 'nw')
        
        self.scroll_frame.bind('<Configure>',
                   lambda e: self.scroll_canvas.configure(scrollregion = self.scroll_canvas.bbox('all')))

        self.items_frame.pack(fill='both', expand=1)        
        self.scroll_canvas.pack(side='left', fill='both', expand=True)
        self.scroll.pack(side='right', fill='y')

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        self.update_button = tk.Button(self.buttons_frame, text="Обновить")
        self.update_button['command'] = self.open_update
        self.update_button.pack(side='right', padx=5, pady=5)
    
        self.report_button = tk.Button(self.buttons_frame, text="Отчет")
        self.report_button['command'] = self.open_report
        self.report_button.pack(side='left', padx=5, pady=5)

    def open_update(self):
        uw = UpdateWindow(self)
        uw.wait_visibility()
        uw.grab_set()
        
    def open_report(self):
        rw = ReportWindow(self)
        rw.wait_visibility()
        rw.grab_set()

    def report(self):
        pass

    def updateUI(self):
        records = self.db.get_all()
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        for r in records:
            f = tk.Frame(self.scroll_frame,
                         highlightthickness=1,
                         highlightbackground="black"
                         )
            tk.Label(f, text=r[1], font='Arial 10 bold').pack(side='top', anchor='w')
            tk.Label(f, text=r[2], font='Arial 9').pack(side='top', anchor='w')
            tk.Label(f, text=r[3], font='Arial 9').pack(side='top', anchor='w')
            tk.Label(f, text=r[4], font='Arial 9').pack(side='top', anchor='w')
            f.pack(side='top', anchor='w', fill='x')
        


def main():
    app = App()

if __name__ == '__main__':
    main()