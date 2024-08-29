#!/usr/bin/env python3

'''
This file is part of Ardupilot methodic configurator. https://github.com/ArduPilot/MethodicConfigurator

https://code.activestate.com/recipes/580770-combobox-autocomplete/

SPDX-FileCopyrightText: 2024 Amilcar do Carmo Lucas <amilcar.lucas@iav.de>

SPDX-License-Identifier: GPL-3.0-or-later
'''


import re

from tkinter import StringVar, Entry, Frame, Listbox, Scrollbar
from tkinter.constants import END, HORIZONTAL, N, S, E, W, VERTICAL, SINGLE

import tkinter as tk
from tkinter import ttk

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class EntryAutocomplete(Entry):  # pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Autocomplete combobox widget
    """
    def __init__(self, master, list_of_items=None, autocomplete_function=None, listbox_width=None, listbox_height=7, # pylint: disable=too-many-arguments, too-many-branches
                 ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, **kwargs):
        if hasattr(self, "autocomplete_function"):
            if autocomplete_function is not None:
                raise ValueError("Combobox_Autocomplete subclass has 'autocomplete_function' implemented")
        else:
            if autocomplete_function is not None:
                self.autocomplete_function = autocomplete_function
            else:
                if list_of_items is None:
                    raise ValueError("If not given complete function, list_of_items can't be 'None'")

                if ignorecase_match:
                    if startswith_match:
                        def matches_function(entry_data, item):
                            return item.startswith(entry_data)
                    else:
                        def matches_function(entry_data, item):
                            return item in entry_data

                    self.autocomplete_function = lambda entry_data: \
                        [item for item in self.list_of_items if matches_function(entry_data, item)]
                else:
                    if startswith_match:
                        def matches_function(escaped_entry_data, item):
                            return re.match(escaped_entry_data, item, re.IGNORECASE)
                    else:
                        def matches_function(escaped_entry_data, item):
                            return re.search(escaped_entry_data, item, re.IGNORECASE)

                    def local_autocomplete_function(entry_data):
                        escaped_entry_data = re.escape(entry_data)
                        return [item for item in self.list_of_items if matches_function(escaped_entry_data, item)]

                    self.autocomplete_function = local_autocomplete_function

        self._listbox_height = int(listbox_height)
        self._listbox_width = listbox_width

        self.list_of_items = list_of_items

        self._use_vscrollbar = vscrollbar
        self._use_hscrollbar = hscrollbar

        kwargs.setdefault("background", "white")

        if "textvariable" in kwargs:
            self._entry_var = kwargs["textvariable"]
        else:
            self._entry_var = kwargs["textvariable"] = StringVar()

        Entry.__init__(self, master, **kwargs)

        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)

        self._listbox = None

        self.bind("<Tab>", self._on_tab)
        self.bind("<Up>", self._previous)
        self.bind("<Down>", self._next)
        self.bind('<Control-n>', self._next)
        self.bind('<Control-p>', self._previous)

        self.bind("<Return>", self._update_entry_from_listbox)
        self.bind("<Escape>", lambda event: self.unpost_listbox())

    def _on_tab(self, _event):
        self.post_listbox()
        return "break"

    def _on_change_entry_var(self, _name, _index, _mode):

        entry_data = self._entry_var.get()

        if entry_data == '':
            self.unpost_listbox()
            self.focus()
        else:
            values = self.autocomplete_function(entry_data)
            if values:
                if self._listbox is None:
                    self._build_listbox(values)
                else:
                    self._listbox.delete(0, END)

                    height = min(self._listbox_height, len(values))
                    self._listbox.configure(height=height)

                    for item in values:
                        self._listbox.insert(END, item)

            else:
                self.unpost_listbox()
                self.focus()

    def _build_listbox(self, values):
        listbox_frame = Frame()

        self._listbox = Listbox(listbox_frame, background="white", selectmode=SINGLE, activestyle="none",
                                exportselection=False)
        self._listbox.grid(row=0, column=0,sticky = N+E+W+S)

        self._listbox.bind("<ButtonRelease-1>", self._update_entry_from_listbox)
        self._listbox.bind("<Return>", self._update_entry_from_listbox)
        self._listbox.bind("<Escape>", lambda event: self.unpost_listbox())

        self._listbox.bind('<Control-n>', self._next)
        self._listbox.bind('<Control-p>', self._previous)

        if self._use_vscrollbar:
            vbar = Scrollbar(listbox_frame, orient=VERTICAL, command= self._listbox.yview)
            vbar.grid(row=0, column=1, sticky=N+S)

            self._listbox.configure(yscrollcommand= lambda f, l: autoscroll(vbar, f, l))

        if self._use_hscrollbar:
            hbar = Scrollbar(listbox_frame, orient=HORIZONTAL, command= self._listbox.xview)
            hbar.grid(row=1, column=0, sticky=E+W)

            self._listbox.configure(xscrollcommand= lambda f, l: autoscroll(hbar, f, l))

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        x = -self.cget("borderwidth") - self.cget("highlightthickness")
        y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")

        if self._listbox_width:
            width = self._listbox_width
        else:
            width=self.winfo_width()

        listbox_frame.place(in_=self, x=x, y=y, width=width)

        height = min(self._listbox_height, len(values))
        self._listbox.configure(height=height)

        for item in values:
            self._listbox.insert(END, item)

    def post_listbox(self):
        if self._listbox is not None:
            return

        entry_data = self._entry_var.get()
        if entry_data == '':
            return

        values = self.autocomplete_function(entry_data)
        if values:
            self._build_listbox(values)

    def unpost_listbox(self):
        if self._listbox is not None:
            self._listbox.master.destroy()
            self._listbox = None

    def get_value(self):
        return self._entry_var.get()

    def set_value(self, text, close_dialog=False):
        self._set_var(text)

        if close_dialog:
            self.unpost_listbox()

        self.icursor(END)
        self.xview_moveto(1.0)

    def _set_var(self, text):
        self._entry_var.trace_remove("write", self._trace_id)
        self._entry_var.set(text)
        self._trace_id = self._entry_var.trace_add('write', self._on_change_entry_var)

    def _update_entry_from_listbox(self, _event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if current_selection:
                text = self._listbox.get(current_selection)
                self._set_var(text)

            self._listbox.master.destroy()
            self._listbox = None

            self.focus()
            self.icursor(END)
            self.xview_moveto(1.0)

        return "break"

    def _previous(self, _event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == 0:
                    index = END
                else:
                    index -= 1

                self._listbox.see(index)
                self._listbox.selection_set(first=index)
                self._listbox.activate(index)

        return "break"

    def _next(self, _event):
        if self._listbox is not None:

            current_selection = self._listbox.curselection()
            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == self._listbox.size() - 1:
                    index = 0
                else:
                    index +=1

                self._listbox.see(index)
                self._listbox.selection_set(index)
                self._listbox.activate(index)
        return "break"

class ComboboxAutocomplete(ttk.Combobox):  # pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Autocomplete combobox widget

    The list of items to autocomplete from is given as a list of strings.
    Initially the entire list of values is displayed and none is selected
    as you type text in the combobox, the list of values displayed in the
    combobox changes to only contain the values that match the text you
    have typed so far.
    """
    def __init__(self, master=None, ignorecase_match=True,
                 startswith_match=False, hscrollbar=True, **kwargs):
        super().__init__(master, **kwargs)
        self._autocomplete_items = []
        self.ignorecase_match = ignorecase_match
        self.startswith_match = startswith_match
        self.hscrollbar = hscrollbar
        self._last_checked_value = None
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Button-1>", self._toggle_dropdown)

        self.after(100, self._check_for_changes)

    def _check_for_changes(self):
        current_value = self.get()
        if current_value != self._last_checked_value:
            self._update_autocomplete(current_value)
            self._show_dropdown()
        self._last_checked_value = current_value
        self.after(100, self._check_for_changes)
        #self.focus_set()  # Keep the focus on the text entry

    def _update_autocomplete(self, entry_data):
        values = self.autocomplete_function(entry_data)
        if values:
            self['values'] = values
            if len(values) == 1:
                self.current(0)  # Select the first item in the dropdown
                self._hide_dropdown()
        else:
            self['values'] = [] # self._autocomplete_items

    def autocomplete_function(self, entry_data):
        if self.ignorecase_match:
            if self.startswith_match:
                return [item for item in self._autocomplete_items if item.lower().startswith(entry_data.lower())]
            return [item for item in self._autocomplete_items if entry_data.lower() in item.lower()]
        if self.startswith_match:
            return [item for item in self._autocomplete_items if item.startswith(entry_data)]
        return [item for item in self._autocomplete_items if entry_data in item]

    def set_values(self, values):
        self._autocomplete_items = values
        self['values'] = values

    def _on_key_release(self, event):
        self._show_dropdown()

    def _show_dropdown(self):
        self.event_generate('<Down>')

    def _hide_dropdown(self):
        self.event_generate('<Up>')

    def _toggle_dropdown(self, event=None):
        if self['state'] == 'readonly': # normal
            self._hide_dropdown()
        elif self['state'] == 'normal': # disabled
            self._show_dropdown()

    def get_value(self):
        return self.get()

    def set_value(self, text, close_dialog=False):
        self.set(text)

        if close_dialog:
            self.master.focus_set()

    def _previous(self, _event):
        current_index = self.current()
        if current_index > 0:
            self.current(current_index - 1)
        else:
            self.current(len(self['values']) - 1)

    def _next(self, _event):
        current_index = self.current()
        if current_index < len(self['values']) - 1:
            self.current(current_index + 1)
        else:
            self.current(0)

