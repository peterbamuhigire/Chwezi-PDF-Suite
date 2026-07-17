"""The themed desktop interface for visual PDF signing."""

from __future__ import annotations

import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, ClassVar

from ui_icons import IconStore
from ui_theme import (
    BODY_FONT,
    MONO_FONT,
    apply_ttk_theme,
    load_theme,
    save_theme,
    style_text_widget,
)
from window_geometry import centered_geometry


class SignatureApp:
    POSITIONS: ClassVar[tuple[tuple[str, str, int, int], ...]] = (
        ("NW", "top-left", 0, 0),
        ("NE", "top-right", 0, 1),
        ("SW", "bottom-left", 1, 0),
        ("SE", "bottom-right", 1, 1),
    )

    def __init__(self, root: tk.Tk, signature_factory: Callable[..., Any]):
        self.root = root
        self.signature_factory = signature_factory
        self.icons = IconStore()
        self._icon_targets: list[tuple[Any, str, str, int, str]] = []
        self.icons.apply_window_icon(root, "app-pdf-signer")
        self.root.title("PDF Signer · Chwezi Document Suite")
        self.root.minsize(940, 900)
        self.theme = load_theme()
        self.palette = apply_ttk_theme(root, self.theme)

        self.sig_path = tk.StringVar()
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.batch_mode = tk.BooleanVar(value=False)
        self.pages_var = tk.StringVar(value="all")
        self.range_var = tk.StringVar(value="1")
        self.skip_var = tk.StringVar(value="")
        self.position = tk.StringVar(value="bottom-left")
        self.scale = tk.DoubleVar(value=25)
        self.x_offset = tk.DoubleVar(value=0.5)
        self.y_offset = tk.DoubleVar(value=0.5)
        self.opacity = tk.DoubleVar(value=100)
        self.rotation = tk.IntVar(value=0)
        self._pos_buttons: dict[str, tk.Button] = {}

        self._build()
        self._apply_theme()
        self._update_preview()

    def _build(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main = ttk.Frame(self.root, padding=24, style="App.TFrame")
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(2, weight=1)

        header = ttk.Frame(main, style="App.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)
        title_label = ttk.Label(header, text="PDF Signer", style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky="w")
        self._bind_icon(title_label, "apps", "app-pdf-signer", 30)
        ttk.Label(
            header,
            text="Place a visual signature precisely, without sending the document online.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.theme_btn = ttk.Button(header, command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=1, rowspan=2, sticky="e")

        files = ttk.LabelFrame(main, text=" 01 · Files ", style="Card.TLabelframe")
        files.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        files.columnconfigure(1, weight=1)
        self._file_row(
            files,
            0,
            "Signature PNG",
            self.sig_path,
            self._browse_signature,
            ("actions", "image-up"),
        )
        self._file_row(
            files,
            1,
            "PDF or folder",
            self.input_path,
            self._browse_input,
            ("navigation", "folder-open"),
        )
        self._file_row(
            files,
            2,
            "Save signed copy",
            self.output_path,
            self._browse_output,
            ("actions", "folder-down"),
        )
        batch_check = ttk.Checkbutton(
            files,
            text="Batch mode · sign every PDF in the selected folder",
            variable=self.batch_mode,
            command=self._on_batch_toggle,
            style="Card.TCheckbutton",
        )
        batch_check.grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 0))
        self._bind_icon(batch_check, "actions", "copy", 16)

        config = ttk.LabelFrame(main, text=" 02 · Placement ", style="Card.TLabelframe")
        config.grid(row=2, column=0, sticky="nsew", padx=(0, 6))
        config.columnconfigure(1, weight=1)

        pages_label = ttk.Label(config, text="Pages", style="Card.TLabel")
        pages_label.grid(row=0, column=0, sticky="w")
        self._bind_icon(pages_label, "actions", "layers", 16)
        pages = ttk.Combobox(
            config,
            textvariable=self.pages_var,
            state="readonly",
            values=["all", "first", "last", "odd", "even", "range"],
            width=12,
        )
        pages.grid(row=0, column=1, sticky="w", padx=8)
        pages.bind("<<ComboboxSelected>>", self._on_pages_change)
        self._range_label = ttk.Label(config, text="Range", style="Card.TLabel")
        self._range_entry = ttk.Entry(config, textvariable=self.range_var, width=14)

        exempt_label = ttk.Label(config, text="Exempt pages", style="Card.TLabel")
        exempt_label.grid(row=2, column=0, sticky="w", pady=3)
        self._bind_icon(exempt_label, "actions", "file-minus", 16)
        ttk.Entry(config, textvariable=self.skip_var, width=18).grid(
            row=2, column=1, sticky="w", padx=8
        )
        ttk.Label(config, text="3 or 1,5,9-12", style="Muted.TLabel").grid(
            row=2, column=2, sticky="w"
        )

        ttk.Label(config, text="Position", style="Card.TLabel").grid(
            row=3, column=0, sticky="nw", pady=(10, 2)
        )
        positions = ttk.Frame(config, style="Card.TFrame")
        positions.grid(row=3, column=1, columnspan=2, sticky="w", padx=8, pady=(8, 4))
        for _code, position, row, column in self.POSITIONS:
            button = tk.Button(
                positions,
                text=position.replace("-", " ").title(),
                # Tk interprets width/height as pixels once an image is attached.
                width=145,
                height=30,
                relief="flat",
                font=(BODY_FONT, 8, "bold"),
                cursor="hand2",
                command=lambda value=position: self._select_position(value),
            )
            button.grid(row=row, column=column, padx=3, pady=3)
            self._pos_buttons[position] = button
            direction = position.replace("top", "up").replace("bottom", "down")
            self._bind_icon(button, "actions", f"move-{direction}", 15)

        sliders = [
            ("Size · % of page width", self.scale, 10, 100, 1, "expand"),
            (
                "Horizontal margin · inches",
                self.x_offset,
                0.1,
                2.0,
                0.1,
                "move-horizontal",
            ),
            (
                "Vertical margin · inches",
                self.y_offset,
                0.1,
                2.0,
                0.1,
                "move-vertical",
            ),
            ("Opacity · %", self.opacity, 10, 100, 1, "blend"),
            ("Rotation · degrees", self.rotation, 0, 360, 1, "rotate-cw"),
        ]
        for row, (label, variable, low, high, resolution, icon_name) in enumerate(sliders, start=5):
            slider_label = ttk.Label(config, text=label, style="Card.TLabel")
            slider_label.grid(row=row, column=0, sticky="w", pady=3)
            self._bind_icon(slider_label, "actions", icon_name, 15)
            value_label = ttk.Label(config, width=5, anchor="e", style="Card.TLabel")
            value_label.grid(row=row, column=2, padx=(4, 0))
            scale = ttk.Scale(
                config,
                from_=low,
                to=high,
                variable=variable,
                orient="horizontal",
                command=lambda value, target=value_label, step=resolution: self._on_slider(
                    value, target, step
                ),
            )
            scale.grid(row=row, column=1, sticky="ew", padx=8)
            self._on_slider(variable.get(), value_label, resolution)

        preview = ttk.LabelFrame(main, text=" Live preview ", style="Card.TLabelframe")
        preview.grid(row=2, column=1, sticky="nsew", padx=(6, 0))
        self.canvas = tk.Canvas(preview, width=260, height=330, highlightthickness=1)
        self.canvas.pack(expand=True)

        for variable in (
            self.position,
            self.scale,
            self.x_offset,
            self.y_offset,
            self.opacity,
            self.rotation,
            self.pages_var,
        ):
            variable.trace_add("write", lambda *_: self._update_preview())

        actions = ttk.Frame(main, style="App.TFrame")
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 10))
        sign_button = ttk.Button(
            actions,
            text="Sign selected PDF files",
            command=self._sign,
            style="Primary.TButton",
        )
        sign_button.pack(side="left")
        self._bind_icon(sign_button, "actions", "pen-line", 17)
        ttk.Label(
            actions,
            text="A new file is created; the original is not overwritten.",
            style="Subtitle.TLabel",
        ).pack(side="left", padx=(14, 0))

        activity = ttk.LabelFrame(main, text=" Activity ", style="Card.TLabelframe")
        activity.grid(row=4, column=0, columnspan=2, sticky="nsew")
        activity.columnconfigure(0, weight=1)
        self.log = tk.Text(
            activity,
            height=3,
            state="disabled",
            font=(MONO_FONT, 9),
            padx=12,
            pady=10,
            wrap="word",
        )
        self.log.grid(row=0, column=0, sticky="nsew")

    def _file_row(self, parent, row, label, variable, command, icon) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=5
        )
        ttk.Entry(parent, textvariable=variable).grid(
            row=row, column=1, sticky="ew", padx=(0, 8), pady=5
        )
        button = ttk.Button(parent, text="Browse…", command=command)
        button.grid(row=row, column=2, pady=5)
        self._bind_icon(button, icon[0], icon[1], 15)

    def _bind_icon(
        self,
        widget: Any,
        group: str,
        name: str,
        size: int,
        compound: str = "left",
    ) -> None:
        self._icon_targets.append((widget, group, name, size, compound))

    def _apply_icons(self) -> None:
        for widget, group, name, size, compound in self._icon_targets:
            image = self.icons.tk(group, name, size, self.theme)
            if image is not None:
                widget.configure(image=image, compound=compound)
        theme_name = "sun" if self.theme == "dark" else "moon"
        theme_icon = self.icons.tk("navigation", theme_name, 15, self.theme)
        if theme_icon is not None:
            self.theme_btn.configure(image=theme_icon, compound="left")

    def _apply_theme(self) -> None:
        self.palette = apply_ttk_theme(self.root, self.theme)
        style_text_widget(self.log, self.palette)
        self.canvas.configure(
            bg=self.palette.surface_sunken,
            highlightbackground=self.palette.border,
            highlightcolor=self.palette.focus,
        )
        self.theme_btn.configure(text="Light mode" if self.theme == "dark" else "Dark mode")
        self._apply_icons()
        self._select_position(self.position.get())
        self._update_preview()

    def _toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        save_theme(self.theme)
        self._apply_theme()

    def _browse_signature(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select signature PNG", filetypes=[("PNG image", "*.png")]
        )
        if selected:
            self.sig_path.set(selected)

    def _browse_input(self) -> None:
        if self.batch_mode.get():
            selected = filedialog.askdirectory(title="Select folder of PDFs")
        else:
            selected = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if selected:
            self.input_path.set(selected)
            self._auto_output(selected)

    def _browse_output(self) -> None:
        if self.batch_mode.get():
            selected = filedialog.askdirectory(title="Select output folder")
        else:
            selected = filedialog.asksaveasfilename(
                title="Save signed PDF as",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
            )
        if selected:
            self.output_path.set(selected)

    def _auto_output(self, input_value: str) -> None:
        source = Path(input_value)
        if self.batch_mode.get():
            self.output_path.set(str(source / "signed"))
        else:
            self.output_path.set(str(source.parent / f"{source.stem}_signed.pdf"))

    def _on_batch_toggle(self) -> None:
        if self.input_path.get():
            self._auto_output(self.input_path.get())

    def _on_pages_change(self, _event=None) -> None:
        if self.pages_var.get() == "range":
            self._range_label.grid(row=1, column=0, sticky="w")
            self._range_entry.grid(row=1, column=1, sticky="w", padx=8)
        else:
            self._range_label.grid_remove()
            self._range_entry.grid_remove()

    def _select_position(self, position: str) -> None:
        self.position.set(position)
        for value, button in self._pos_buttons.items():
            selected = value == position
            button.configure(
                bg=self.palette.accent if selected else self.palette.surface_sunken,
                activebackground=(
                    self.palette.accent_hover if selected else self.palette.surface_hover
                ),
                fg=self.palette.accent_text if selected else self.palette.text_primary,
                activeforeground=(
                    self.palette.accent_text if selected else self.palette.text_primary
                ),
                highlightthickness=1,
                highlightbackground=(self.palette.accent if selected else self.palette.border),
            )

    def _on_slider(self, value, label, resolution) -> None:
        number = float(value)
        label.configure(text=f"{number:.1f}" if resolution < 1 else str(round(number)))
        self._update_preview()

    def _update_preview(self) -> None:
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        canvas.delete("all")
        width, height, margin = 260, 330, 14
        page_height = height - 2 * margin
        page_width = page_height * (210 / 297)
        page_x = (width - page_width) / 2
        page_y = margin
        canvas.create_rectangle(
            page_x,
            page_y,
            page_x + page_width,
            page_y + page_height,
            fill=self.palette.surface_raised,
            outline=self.palette.border,
            width=2,
        )

        signature_width = page_width * (self.scale.get() / 100)
        signature_height = signature_width * 0.4
        horizontal = self.x_offset.get() * 20
        vertical = self.y_offset.get() * 20
        position = self.position.get()
        if position == "bottom-left":
            x = page_x + horizontal
            y = page_y + page_height - vertical - signature_height
        elif position == "bottom-right":
            x = page_x + page_width - horizontal - signature_width
            y = page_y + page_height - vertical - signature_height
        elif position == "top-left":
            x = page_x + horizontal
            y = page_y + vertical
        else:
            x = page_x + page_width - horizontal - signature_width
            y = page_y + vertical

        opacity = self.opacity.get() / 100
        stipple = "" if opacity > 0.7 else ("gray50" if opacity > 0.4 else "gray25")
        canvas.create_rectangle(
            x,
            y,
            x + signature_width,
            y + signature_height,
            fill=self.palette.accent_secondary,
            outline=self.palette.accent_secondary,
            width=1,
            stipple=stipple,
        )
        canvas.create_text(
            x + signature_width / 2,
            y + signature_height / 2,
            text="SIGN",
            fill=self.palette.surface_sunken,
            font=(BODY_FONT, 7, "bold"),
        )
        canvas.create_text(
            width // 2,
            height // 2,
            text=f"A4 · {int(self.rotation.get())}°",
            fill=self.palette.text_muted,
            font=(BODY_FONT, 9),
        )

    def _write_log(self, message: str) -> None:
        def append() -> None:
            self.log.configure(state="normal")
            self.log.insert("end", message + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")

        self.root.after(0, append)

    def _sign(self) -> None:
        signature = self.sig_path.get().strip()
        source = self.input_path.get().strip()
        output = self.output_path.get().strip()
        pages = (
            self.range_var.get().strip()
            if self.pages_var.get() == "range"
            else self.pages_var.get()
        )

        if not signature:
            messagebox.showerror("Signature needed", "Select a PNG signature image first.")
            return
        if not source:
            messagebox.showerror("PDF needed", "Select an input PDF or folder first.")
            return
        if not output:
            messagebox.showerror("Output needed", "Choose where the signed copy should be saved.")
            return

        def run() -> None:
            try:
                signer = self.signature_factory(
                    signature_image_path=signature,
                    position=self.position.get(),
                    scale=self.scale.get() / 100,
                    x_offset=self.x_offset.get(),
                    y_offset=self.y_offset.get(),
                    opacity=self.opacity.get() / 100,
                    rotation=self.rotation.get(),
                    pages=pages,
                    skip_pages=self.skip_var.get().strip(),
                )
                if self.batch_mode.get():
                    self._write_log(f"Signing folder: {source}")
                    result = signer.batch_sign_pdfs(source, output)
                    self._write_log(
                        f"Finished · {result['successful']} signed · {result['failed']} failed"
                    )
                else:
                    self._write_log(f"Signing: {source}")
                    result = signer.add_signature_to_pdf(source, output)
                    if result["success"]:
                        self._write_log(
                            "Finished · "
                            f"{result['pages_signed']}/{result['total_pages']} pages · "
                            f"{result['output_path']}"
                        )
                    else:
                        self._write_log(f"Could not sign PDF · {result['error']}")
            except Exception as exc:  # The worker reports third-party PDF failures in the UI.
                self._write_log(f"Could not sign PDF · {exc}")

        threading.Thread(target=run, daemon=True).start()


def launch_signature_gui(signature_factory: Callable[..., Any]) -> None:
    root = tk.Tk()
    SignatureApp(root, signature_factory)
    root.update_idletasks()
    width = max(root.winfo_reqwidth(), 980)
    height = max(root.winfo_reqheight(), 960)
    root.geometry(
        centered_geometry(
            width,
            height,
            root.winfo_screenwidth(),
            root.winfo_screenheight(),
        )
    )
    root.mainloop()
