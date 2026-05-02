"""Reusable UI components built on tkinter / ttkbootstrap."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ScrollableFrame(ttk.Frame):
    """A container that adds vertical scrollbar when content overflows.

    Usage:
        sf = ScrollableFrame(parent, padding=20)
        label = ttk.Label(sf.inner, text="Content here")
        label.pack()
    """

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(
            self, orient=VERTICAL, command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas.grid(row=0, column=0, sticky="nsew")

        self._inner = ttk.Frame(self._canvas)

        def _on_inner_configure(_: tk.Event) -> None:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        self._inner.bind("<Configure>", _on_inner_configure)

        def _on_canvas_configure(event: tk.Event) -> None:
            self._canvas.itemconfig(
                self._canvas_window, width=event.width
            )

        self._canvas.bind("<Configure>", _on_canvas_configure)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        def _on_mousewheel(event: tk.Event) -> None:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self._canvas.bind("<Enter>", lambda _: self._canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self._canvas.bind("<Leave>", lambda _: self._canvas.unbind_all("<MouseWheel>"))

    @property
    def inner(self) -> ttk.Frame:
        """The frame where child widgets should be placed."""
        return self._inner


class DnDListbox(tk.Listbox):
    """A Listbox that accepts file drops via tkinterdnd2.

    Callback signature: on_files_dropped(file_paths: list[str]) -> None

    If *dnd_adapter* is provided and available, DnD is registered through
    the adapter. Otherwise the listbox degrades gracefully — it still works
    for display and the user can add files via the button.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_files_dropped: Callable[[list[str]], None],
        dnd_adapter: object | None = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_files_dropped = on_files_dropped
        self._register_dnd(dnd_adapter)

    def _register_dnd(self, adapter: object | None) -> None:
        if adapter is not None and getattr(adapter, "available", False):
            adapter.register_drop_target(self, self._on_drop)

    def _on_drop(self, event: tk.Event) -> None:
        if not event.data:
            return
        try:
            files = self.tk.splitlist(event.data)
        except Exception:
            files = event.data.split()
        cleaned = [f.strip("{}") for f in files if f.strip("{}")]
        if cleaned:
            self._on_files_dropped(cleaned)