class ComboboxAutocomplete2(ttk.Combobox):
    def __init__(self, master, items, **kwargs):
        super().__init__(master, **kwargs)
        self.items = items
        self.update_values()

    def update_values(self):
        filtered_items = [item for item in self.items if item.lower().startswith(self.get().lower())]
        self['values'] = filtered_items

import tkinter as tk
import tkinter.ttk as ttk


#https://stackoverflow.com/questions/59763822/show-combobox-drop-down-while-editing-text-using-tkinter
class Combobox3(ttk.Combobox):
    def _tk(self, cls, parent):
        obj = cls(parent)
        obj.destroy()
        if cls is tk.Toplevel:
            obj._w = self.tk.call('ttk::combobox::PopdownWindow', self)
        else:
            obj._w = '{}.{}'.format(parent._w, 'f.l')
        return obj
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.popdown = self._tk(tk.Toplevel, parent)
        self.listbox = self._tk(tk.Listbox, self.popdown)

        self.bind("<KeyPress>", self.on_keypress, '+')
        self.listbox.bind("<Up>", self.on_keypress)

    def on_keypress(self, event):
        if event.widget == self:
            state = self.popdown.state()

            if state == 'withdrawn' \
                    and event.keysym not in ['BackSpace', 'Up']:
                self.event_generate('<Button-1>')
                self.after(0, self.focus_set)

            if event.keysym == 'Down':
                self.after(0, self.listbox.focus_set)

        else:  # self.listbox
            curselection = self.listbox.curselection()

            if event.keysym == 'Up' and curselection[0] == 0:
                self.popdown.withdraw()

