# pip install customtkinter
# Optional (for gradient image): pip install pillow

import math
import customtkinter as ctk
from tkinter import messagebox
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("dark-blue")

BTN_FONT = ("Inter", 16)
DISP_FONT_LARGE = ("JetBrains Mono", 28)
DISP_FONT_SMALL = ("JetBrains Mono", 14)


class GradientHeader(ctk.CTkLabel):
    """A simple gradient banner using PIL; falls back to solid color if PIL not available."""

    def __init__(self, master, width=480, height=80, color1=(59, 130, 246), color2=(147, 51, 234), **kwargs):
        if Image is not None:
            img = Image.new("RGB", (width, height), color1)
            # vertical gradient
            for y in range(height):
                r = int(color1[0] + (color2[0]-color1[0]) * y/height)
                g = int(color1[1] + (color2[1]-color1[1]) * y/height)
                b = int(color1[2] + (color2[2]-color1[2]) * y/height)
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))
            self._photo = ImageTk.PhotoImage(img)
            super().__init__(master, image=self._photo, text="SciCalc • clean & modern", compound="center",
                             font=("Inter SemiBold", 18), text_color="white", **kwargs)
        else:
            super().__init__(master, text="SciCalc • clean & modern", font=("Inter SemiBold", 18),
                             text_color="white", fg_color="#3b82f6", **kwargs)


class ModernCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Calculator — Modern UI")
        self.geometry("480x700")
        self.minsize(420, 640)

        # App grid
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Gradient header
        self.header = GradientHeader(self, width=800, height=90)
        self.header.grid(row=0, column=0, sticky="ew")

        # Display frame
        disp = ctk.CTkFrame(self, corner_radius=20,
                            fg_color=("#111318", "#0c0e10"))
        disp.grid(row=1, column=0, padx=16, pady=(16, 10), sticky="nsew")
        disp.grid_columnconfigure(0, weight=1)

        self.expr_var = ctk.StringVar(value="")
        self.res_var = ctk.StringVar(value="0")

        self.expr_label = ctk.CTkLabel(disp, textvariable=self.expr_var, anchor="e",
                                       font=DISP_FONT_SMALL, text_color=("#334155", "#94a3b8"))
        self.expr_label.grid(row=0, column=0, sticky="ew",
                             padx=16, pady=(12, 0))

        self.result_label = ctk.CTkLabel(disp, textvariable=self.res_var, anchor="e",
                                         font=DISP_FONT_LARGE)
        self.result_label.grid(
            row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Buttons container
        self.pad = ctk.CTkFrame(self, corner_radius=24)
        self.pad.grid(row=3, column=0, padx=16, pady=16, sticky="nsew")
        for r in range(6):
            self.pad.grid_rowconfigure(r, weight=1, uniform="row")
        for c in range(5):
            self.pad.grid_columnconfigure(c, weight=1, uniform="col")

        # Key layout (rows)
        keys = [
            ["AC", "⌫", "(", ")", "/"],
            ["7", "8", "9", "*", "^"],
            ["4", "5", "6", "-", "√"],
            ["1", "2", "3", "+", "x²"],
            ["0", ".", "=", "Ans", "mod"],
            ["sin", "cos", "tan", "ln", "log"]
        ]

        self.last_answer = 0

        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                self._make_btn(key, r, c)

        # Keyboard bindings
        self.bind_all("<Key>", self._on_key)
        self.bind("<Return>", lambda e: self._equals())
        self.bind("<BackSpace>", lambda e: self._backspace())
        self.bind("<Escape>", lambda e: self._clear())

    # ---- UI helpers ----
    def _make_btn(self, text, r, c):
        style = self._btn_style(text)
        btn = ctk.CTkButton(self.pad, text=text, **style,
                            command=lambda t=text: self._press(t))
        btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

    def _btn_style(self, text):
        base = dict(font=BTN_FONT, corner_radius=14)
        accent = {"fg_color": "#0ea5e9",
                  "hover_color": "#0284c7", "text_color": "white"}
        danger = {"fg_color": "#ef4444",
                  "hover_color": "#dc2626", "text_color": "white"}
        op = {"fg_color": "#374151",
              "hover_color": "#4b5563", "text_color": "#e5e7eb"}
        num = {"fg_color": "#1f2937",
               "hover_color": "#374151", "text_color": "#e5e7eb"}

        if text in ("=",):
            return {**base, **accent, "height": 48}
        if text in ("AC", "⌫"):
            return {**base, **danger}
        if text in ("+", "-", "*", "/", "^", "mod"):
            return {**base, **op}
        if text in ("(", ")", "√", "x²", "sin", "cos", "tan", "ln", "log", "Ans"):
            return {**base, **op}
        return {**base, **num}

    # ---- Logic ----
    def _press(self, key):
        if key == "AC":
            self._clear()
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._equals()
        elif key == "x²":
            self._append("^2")
        elif key == "√":
            self._append("sqrt(")
        elif key == "Ans":
            self._append(str(self.last_answer))
        elif key in ("sin", "cos", "tan", "ln", "log"):
            mapping = {"sin": "sin(", "cos": "cos(",
                       "tan": "tan(", "ln": "ln(", "log": "log("}
            self._append(mapping[key])
        elif key == "mod":
            self._append("%")
        else:
            self._append(key)

    def _append(self, s):
        self.expr_var.set(self.expr_var.get() + s)

    def _clear(self):
        self.expr_var.set("")
        self.res_var.set("0")

    def _backspace(self):
        cur = self.expr_var.get()
        if cur:
            self.expr_var.set(cur[:-1])

    def _on_key(self, event):
        ch = event.char
        if ch in "0123456789.+-*/%^()":
            self._append(ch)
        elif ch.lower() == 's':
            self._append("sin(")
        elif ch.lower() == 'c':
            self._append("cos(")
        elif ch.lower() == 't':
            self._append("tan(")
        elif ch.lower() == 'l':
            self._append("ln(")

    def _equals(self):
        expr = self.expr_var.get()
        try:
            # Safe eval mapping
            safe = {
                'sin': lambda x: math.sin(math.radians(x)),
                'cos': lambda x: math.cos(math.radians(x)),
                'tan': lambda x: math.tan(math.radians(x)),
                'ln': lambda x: math.log(x),
                'log': lambda x: math.log10(x),
                'sqrt': lambda x: math.sqrt(x),
                'pi': math.pi,
                'e': math.e
            }
            formatted = expr.replace('^', '**')
            result = eval(formatted, {"__builtins__": {}}, safe)
            if isinstance(result, float):
                result = round(result, 10)
            self.res_var.set(str(result))
            self.last_answer = result
        except ZeroDivisionError:
            self._error("Division by zero")
        except Exception:
            self._error("Invalid expression")

    def _error(self, msg):
        messagebox.showerror("Error", msg)
        self.res_var.set("Error")


if __name__ == "__main__":
    app = ModernCalculator()
    app.mainloop()
