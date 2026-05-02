"""Drag-and-drop adapter — non-invasive, delegation-based.

Wraps the tkinterdnd2 library behind a single adapter so the rest of the
codebase never touches tkinterdnd2 internals. If the library or its native
Tcl extension is missing, the adapter reports ``available=False`` and all
register calls become safe no-ops.
"""

from __future__ import annotations

import logging
import tkinter as tk
from typing import Callable

logger = logging.getLogger(__name__)


class DnDAdapter:
    """Attach drag-and-drop capability to an existing Tk window.

    Usage::

        adapter = DnDAdapter(root)
        if adapter.available:
            adapter.register_drop_target(root, on_root_drop)
            adapter.register_drop_target(listbox, on_listbox_drop)
    """

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._available = False
        self._dnd_wrapper_cls: type | None = None

        try:
            from tkinterdnd2.TkinterDnD import DnDWrapper, _require

            _require(root)
            self._dnd_wrapper_cls = DnDWrapper
            self._available = True
            logger.info("DnD adapter 已启用")
        except ImportError:
            logger.info("tkinterdnd2 未安装，拖放功能不可用")
        except (RuntimeError, tk.TclError) as exc:
            logger.info("无法加载 tkdnd Tcl 扩展: %s", exc)

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
        self._ensure_dnd_methods(widget)
        try:
            widget.drop_target_register("*")
            widget.dnd_bind("<<Drop>>", callback)
        except tk.TclError as exc:
            logger.warning("注册拖放目标失败: %s", exc)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_dnd_methods(self, widget: tk.Widget) -> None:
        """Bind ``DnDWrapper`` methods onto *widget* when the import-time
        class-level patch of ``tkinter.BaseWidget`` did not take effect
        (observed in some PyInstaller frozen builds)."""
        if hasattr(widget, "drop_target_register"):
            return  # already available through normal MRO

        import types

        dw = self._dnd_wrapper_cls
        for name in (
            "drop_target_register",
            "dnd_bind",
            "_dnd_bind",
            "_substitute_dnd",
            "_subst_format_dnd",
            "_subst_format_str_dnd",
        ):
            if hasattr(widget, name):
                continue
            attr = getattr(dw, name, None)
            if attr is None:
                continue
            if callable(attr):
                setattr(widget, name, types.MethodType(attr, widget))
            else:
                setattr(widget, name, attr)
