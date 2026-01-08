def hide_widget(widget):
    widget.grid_remove()
        
def show_widget(widget):
    widget.grid()

def hide_pack_widget(widget):
    widget.pack_forget()

def show_pack_widget(widget):
    widget.pack()

def disable_widget(widget):
    widget.config(state="disabled")

def enable_widget(widget):
    widget.config(state="normal")

def delete_widget(widget):
    widget.destroy()

def arrange_widgets(arrangement: list, branch = "NEWS"):
    for ind_y in range(len(arrangement)):
        for ind_x in range(len(arrangement[ind_y])):

            if arrangement[ind_y][ind_x] == None:
                pass
            else:
                arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = branch)