import tkinter as tk
from PIL import Image, ImageTk

# https://coderslegacy.com/searchable-combobox-in-tkinter/
class SearchableComboBox():
    def __init__(self, options) -> None:
        self.dropdown_id = None
        self.options = options

        # Create a Text widget for the entry field
        wrapper = tk.Frame(root)
        wrapper.pack()

        self.entry = tk.Entry(wrapper, width=24)
        self.entry.bind("<KeyRelease>", self.on_entry_key)
        self.entry.bind("<FocusIn>", self.show_dropdown)
        self.entry.pack(side=tk.LEFT)

        # Dropdown icon/button
        #self.icon = ImageTk.PhotoImage(Image.open("dropdown_arrow.png").resize((16,16)))
        #tk.Button(wrapper, image=self.icon, command=self.show_dropdown).pack(side=tk.LEFT)

        # Create a Listbox widget for the dropdown menu
        self.listbox = tk.Listbox(root, height=5, width=30)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for option in self.options:
            self.listbox.insert(tk.END, option)

    def on_entry_key(self, event):
        typed_value = event.widget.get().strip().lower()
        if not typed_value:
            # If the entry is empty, display all options
            self.listbox.delete(0, tk.END)
            for option in self.options:
                self.listbox.insert(tk.END, option)
        else:
            # Filter options based on the typed value
            self.listbox.delete(0, tk.END)
            filtered_options = [option for option in self.options if option.lower().startswith(typed_value)]
            for option in filtered_options:
                self.listbox.insert(tk.END, option)
        self.show_dropdown()

    def on_select(self, event):
            selected_index = self.listbox.curselection()
            if selected_index:
                selected_option = self.listbox.get(selected_index)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, selected_option)

    def show_dropdown(self, event=None):
        self.listbox.place(in_=self.entry, x=0, rely=1, relwidth=1.0, anchor="nw")
        self.listbox.lift()

        # Show dropdown for 2 seconds
        if self.dropdown_id: # Cancel any old events
            self.listbox.after_cancel(self.dropdown_id)
        self.dropdown_id = self.listbox.after(2000, self.hide_dropdown)

    def hide_dropdown(self):
        self.listbox.place_forget()

