"""Drag-and-drop adapter — non-invasive, delegation-based.

Wraps the tkinterdnd2 library behind a single adapter so the rest of the
codebase never touches tkinterdnd2 internals. If the root window is not
a ``tkinterdnd2.Tk`` instance, DnD is unavailable and all register calls
become safe no-ops.
"""

from __future__ import annotations

import logging
import tkinter as tk
from typing import Callable

logger = logging.getLogger(__name__)


class DnDAdapter:
    """Attach drag-and-drop capability to an existing Tk window.

    Works when the root window is ``tkinterdnd2.Tk()``. When the root is a
    plain ``tk.Tk()`` or ``ttk.Window()``, DnD is unavailable and all
    ``register_drop_target`` calls become safe no-ops.

    Usage::

        adapter = DnDAdapter(root)
        if adapter.available:
            adapter.register_drop_target(root, on_root_drop)
            adapter.register_drop_target(listbox, on_listbox_drop)
    """

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._available = False

        try:
            import tkinterdnd2
            if isinstance(root, tkinterdnd2.Tk):
                self._available = True
                logger.info("DnD adapter 已启用（根窗口为 tkinterdnd2.Tk）")
            else:
                logger.info("根窗口非 tkinterdnd2.Tk，拖放功能不可用")
        except ImportError:
            logger.info("tkinterdnd2 未安装，拖放功能不可用")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        return self._available

    def register_drop_target(
        self,
        widget: tk.Widget,
        callback: Callable[[tk.Event], None],
    ) -> None:
        """Register *widget* as a file-drop target.

        Does nothing when DnD is unavailable (graceful degradation).
        """
        if not self._available:
            return
        try:
            widget.drop_target_register("*")
            widget.dnd_bind("<<Drop>>", callback)
        except tk.TclError as exc:
            logger.warning("注册拖放目标失败: %s", exc)
