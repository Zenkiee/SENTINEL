import tkinter as tk

class RoundedFrame(tk.Frame):
    def __init__(
        self,
        parent,
        bg="#FFFFFF",
        parent_bg="#F5F5F7",
        radius=18,
        border_color="#E5E5EA",
        border_width=1,
        padding=16,
        hoverable=False,
        hover_bg=None,
        hover_border=None,
        **kwargs
    ):
        super().__init__(parent, bg=parent_bg, **kwargs)

        self.bg_color = bg
        self.parent_bg = parent_bg
        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding

        self.hoverable = hoverable
        self.hover_bg = hover_bg or bg
        self.hover_border = hover_border or border_color
        self._hovered = False

        self.canvas = tk.Canvas(self, bg=parent_bg, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window(
            padding,
            padding,
            window=self.inner,
            anchor="nw"
        )

        self.canvas.bind("<Configure>", self._resize)
        self.inner.bind("<Configure>", self._update_requested_size)

        if hoverable:
            self._bind_hover_recursive(self)

    #Trying to fix the vanishing button in report page when hovering over the card. -PJ
    def _bind_hover_recursive(self, widget):
        # Bind the hover triggers ONLY to the canvas itself.
        # This completely stops sub-widgets from fighting for mouse hover focus!
        self.canvas.bind("<Enter>", self._on_enter, add="+")
        self.canvas.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        if self._hovered:
            return
        self._hovered = True
        self._animate_hover(True)

    def _on_leave(self, event=None):
        if not self._hovered:
            return
        
        # Check carefully if the cursor is truly outside the Card boundaries
        try:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            if 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height():
                # Mouse is still inside the card layout area (e.g., over a button), ignore!
                return
        except Exception:
            pass
            
        self._hovered = False
        self._animate_hover(False)

    def _animate_hover(self, entering):
        bg = self.hover_bg if entering else self.bg_color
        border = self.hover_border if entering else self.border_color
        shadow_offset = 3 if entering else 0

        # 1. Update the background of the immediate parent frame
        self.inner.config(bg=bg)
        
        # 2. Update child configurations *safely* without causing a restack loop
        self._update_child_bg(self.inner, bg)

        # 3. Trigger the shape fill refresh
        self._current_bg = bg
        self._current_border = border
        self._shadow_offset = shadow_offset
        self._redraw()

        # 4. CRITICAL: Forcefully pull the embedded window item to the top layer 
        # and drop the background drawings beneath it!
        self.canvas.tag_lower("rounded")
        self.canvas.tag_raise(self.window_id)

    def _update_child_bg(self, widget, bg):
        for child in widget.winfo_children():
            try:
                # Only update simple container frames or text labels
                # Skip updates on full buttons to avoid drawing glitches
                if isinstance(child, (tk.Label, tk.Frame)):
                    child.config(bg=bg)
            except Exception:
                pass
            self._update_child_bg(child, bg)
            
    def _redraw(self):
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            if w < 2 or h < 2:
                return
            self.canvas.delete("rounded")
            bg = getattr(self, "_current_bg", self.bg_color)
            border = getattr(self, "_current_border", self.border_color)
            self._draw_rounded_rect(
                1, 1, w - 1, h - 1,
                self.radius,
                fill=bg,
                outline=border,
                width=self.border_width,
                tags="rounded"
            )
            self.canvas.tag_lower("rounded")
        except Exception:
            pass

    def _update_requested_size(self, event=None):
        width = self.inner.winfo_reqwidth() + self.padding * 2
        height = self.inner.winfo_reqheight() + self.padding * 2
        self.canvas.configure(width=width, height=height)

    def _resize(self, event):
        width = max(1, event.width)
        height = max(1, event.height)

        self.canvas.delete("rounded")

        bg = getattr(self, "_current_bg", self.bg_color)
        border = getattr(self, "_current_border", self.border_color)

        self._draw_rounded_rect(
            1,
            1,
            width - 1,
            height - 1,
            self.radius,
            fill=bg,
            outline=border,
            width=self.border_width,
            tags="rounded"
        )

        self.canvas.tag_lower("rounded")

        self.canvas.itemconfigure(
            self.window_id,
            width=max(1, width - self.padding * 2),
            height=max(1, height - self.padding * 2)
        )

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]

        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            **kwargs
        )