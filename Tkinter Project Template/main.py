import tkinter as tk
from tkinter import ttk


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.title("Simple App")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        
        frame = InputForm(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        frame2 = InputForm(self)
        frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)


class InputForm(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=0, sticky="ew")

        self.entry.bind("<Return>", self.add_to_list)

        self.entry_btn = tk.Button(self, text="Add", command=self.add_to_list)
        #self.entry_btn.grid(row=0, column=1)

        self.entry_btn2 = tk.Button(self, text="Clear", command=self.clear_list)
        #self.entry_btn2.grid(row=0, column=2)

        self.text_list = tk.Listbox(self)
        #self.text_list.grid(row=1, column=0,  sticky="nsew")
        
        
        arrangement = [
            [self.entry           , self.entry_btn       , self.entry_btn2 ],
            [self.text_list       , None                 , None            ],
            [None                 , None                 , None            ],     
        ]
        
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):
                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                    
                    if isinstance(arrangement[ind_y][ind_x], tk.Entry):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "EW")
                    elif isinstance(arrangement[ind_y][ind_x], tk.Listbox):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, columnspan=3, sticky = "NSEW")
                    else:
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x)
        

    def add_to_list(self, _event=None):
        text = self.entry.get()
        if text:
            self.text_list.insert(tk.END, text)
            self.entry.delete(0, tk.END)

    def clear_list(self):
        self.text_list.delete(0, tk.END)


if __name__ == "__main__":
    app = Application()
    app.geometry("300x400")
    app.mainloop()