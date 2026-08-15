#!/usr/bin/env python3
"""Mac desktop helper — buttons for dashboard and daily refresh (no Terminal)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

DASHBOARD_URL = "http://127.0.0.1:8080"
CONFIG_PATH = Path.home() / ".investment_agent" / "repo.path"
EXPECTED_VERSION = "0.9.0"


def _repo_from_argv() -> Path | None:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        p = Path(sys.argv[1]).expanduser().resolve()
        if (p / "scripts" / "run_dashboard.py").is_file():
            return p
    return None


def _repo_from_config() -> Path | None:
    if CONFIG_PATH.is_file():
        p = Path(CONFIG_PATH.read_text(encoding="utf-8").strip()).expanduser().resolve()
        if (p / "scripts" / "run_dashboard.py").is_file():
            return p
    return None


def discover_repo() -> Path | None:
    env = os.environ.get("INVESTMENT_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "scripts" / "run_dashboard.py").is_file():
            return p
    for candidate in (_repo_from_argv(), _repo_from_config()):
        if candidate:
            return candidate
    # App bundle layout: repo/desktop/AI Investment Agent.app/Contents/MacOS/launcher
    here = Path(__file__).resolve().parent.parent
    if (here / "scripts" / "run_dashboard.py").is_file():
        return here
    return None


def save_repo(path: Path) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(str(path.resolve()) + "\n", encoding="utf-8")


class DesktopHelperApp:
    def __init__(self, root: tk.Tk, repo: Path) -> None:
        self.root = root
        self.repo = repo
        self.running = False
        self.root.title("AI Investment Agent")
        self.root.minsize(420, 520)
        self.root.geometry("480x580")
        self._build_ui()
        self.refresh_status()
        self.log(f"Project folder: {self.repo}")

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 4}
        header = ttk.Frame(self.root)
        header.pack(fill="x", **pad)
        ttk.Label(header, text="AI Investment Agent", font=("Helvetica", 16, "bold")).pack(anchor="w")
        self.status_label = ttk.Label(header, text="Checking dashboard…", font=("Helvetica", 11))
        self.status_label.pack(anchor="w", pady=(4, 0))
        self.version_label = ttk.Label(header, text="", font=("Helvetica", 10))
        self.version_label.pack(anchor="w")

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", pady=8)

        primary = ttk.LabelFrame(self.root, text="Dashboard", padding=10)
        primary.pack(fill="x", **pad)
        ttk.Button(primary, text="Update & Open Dashboard", command=self.update_and_open).pack(
            fill="x", pady=3
        )
        ttk.Button(primary, text="Open Dashboard in Browser", command=self.open_browser).pack(
            fill="x", pady=3
        )

        rhythm = ttk.LabelFrame(self.root, text="Daily rhythm (no Terminal)", padding=10)
        rhythm.pack(fill="x", **pad)
        ttk.Button(rhythm, text="Morning Prep", command=self.morning_prep).pack(fill="x", pady=3)
        ttk.Button(
            rhythm,
            text="Refresh Live — before buy/sell (Step 3)",
            command=self.refresh_live,
        ).pack(fill="x", pady=3)
        ttk.Button(rhythm, text="End of Day", command=self.end_of_day).pack(fill="x", pady=3)

        other = ttk.LabelFrame(self.root, text="Other", padding=10)
        other.pack(fill="x", **pad)
        ttk.Button(other, text="Stop Background Dashboard", command=self.stop_background).pack(
            fill="x", pady=3
        )
        ttk.Button(other, text="Open Operator Checklist (PDF)", command=self.open_checklist).pack(
            fill="x", pady=3
        )
        ttk.Button(other, text="Change project folder…", command=self.pick_repo).pack(fill="x", pady=3)

        log_frame = ttk.LabelFrame(self.root, text="Activity log", padding=8)
        log_frame.pack(fill="both", expand=True, **pad)
        self.log_box = scrolledtext.ScrolledText(log_frame, height=10, font=("Menlo", 10))
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def log(self, msg: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg.rstrip() + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def refresh_status(self) -> None:
        def worker() -> None:
            try:
                with urllib.request.urlopen(f"{DASHBOARD_URL}/api/version", timeout=2) as resp:
                    data = json.loads(resp.read().decode())
                label = data.get("label") or f"v{data.get('version', '?')}"
                version = data.get("version", "?")
                if version == EXPECTED_VERSION:
                    text = f"Dashboard running · {label}"
                else:
                    text = f"Dashboard running · {label} (update recommended)"
                self.root.after(0, lambda: self.status_label.configure(text=text))
                self.root.after(0, lambda: self.version_label.configure(text=""))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                self.root.after(
                    0,
                    lambda: self.status_label.configure(
                        text="Dashboard not running — click Update & Open Dashboard"
                    ),
                )
                self.root.after(
                    0,
                    lambda: self.version_label.configure(
                        text=f"Latest release: v{EXPECTED_VERSION} · Phase 1B"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    def _run_script(self, title: str, script: Path, *, open_browser_after: bool = False) -> None:
        if self.running:
            messagebox.showinfo("Please wait", "Another task is still running.")
            return
        if not script.is_file():
            messagebox.showerror("Missing script", f"Not found:\n{script}")
            return
        self.running = True
        self.log(f"── {title} ──")

        def worker() -> None:
            try:
                proc = subprocess.Popen(
                    ["/bin/bash", str(script)],
                    cwd=self.repo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    self.root.after(0, lambda l=line: self.log(l.rstrip()))
                code = proc.wait()
                self.root.after(0, lambda: self.log(f"Finished (exit {code})"))
                if open_browser_after and code == 0:
                    self.root.after(0, self.open_browser)
            except Exception as exc:
                self.root.after(0, lambda: self.log(f"ERROR: {exc}"))
            finally:
                self.running = False
                self.root.after(0, self.refresh_status)

        threading.Thread(target=worker, daemon=True).start()

    def update_and_open(self) -> None:
        git = subprocess.run(
            ["git", "-C", str(self.repo), "pull", "--ff-only", "origin", "main"],
            capture_output=True,
            text=True,
        )
        if git.stdout.strip():
            self.log(git.stdout.strip())
        if git.returncode != 0 and git.stderr.strip():
            self.log(git.stderr.strip())
        self._run_script(
            "Update & open dashboard",
            self.repo / "scripts" / "hard_restart_dashboard_mac.sh",
            open_browser_after=True,
        )

    def open_browser(self) -> None:
        webbrowser.open(DASHBOARD_URL)
        self.log(f"Opened {DASHBOARD_URL}")

    def morning_prep(self) -> None:
        self._run_script("Morning prep", self.repo / "scripts" / "run_morning_prep_mac.sh")

    def refresh_live(self) -> None:
        self._run_script("Refresh live", self.repo / "scripts" / "run_refresh_live_mac.sh")

    def end_of_day(self) -> None:
        self._run_script("End of day", self.repo / "scripts" / "run_end_of_day_mac.sh")

    def stop_background(self) -> None:
        script = self.repo / "scripts" / "uninstall_dashboard_service_mac.sh"
        self._run_script("Stop background dashboard", script)

    def open_checklist(self) -> None:
        webbrowser.open(f"{DASHBOARD_URL}/operator-checklist.pdf")
        self.log("Opened operator checklist PDF")

    def pick_repo(self) -> None:
        chosen = filedialog.askdirectory(title="Select Home-Repository folder", initialdir=str(self.repo))
        if not chosen:
            return
        path = Path(chosen)
        if not (path / "scripts" / "run_dashboard.py").is_file():
            messagebox.showerror("Invalid folder", "That folder is not Home-Repository.")
            return
        self.repo = path
        save_repo(path)
        self.log(f"Project folder set to: {path}")


def main() -> None:
    repo = discover_repo()
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 2.0)
    except tk.TclError:
        pass
    style = ttk.Style()
    if sys.platform == "darwin":
        style.theme_use("aqua")

    if repo is None:
        chosen = filedialog.askdirectory(title="Select your Home-Repository folder")
        if not chosen:
            sys.exit(0)
        repo = Path(chosen)
        if not (repo / "scripts" / "run_dashboard.py").is_file():
            messagebox.showerror("Invalid folder", "Please select the Home-Repository project root.")
            sys.exit(1)
        save_repo(repo)

    DesktopHelperApp(root, repo)
    root.mainloop()


if __name__ == "__main__":
    main()
