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


class ComboboxAutocomplete(ttk.Combobox):  # pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Autocomplete combobox widget
    """
    def __init__(self, master=None, startswith_match=False, **kwargs):
        super().__init__(master, **kwargs)
        self._autocomplete_items = []
        self.startswith_match = startswith_match
        self._last_checked_value = None
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Button-1>", self._toggle_dropdown)

        self.after(100, self._check_for_changes)

    def _check_for_changes(self):
        current_value = self.get()
        if current_value != self._last_checked_value:
            self._update_autocomplete(current_value)
        self._last_checked_value = current_value
        self.after(100, self._check_for_changes)

    def _update_autocomplete(self, entry_data):
        values = self.autocomplete_function(entry_data)
        if values:
            self['values'] = values
            self.current(0)  # Select the first item in the dropdown
        else:
            self['values'] = []

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

    def set_values(self, values):
        self._autocomplete_items = values
        self['values'] = values

    def autocomplete_function(self, entry_data):
        # Simple case-insensitive match
        return [item for item in self._autocomplete_items if item.lower().startswith(entry_data.lower())]

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

        combobox_autocomplete = ComboboxAutocomplete(root, startswith_match=False)
        combobox_autocomplete.set_values(list_of_items)

        combobox_autocomplete.pack()

        combobox_autocomplete.focus()

        root.mainloop()

    main()
