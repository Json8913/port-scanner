#!/usr/bin/env python3
"""Desktop interface for the authorised-lab TCP port scanner."""

import ipaddress
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk


BG = "#0b1220"
PANEL = "#121d2e"
TEXT = "#edf4ff"
MUTED = "#9bacbf"
ACCENT = "#45d6c5"


class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner")
        self.geometry("820x600")
        self.minsize(700, 520)
        self.configure(bg=BG)
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Arial", 10))
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT)
        style.configure("TEntry", fieldbackground="#0f1928", foreground=TEXT,
                        insertcolor=TEXT, bordercolor="#31445b")
        style.configure("TButton", padding=(12, 8), background="#24364b",
                        foreground=TEXT, borderwidth=0)
        style.map("TButton", background=[("active", "#304963")])
        style.configure("Accent.TButton", background=ACCENT, foreground="#07131b",
                        font=("Arial", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#70e8d9")])

    def _build(self):
        shell = ttk.Frame(self, padding=24)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="NETWORK TOOLS  /  TCP", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(shell, text="Port Scanner", font=("Arial", 25, "bold")).pack(anchor="w", pady=(6, 4))
        ttk.Label(shell, text="Scan only systems you own or have permission to assess.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 18))

        card = ttk.Frame(shell, style="Card.TFrame", padding=18)
        card.pack(fill="x")
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x")
        self.host = tk.StringVar(value="127.0.0.1")
        self.ports = tk.StringVar(value="1-1024")
        for label, variable, width in (("Private or loopback IP", self.host, 24),
                                       ("Port range (max 4096)", self.ports, 18)):
            block = ttk.Frame(row, style="Card.TFrame")
            block.pack(side="left", padx=(0, 14))
            ttk.Label(block, text=label, style="Card.TLabel").pack(anchor="w", pady=(0, 6))
            ttk.Entry(block, textvariable=variable, width=width).pack()
        self.run_button = ttk.Button(row, text="Run scan", style="Accent.TButton", command=self.scan)
        self.run_button.pack(side="right", anchor="s", pady=(24, 0))

        self.status = tk.StringVar(value="Ready. Default scope is this computer.")
        ttk.Label(shell, textvariable=self.status, style="Muted.TLabel").pack(anchor="w", pady=(16, 8))
        self.output = tk.Text(shell, bg="#070d16", fg=TEXT, insertbackground=TEXT,
                              relief="flat", padx=16, pady=14, font=("Menlo", 11),
                              wrap="word")
        self.output.pack(fill="both", expand=True)
        self.output.insert("end", "Results will appear here.\n")
        self.output.configure(state="disabled")

    def scan(self):
        try:
            address = ipaddress.ip_address(self.host.get().strip())
            if not (address.is_private or address.is_loopback):
                raise ValueError("Only loopback and private addresses are allowed.")
            start, end = [int(part) for part in self.ports.get().split("-", 1)]
            if not (1 <= start <= end <= 65535) or end - start > 4095:
                raise ValueError("Enter a valid range covering no more than 4096 ports.")
        except (ValueError, TypeError) as exc:
            self.status.set(str(exc))
            return
        self.run_button.configure(state="disabled")
        self.status.set(f"Scanning {address} on {end - start + 1} TCP ports…")
        self._set_output("")
        threading.Thread(target=self._run, args=(str(address), f"{start}-{end}"), daemon=True).start()

    def _run(self, host, ports):
        result = subprocess.run(
            [sys.executable, "port_scanner.py", host, "--ports", ports, "--json", "--delay", "0"],
            capture_output=True, text=True, timeout=180
        )
        self.after(0, self._finish, result)

    def _finish(self, result):
        self.run_button.configure(state="normal")
        self.status.set("Scan finished." if result.returncode == 0 else "Scan could not be completed.")
        self._set_output(result.stdout if result.returncode == 0 else result.stderr)

    def _set_output(self, value):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", value or "No results.")
        self.output.configure(state="disabled")


if __name__ == "__main__":
    ScannerApp().mainloop()
