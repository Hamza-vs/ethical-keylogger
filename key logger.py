#!/usr/bin/env python3
"""
Safe typing-practice app.
Records keystrokes only while the app window is focused, and only if the user consents.
Saves a simple CSV with timestamp and key.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from datetime import datetime

class TypingPracticeApp:
    def _init_(self, root):
        self.root = root
        root.title("Typing Practice (Safe Logger)")

        self.logging = False
        self.log = []  # list of (timestamp_iso, key_symbol)

        # UI
        self.instructions = tk.Label(root, text="Type in the box below. Check consent and press Start to record.")
        self.instructions.pack(padx=8, pady=(8, 0))

        self.consent_var = tk.IntVar()
        self.consent_chk = tk.Checkbutton(
            root,
            text="I consent to local logging of my keystrokes (for practice only)",
            variable=self.consent_var
        )
        self.consent_chk.pack(anchor="w", padx=8, pady=(4, 6))

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=8)

        self.start_btn = tk.Button(btn_frame, text="Start Recording", command=self.start_recording)
        self.start_btn.pack(side="left", padx=(0, 4))

        self.stop_btn = tk.Button(btn_frame, text="Stop & Save", command=self.stop_and_save, state="disabled")
        self.stop_btn.pack(side="left")

        self.clear_btn = tk.Button(btn_frame, text="Clear Log", command=self.clear_log)
        self.clear_btn.pack(side="right")

        self.text = tk.Text(root, width=80, height=12, wrap="word")
        self.text.pack(padx=8, pady=8)
        self.text.focus_set()

        self.status = tk.Label(root, text="Status: idle", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 8))

        # Bind key events only on the text widget (so logging is in-app)
        self.text.bind("<Key>", self.on_key)

    def on_key(self, event):
        """Record keystrokes when logging is enabled and consent is given."""
        if not self.logging:
            return

        if self.root.focus_get() is None or not self.consent_var.get():
            return

        ks = event.keysym
        ts = datetime.utcnow().isoformat() + "Z"
        self.log.append((ts, ks))
        self.status.config(text=f"Logging: {len(self.log)} events — last: {ks}")

    def start_recording(self):
        if not self.consent_var.get():
            messagebox.showwarning("Consent required", "Please check the consent box to enable logging.")
            return
        self.logging = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text="Logging: 0 events")

    def stop_and_save(self):
        if not self.logging:
            return
        self.logging = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        if not self.log:
            messagebox.showinfo("No data", "No keystrokes were recorded.")
            self.status.config(text="Status: stopped (no data)")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", ".csv"), ("All files", ".*")],
            title="Save keystroke log (local file)"
        )
        if not filename:
            self.status.config(text="Status: stopped (not saved)")
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp_utc_iso", "key"])
                writer.writerows(self.log)
            messagebox.showinfo("Saved", f"Saved {len(self.log)} events to:\n{filename}")
            self.status.config(text=f"Status: saved {len(self.log)} events")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            self.status.config(text="Status: stopped (save failed)")

    def clear_log(self):
        if messagebox.askyesno("Clear log", "Clear all recorded events?"):
            self.log.clear()
            self.status.config(text="Status: cleared")

# Main program entry point
if __name__ == "_main_":
    root = tk.Tk()
    app = TypingPracticeApp(root)
    root.mainloop()