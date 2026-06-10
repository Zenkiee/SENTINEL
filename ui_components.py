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
        **kwargs
    ):
        super().__init__(parent, bg=parent_bg, **kwargs)

        self.bg_color = bg
        self.parent_bg = parent_bg
        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding

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

    def _update_requested_size(self, event=None):
        width = self.inner.winfo_reqwidth() + self.padding * 2
        height = self.inner.winfo_reqheight() + self.padding * 2
        self.canvas.configure(width=width, height=height)

    def _resize(self, event):
        width = max(1, event.width)
        height = max(1, event.height)

        self.canvas.delete("rounded")

        self._draw_rounded_rect(
            1,
            1,
            width - 1,
            height - 1,
            self.radius,
            fill=self.bg_color,
            outline=self.border_color,
            width=self.border_width,
            tags="rounded"
        )

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