# Create the main window
root = tk.Tk()
root.title("Searchable Dropdown")

options = ["Apple", "Banana", "Cherry", "Date", "Grapes", "Kiwi", "Mango", "Orange", "Peach", "Pear"]
SearchableComboBox(options)

# Run the Tkinter event loop
root.geometry('220x150')
root.mainloop()


if __name__ == '__main__':
    def main():

        list_of_items = [
            "Cordell Cannata", "Lacey Naples", "Zachery Manigault", "Regan Brunt",
            "Mario Hilgefort", "Austin Phong", "Moises Saum", "Willy Neill",
            "Rosendo Sokoloff", "Salley Christenberry", "Toby Schneller",
            "Angel Buchwald", "Nestor Criger", "Arie Jozwiak", "Nita Montelongo",
            "Clemencia Okane", "Alison Scaggs", "Von Petrella", "Glennie Gurley",
            "Jamar Callender", "Titus Wenrich", "Chadwick Liedtke", "Sharlene Yochum",
            "Leonida Mutchler", "Duane Pickett", "Morton Brackins", "Ervin Trundy",
            "Antony Orwig", "Audrea Yutzy", "Michal Hepp", "Annelle Hoadley",
            "Hank Wyman", "Mika Fernandez", "Elisa Legendre", "Sade Nicolson",
            "Jessie Yi", "Forrest Mooneyhan", "Alvin Widell", "Lizette Ruppe",
            "Marguerita Pilarski", "Merna Argento", "Jess Daquila", "Breann Bevans",
            "Melvin Guidry", "Jacelyn Vanleer", "Jerome Riendeau", "Iraida Nyquist",
            "Micah Glantz", "Dorene Waldrip", "Fidel Garey", "Vertie Deady",
            "Rosalinda Odegaard", "Chong Hayner", "Candida Palazzolo", "Bennie Faison",
            "Nova Bunkley", "Francis Buckwalter", "Georgianne Espinal", "Karleen Dockins",
            "Hertha Lucus", "Ike Alberty", "Deangelo Revelle", "Juli Gallup",
            "Wendie Eisner", "Khalilah Travers", "Rex Outman", "Anabel King",
            "Lorelei Tardiff", "Pablo Berkey", "Mariel Tutino", "Leigh Marciano",
            "Ok Nadeau", "Zachary Antrim", "Chun Matthew", "Golden Keniston",
            "Anthony Johson", "Rossana Ahlstrom", "Amado Schluter", "Delila Lovelady",
            "Josef Belle", "Leif Negrete", "Alec Doss", "Darryl Stryker",
            "Michael Cagley", "Sabina Alejo", "Delana Mewborn", "Aurelio Crouch",
            "Ashlie Shulman", "Danielle Conlan", "Randal Donnell", "Rheba Anzalone",
            "Lilian Truax", "Weston Quarterman", "Britt Brunt", "Leonie Corbett",
            "Monika Gamet", "Ingeborg Bello", "Angelique Zhang", "Santiago Thibeau",
            "Eliseo Helmuth"
        ]

        root = tk.Tk()
        root.geometry("300x200")

        #combobox_autocomplete = ComboboxAutocomplete(root)
        #combobox_autocomplete.set_values(list_of_items)

        #combobox_autocomplete.pack()

        #combobox_autocomplete.focus()

        #combobox_autocomplete2 = ComboboxAutocomplete2(root, list_of_items)
        #combobox_autocomplete2.pack()

        combobox_autocomplete3 = Combobox3(root, values=list_of_items)
        combobox_autocomplete3.pack()

        entry_autocomplete = EntryAutocomplete(root, list_of_items=list_of_items, startswith_match=False)

        entry_autocomplete.pack()

        entry_autocomplete.focus()

        root.mainloop()

    main()
