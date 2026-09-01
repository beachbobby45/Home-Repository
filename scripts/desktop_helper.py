#!/usr/bin/env python3
"""Mac desktop helper — buttons for dashboard and daily refresh (no Terminal)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")  # kept for compatibility; log() inlines ZoneInfo

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
except ImportError as exc:
    print(f"ERROR: tkinter is required for the desktop app: {exc}", file=sys.stderr)
    print("Mac fix: brew install python-tk@3.12  (or use python.org installer)", file=sys.stderr)
    sys.exit(1)

DASHBOARD_URL = "http://127.0.0.1:8080"
CONFIG_PATH = Path.home() / ".investment_agent" / "repo.path"
LOG_PATH = Path.home() / ".investment_agent" / "desktop-app.log"
LAST_RUN_LOG = Path.home() / ".investment_agent" / "last-run.log"
EXPECTED_VERSION = "0.9.3"
DESKTOP_HELPER_BUILD = "20260901a"


def _save_last_run_log(title: str, lines: list[str], exit_code: int) -> Path:
    """Write full script output so Tony can open it in TextEdit (Activity log is hard to copy)."""
    LAST_RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"=== {title} · exit {exit_code} · {stamp} ===\n\n"
    LAST_RUN_LOG.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return LAST_RUN_LOG


def _open_path_in_editor(path: Path) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "TextEdit", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def _ingest_errors_from_disk(repo: Path) -> list[str]:
    """Read the last ingest failure written by run_ingest.py (survives scroll/buffer issues)."""
    err_file = repo / "data" / "ingest_last_error.txt"
    if err_file.is_file():
        lines = [ln.strip() for ln in err_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return [ln for ln in lines if not ln.startswith("Fix:")][:14]
    last_run = repo / "data" / "ingest_last_run.json"
    if last_run.is_file():
        try:
            data = json.loads(last_run.read_text(encoding="utf-8"))
            if not data.get("ok") and data.get("errors"):
                return [f"• {err}" for err in data["errors"][:12]]
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _failure_lines_for_task(
    all_lines: list[str],
    repo: Path,
    *,
    task_key: str,
) -> list[str]:
    disk = _ingest_errors_from_disk(repo) if task_key in (
        "end_of_day",
        "ingest",
        "morning_prep",
        "refresh_live",
    ) else []
    if disk:
        return disk
    parsed = _extract_failure_lines(all_lines)
    if parsed:
        return parsed
    return disk


def _extract_failure_lines(lines: list[str]) -> list[str]:
    """Pull ERROR / ingest failure lines out of script output (skip cleanup boilerplate)."""
    if not lines:
        return []
    skip_sub = (
        "Restarting dashboard",
        "Dashboard back at",
        "Dashboard was restarted",
        "Scroll up in the Activity log",
        "Ingest failed (exit",
        "── Ingest errors ──",
    )
    hits: list[str] = []
    capture = False
    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        if capture:
            if (
                text.startswith("Fix:")
                or text.startswith("•")
                or raw.lstrip().startswith("•")
                or text.startswith("…")
            ):
                hits.append(text)
                continue
            capture = False
        lower = text.lower()
        if text.startswith("ERROR:") or "preflight failed" in lower:
            hits.append(text)
        elif "INGEST FAILED" in text or text == "── Ingest errors ──":
            hits.append(text)
            capture = True
        elif (
            "Dashboard failed to load" in text
            or "Could not set up Python" in text
            or text == "--- import error ---"
        ):
            hits.append(text)
            capture = True
        elif capture and ('File "' in text or text.startswith("ModuleNotFoundError") or text.startswith("ImportError")):
            hits.append(text)
        elif (text.startswith("•") or raw.lstrip().startswith("•")) and hits:
            hits.append(text)
        elif "incompatible architecture" in lower or "unable to import required dependency numpy" in lower:
            hits.append("ERROR: Python/NumPy architecture mismatch (see log above)")
            hits.append("Fix: double-click scripts/Fix Ingest Python.command")
            capture = True
    if hits:
        return hits[-12:]
    # Fallback: last non-boilerplate lines
    fallback = [
        ln.strip()
        for ln in lines
        if ln.strip() and not any(s in ln for s in skip_sub)
    ]
    return fallback[-8:]


def _log_startup(msg: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] {msg}\n")
    except OSError:
        pass


def _fatal_startup(msg: str) -> None:
    _log_startup(f"FATAL: {msg}")
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "AI Investment Agent — could not start",
            msg + f"\n\nDetails saved to:\n{LOG_PATH}",
        )
        root.destroy()
    except Exception:
        pass
    sys.exit(1)


def _bootstrap_import_path() -> None:
    """Ensure src/ is on sys.path before investment_agent imports."""
    for candidate in (
        os.environ.get("INVESTMENT_AGENT_ROOT", "").strip(),
        sys.argv[1].strip() if len(sys.argv) > 1 else "",
    ):
        if not candidate:
            continue
        src = Path(candidate).expanduser().resolve() / "src"
        if src.is_dir():
            src_str = str(src)
            if src_str not in sys.path:
                sys.path.insert(0, src_str)
            return
    here = Path(__file__).resolve().parent.parent / "src"
    if here.is_dir():
        here_str = str(here)
        if here_str not in sys.path:
            sys.path.insert(0, here_str)


_bootstrap_import_path()

# Populated in main() after Tk is ready (avoids silent import crash before UI).
fetch_rhythm_status = None
format_last_run = None
now_pt_label = None


def _load_desktop_status() -> None:
    global fetch_rhythm_status, format_last_run, now_pt_label
    try:
        from investment_agent.desktop_status import (
            fetch_rhythm_status as _fetch,
            format_last_run as _fmt,
            now_pt_label as _now,
        )
    except ImportError as exc:
        _fatal_startup(
            "Could not load the project code (investment_agent).\n"
            f"Import error: {exc}\n\n"
            "Reinstall: Home-Repository/scripts/Install Desktop App.command"
        )
    fetch_rhythm_status = _fetch
    format_last_run = _fmt
    now_pt_label = _now

# task_key → (button label, script name, rhythm step id for last-run display)
RHYTHM_TASKS: tuple[tuple[str, str, str, str], ...] = (
    (
        "morning_prep",
        "Morning Prep",
        "run_morning_prep_mac.sh",
        "pre_market",
    ),
    (
        "refresh_live",
        "Refresh Live — before buy/sell (Step 3)",
        "run_refresh_live_mac.sh",
        "before_buy",
    ),
    (
        "end_of_day",
        "End of Day",
        "run_end_of_day_mac.sh",
        "after_close",
    ),
)


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
        self.current_task = ""
        self.current_task_key = ""
        self.task_started_pt = ""
        self._clear_status_after_id: str | None = None
        self.dashboard_pause_expected = False
        self.rhythm_last_labels: dict[str, ttk.Label] = {}
        self.rhythm_buttons: dict[str, ttk.Button] = {}

        self.root.title("AI Investment Agent")
        self.root.minsize(460, 640)
        self.root.geometry("500x700")
        self._build_ui()
        self.refresh_status()
        self.refresh_rhythm_labels()
        self.log(f"Project folder: {self.repo}")

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 4}
        header = ttk.Frame(self.root)
        header.pack(fill="x", **pad)
        ttk.Label(header, text="AI Investment Agent", font=("Helvetica", 16, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text=f"Desktop helper · build {DESKTOP_HELPER_BUILD}",
            font=("Helvetica", 9),
        ).pack(anchor="w")
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

        self.task_banner = ttk.Label(
            rhythm,
            text="Ready — pick a step below",
            font=("Helvetica", 11, "bold"),
            wraplength=440,
        )
        self.task_banner.pack(fill="x", pady=(0, 6))

        self.progress = ttk.Progressbar(rhythm, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.stop()
        self.progress.pack_forget()

        for task_key, label, script_name, step_id in RHYTHM_TASKS:
            row = ttk.Frame(rhythm)
            row.pack(fill="x", pady=(0, 6))
            last_lbl = ttk.Label(row, text="Last run: loading…", font=("Helvetica", 9))
            last_lbl.pack(anchor="w")
            self.rhythm_last_labels[task_key] = last_lbl
            btn = ttk.Button(
                row,
                text=label,
                command=lambda k=task_key, s=script_name, t=label: self._start_rhythm_task(k, s, t),
            )
            btn.pack(fill="x", pady=(2, 0))
            self.rhythm_buttons[task_key] = btn

        hint = ttk.Label(
            rhythm,
            text=(
                "End of Day can take 15–30 min. If something fails, use Activity log → "
                "Open last run log (full output in TextEdit)."
            ),
            font=("Helvetica", 9),
            wraplength=440,
        )
        hint.pack(anchor="w", pady=(4, 0))

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
        log_tools = ttk.Frame(log_frame)
        log_tools.pack(fill="x", pady=(0, 6))
        ttk.Button(log_tools, text="Copy activity log", command=self.copy_activity_log).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(log_tools, text="Open last run log", command=self.open_last_run_log).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(log_tools, text="Open ingest error", command=self.open_ingest_error).pack(
            side="left"
        )
        ttk.Label(
            log_tools,
            text="Tip: last run log opens in TextEdit — select all (Cmd+A) and copy.",
            font=("Helvetica", 9),
        ).pack(side="left", padx=(8, 0))
        self.log_box = scrolledtext.ScrolledText(log_frame, height=12, font=("Menlo", 10))
        self.log_box.pack(fill="both", expand=True)
        # Read-only but selectable (disabled Text blocks copy on some Mac builds).
        self.log_box.bind("<Key>", self._log_box_key)

    def _log_box_key(self, event: tk.Event) -> str | None:
        """Allow Cmd/Ctrl+C and Cmd/Ctrl+A; block edits."""
        if event.state & 0x4 and event.keysym.lower() in ("c", "a", "copy"):
            return None
        if event.keysym in ("Up", "Down", "Left", "Right", "Prior", "Next", "Home", "End"):
            return None
        return "break"

    def log(self, msg: str) -> None:
        local = datetime.now(ZoneInfo("America/Los_Angeles"))
        hour = local.hour % 12 or 12
        stamp = f"{hour}:{local.strftime('%M:%S %p')}"
        self.log_box.insert("end", f"[{stamp}] {msg.rstrip()}\n")
        self.log_box.see("end")

    def copy_activity_log(self) -> None:
        text = self.log_box.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Activity log", "Log is empty.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update_idletasks()
        self.log("Copied Activity log to clipboard — paste with Cmd+V.")

    def open_last_run_log(self) -> None:
        if not LAST_RUN_LOG.is_file():
            messagebox.showinfo(
                "Last run log",
                f"No run log yet.\n\nAfter Morning Prep, Refresh Live, or End of Day,\n"
                f"output is saved to:\n{LAST_RUN_LOG}",
            )
            return
        _open_path_in_editor(LAST_RUN_LOG)
        self.log(f"Opened {LAST_RUN_LOG}")

    def open_ingest_error(self) -> None:
        path = self.repo / "data" / "ingest_last_error.txt"
        if not path.is_file():
            messagebox.showinfo(
                "Ingest error",
                "No ingest error file yet.\n\n"
                f"Expected after a failed End of Day:\n{path}\n\n"
                "Or run: ./scripts/doctor_ingest_mac.sh",
            )
            return
        _open_path_in_editor(path)
        self.log(f"Opened {path}")

    def _set_task_banner(self, text: str, *, running: bool = False) -> None:
        self.task_banner.configure(text=text)
        if running:
            if not self.progress.winfo_ismapped():
                self.progress.pack(fill="x", pady=(0, 8), after=self.task_banner)
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.pack_forget()

    def _set_rhythm_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in self.rhythm_buttons.values():
            btn.configure(state=state)

    def refresh_rhythm_labels(self) -> None:
        def worker() -> None:
            if fetch_rhythm_status is None:
                return
            status = fetch_rhythm_status(self.repo)
            step_times: dict[str, str | None] = {}
            if status:
                for step in status.get("steps") or []:
                    step_times[step.get("id", "")] = step.get("last_at")

            def apply() -> None:
                for task_key, _, _, step_id in RHYTHM_TASKS:
                    lbl = self.rhythm_last_labels.get(task_key)
                    if lbl:
                        lbl.configure(text=format_last_run(step_times.get(step_id)))

            self.root.after(0, apply)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_status(self) -> None:
        def worker() -> None:
            if self.dashboard_pause_expected or (
                self.running and self.current_task_key == "end_of_day"
            ):
                self.root.after(
                    0,
                    lambda: self.status_label.configure(
                        text="Dashboard paused for End of Day ingest (normal — ~15–25 min)"
                    ),
                )
                return
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

    def _busy(self) -> bool:
        return self.running

    def _start_rhythm_task(self, task_key: str, script_name: str, title: str) -> None:
        if task_key == "end_of_day":
            self.dashboard_pause_expected = True
            self.status_label.configure(
                text="Dashboard will pause during ingest (browser may say not connected)"
            )
        script = self.repo / "scripts" / script_name
        self._run_script(title, script, task_key=task_key)

    def _run_script(
        self,
        title: str,
        script: Path,
        *,
        task_key: str = "",
        open_browser_after: bool = False,
        script_args: list[str] | None = None,
    ) -> None:
        if self._busy():
            messagebox.showinfo(
                "Please wait",
                f"Still running: {self.current_task or 'background task'}\n\n"
                "Watch the progress bar and Activity log at the bottom.",
            )
            return
        if not script.is_file():
            messagebox.showerror("Missing script", f"Not found:\n{script}")
            return

        self.running = True
        self.current_task = title
        self.current_task_key = task_key
        self.task_started_pt = now_pt_label() if now_pt_label else datetime.now().strftime("%H:%M")
        self._set_rhythm_buttons_enabled(False)
        self._set_task_banner(f"Running: {title} — started {self.task_started_pt}", running=True)
        self.log(f"── {title} — started {self.task_started_pt} ──")

        def worker() -> None:
            exit_code = 1
            all_lines: list[str] = []
            cmd = ["/bin/bash", str(script)]
            if script_args:
                cmd.extend(script_args)
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=self.repo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    text = line.rstrip()
                    all_lines.append(text)
                    self.root.after(0, lambda l=text: self.log(l))
                exit_code = proc.wait()
                finished = now_pt_label() if now_pt_label else datetime.now().strftime("%H:%M")
                if exit_code == 0:
                    self.root.after(
                        0,
                        lambda: self.log(f"✓ {title} finished successfully at {finished}"),
                    )
                else:
                    failure_lines = _failure_lines_for_task(
                        all_lines, self.repo, task_key=task_key
                    )
                    if failure_lines:
                        def log_summary(fl: list[str] = failure_lines) -> None:
                            self.log("── Failure reason ──")
                            for ln in fl:
                                self.log(ln)
                        self.root.after(0, log_summary)
                    self.root.after(
                        0,
                        lambda: self.log(f"✗ {title} failed (exit {exit_code}) at {finished}"),
                    )
                if open_browser_after and exit_code == 0:
                    def open_after_restart() -> None:
                        if self._open_dashboard_browser(wait=True):
                            messagebox.showinfo(
                                "Dashboard ready",
                                f"Dashboard is running at {DASHBOARD_URL}\n\n"
                                "If the page shows 'connection failed', wait 2 seconds "
                                "and press Cmd+Shift+R to hard-refresh.",
                            )
                        else:
                            messagebox.showerror(
                                "Dashboard not responding",
                                f"Restart finished but {DASHBOARD_URL} did not respond.\n\n"
                                "In Activity log, scroll up for errors.\n"
                                "Or run in Terminal:\n"
                                "  ./scripts/doctor_dashboard_mac.sh",
                            )

                    self.root.after(0, open_after_restart)
            except Exception as exc:
                self.root.after(0, lambda: self.log(f"ERROR: {exc}"))
            finally:
                if all_lines:
                    saved = _save_last_run_log(title, all_lines, exit_code)
                    self.root.after(
                        0,
                        lambda p=saved: self.log(f"Full output saved: {p}"),
                    )

                def finish_ui() -> None:
                    self.running = False
                    finished = now_pt_label() if now_pt_label else datetime.now().strftime("%H:%M")
                    if exit_code == 0:
                        banner = f"✓ {title} completed at {finished}"
                        self._set_task_banner(banner, running=False)
                        if task_key == "end_of_day":
                            messagebox.showinfo(
                                "End of Day complete",
                                f"Finished at {finished}.\n\n"
                                "Dashboard is restarting at http://127.0.0.1:8080\n\n"
                                "Tomorrow: run Morning Prep before the open, "
                                "then Refresh Live right before you buy.",
                            )
                        elif task_key:
                            messagebox.showinfo(f"{title} complete", f"Finished at {finished}.")
                    else:
                        banner = f"✗ {title} failed — see Activity log ({finished})"
                        self._set_task_banner(banner, running=False)
                        failure_lines = _failure_lines_for_task(
                            all_lines, self.repo, task_key=task_key
                        )
                        hint = (
                            "\n".join(failure_lines)
                            if failure_lines
                            else "(no error detail captured — scroll up in Activity log)"
                        )
                        extra = (
                            f"\n\nFull log saved to:\n{LAST_RUN_LOG}\n"
                            "In the app: Activity log → Open last run log (TextEdit).\n"
                            "Or: Activity log → Copy activity log."
                        )
                        if task_key in ("end_of_day", "morning_prep", "refresh_live", "update_dashboard"):
                            extra += (
                                "\n\nPython / dashboard error? Double-click:\n"
                                "  Home-Repository/scripts/Repair Dashboard.command\n"
                                "Then quit (Cmd+Q) and reopen this app."
                            )
                        messagebox.showerror(
                            f"{title} failed",
                            f"Exit code {exit_code}.{extra}\n\nLast log lines:\n{hint}",
                        )
                    self.current_task = ""
                    self.current_task_key = ""
                    if task_key == "end_of_day":
                        self.dashboard_pause_expected = False

                        def restart_dashboard() -> None:
                            script = self.repo / "scripts" / "ensure_dashboard_mac.sh"
                            if script.is_file():
                                proc = subprocess.run(
                                    ["/bin/bash", str(script)],
                                    cwd=self.repo,
                                    capture_output=True,
                                    text=True,
                                )
                                out = (proc.stdout or "") + (proc.stderr or "")
                                if out.strip():
                                    for line in out.strip().splitlines():
                                        self.root.after(0, lambda l=line: self.log(l))
                            self.root.after(0, self.refresh_status)

                        threading.Thread(target=restart_dashboard, daemon=True).start()
                    self._set_rhythm_buttons_enabled(True)
                    self.refresh_rhythm_labels()
                    if task_key != "end_of_day":
                        self.refresh_status()
                    if self._clear_status_after_id:
                        self.root.after_cancel(self._clear_status_after_id)
                    self._clear_status_after_id = self.root.after(
                        15000,
                        lambda: self._set_task_banner("Ready — pick a step below", running=False),
                    )

                self.root.after(0, finish_ui)

        threading.Thread(target=worker, daemon=True).start()

    def update_and_open(self) -> None:
        script = self.repo / "scripts" / "update_and_open_dashboard_mac.sh"
        if script.is_file():
            self._run_script(
                "Update & open dashboard",
                script,
                task_key="update_dashboard",
                open_browser_after=True,
                script_args=["--no-open"],
            )
            return
        self._run_script(
            "Update & open dashboard",
            self.repo / "scripts" / "hard_restart_dashboard_mac.sh",
            task_key="update_dashboard",
            open_browser_after=True,
            script_args=["--pull", "--no-open"],
        )

    def open_browser(self) -> None:
        self._open_dashboard_browser(wait=False)

    def _open_dashboard_browser(self, *, wait: bool = True, wait_seconds: int = 35) -> bool:
        """Open dashboard URL; optionally wait until /api/version responds."""
        if wait:
            deadline = time.time() + wait_seconds
            while time.time() < deadline:
                try:
                    with urllib.request.urlopen(f"{DASHBOARD_URL}/api/version", timeout=2) as resp:
                        json.loads(resp.read().decode())
                    break
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                    time.sleep(1)
            else:
                self.log(
                    f"Dashboard not responding at {DASHBOARD_URL} after {wait_seconds}s"
                )
                return False

        if sys.platform == "darwin":
            subprocess.run(["open", DASHBOARD_URL], check=False)
        else:
            webbrowser.open(DASHBOARD_URL)
        self.log(f"Opened {DASHBOARD_URL}")
        return True

    def morning_prep(self) -> None:
        self._start_rhythm_task("morning_prep", "run_morning_prep_mac.sh", "Morning prep")

    def refresh_live(self) -> None:
        self._start_rhythm_task("refresh_live", "run_refresh_live_mac.sh", "Refresh live")

    def end_of_day(self) -> None:
        self._start_rhythm_task("end_of_day", "run_end_of_day_mac.sh", "End of day")

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
        self.refresh_rhythm_labels()


def main() -> None:
    helper_path = Path(__file__).resolve()
    _log_startup(f"Starting desktop helper {DESKTOP_HELPER_BUILD}")
    _log_startup(f"Script: {helper_path}")
    repo = discover_repo()
    if repo:
        _log_startup(f"Repo: {repo}")
    else:
        _log_startup("Repo not found — will prompt")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        _fatal_startup(
            f"Could not open the app window (Tk error):\n{exc}\n\n"
            "On Mac with Homebrew Python, install Tk support:\n"
            "  brew install python-tk@3.12"
        )
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

    _load_desktop_status()
    try:
        DesktopHelperApp(root, repo)
        root.mainloop()
    except Exception as exc:
        _fatal_startup(f"Unexpected error:\n{exc}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        _fatal_startup(f"Startup crashed:\n{exc}")
