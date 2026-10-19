import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from cmm import CMM
class CMMIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("CMM IDE")
        self.root.geometry("900x650")
        self.filename = None
        self.issafemode = True
        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x", padx=5, pady=5)
        ttk.Button(
            toolbar,
            text="▶ Run code",
            command=self.run_code
        ).pack(side="left", padx=10)
        ttk.Button(
            toolbar,
            text="📄 New",
            command=self.new_file
        ).pack(side="left", padx=2)
        ttk.Button(
            toolbar,
            text="📁 Open",
            command=self.open_file
        ).pack(side="left", padx=2)
        ttk.Button(
            toolbar,
            text="💾 Save",
            command=self.save_file
        ).pack(side="left", padx=2)
        self.disable_safemode_button = ttk.Button(
            toolbar,
            text="⚠️ Disable safe mode ⚠️",
            command=self.disable_safemode
        )
        self.disable_safemode_button.pack(side="left", padx=2)
        editor_frame = ttk.LabelFrame(
            root,
            text="Editor"
        )
        editor_frame.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )
        self.editor = tk.Text(
            editor_frame,
            wrap="none",
            font=("Consolas", 12),
            undo=True
        )
        self.editor.pack(
            fill="both",
            expand=True,
            side="left"
        )
        editor_scroll = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=self.editor.yview
        )
        editor_scroll.pack(
            side="right",
            fill="y"
        )
        self.editor.configure(
            yscrollcommand=editor_scroll.set
        )
        console_frame = ttk.LabelFrame(
            root,
            text="CMM Console"
        )
        console_frame.pack(
            fill="both",
            expand=False,
            padx=5,
            pady=5
        )
        self.console = tk.Text(
            console_frame,
            height=12,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Consolas", 11),
            state="disabled"
        )
        self.console.pack(
            fill="both",
            expand=True
        )
        self.root.bind(
            "<F5>",
            lambda event: self.run_code()
        )
        self.root.bind(
            "<Control-O>",
            lambda event: self.open_file()
        )
        self.root.bind(
            "<Control-o>",
            lambda event: self.open_file()
        )
        self.root.bind(
            "<Control-S>",
            lambda event: self.save_file()
        )
        self.root.bind(
            "<Control-s>",
            lambda event: self.save_file()
        )
        self.root.bind(
            "<Control-N>",
            lambda event: self.new_file()
        )
        self.root.bind(
            "<Control-n>",
            lambda event: self.new_file()
        )
        self.new_file()
    def write_console(self, text="", end="\n"):
        self.console.configure(state="normal")
        self.console.insert("end", str(text)+end)
        self.console.see("end")
        self.console.configure(state="disabled")
    def disable_safemode(self):
        confirm = messagebox.askyesno(
            "Disable SafeMode",
            "¿Are you sure that you want to disable the safe mode?\n* If you want to enable the safe mode, close and reopen the IDE"
        )
        if confirm:
            self.issafemode = False
            self.disable_safemode_button.destroy()
    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
    def new_file(self):
        self.filename = None
        self.editor.delete("1.0", "end")
        self.editor.insert(1.0, "cmm-pr(txt(Hello world!)).")
        self.root.title("CMM IDE - Untitled")
    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("CMM files", "*.cmm"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                code = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", code)
            self.filename = path
            self.root.title(
                f"CMM IDE - {path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )
    def save_file(self):
        if self.filename is None:
            self.filename = filedialog.asksaveasfilename(
                defaultextension=".cmm",
                filetypes=[
                    ("CMM files", "*.cmm"),
                    ("All files", "*.*")
                ]
            )
            if not self.filename:
                self.filename = None
                return
        try:
            code = self.editor.get(
                "1.0",
                "end-1c"
            )
            with open(
                self.filename,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)
            self.root.title(
                f"CMM IDE - {self.filename}"
            )
            self.write_console(
                f"Saved: {self.filename}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )
    def IDE_input(self, prompt=""):
        self.write_console(prompt, end="")
        value = simpledialog.askstring(
            "CMM Input",
            prompt
        )
        if value is None:
            return ""
        self.write_console(value)
        return value
    def run_code(self):
        code = self.editor.get(
            "1.0",
            "end-1c"
        )
        if not code.strip():
            return
        self.clear_console()
        try:
            vm = CMM(
                file=None,
                prompt=code,
                stdout=self.write_console,
                stdin=self.IDE_input,
                safemode=self.issafemode
            )
            val = vm()
            self.write_console()
            self.write_console( "    [DONE]")
            self.write_console(f"    CMM code exited with code={val}")
        except BaseException as e:
            self.write_console(
                f"{type(e).__name__}: {e}"
            )
root = tk.Tk()
app = CMMIDE(root)
root.mainloop()
