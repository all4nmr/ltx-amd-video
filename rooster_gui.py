#!/usr/bin/env python3
"""
rooster_gui.py — Native Tkinter GUI for LTX-2 AMD Video Generation.

Replaces the Gradio Web UI with a native Windows desktop GUI.
Supports DirectML (AMD) and CUDA (NVIDIA) backends.

Usage:
    python rooster_gui.py [--device auto|cuda|directml|cpu]
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("rooster_gui")

# ── Constants ──────────────────────────────────────────────────────────────

DEFAULT_MODELS_DIR = "./models"
DEFAULT_OUTPUT_DIR = "./output"
RESOLUTIONS = [
    "640x360  (Low VRAM)",
    "1280x704 (8GB Safe)",
    "1536x1024",
    "1920x1088",
    "2560x1408",
]
MAX_FRAMES_SAFE = 257  # 10s @ 25fps


# ── Segment Manager (configurable splitting + stitching) ────────────────────

class SegmentManager:
    """Handles splitting long videos into segments and stitching results."""

    @staticmethod
    def split(total_seconds: int, fps: int = 25,
              max_segment_seconds: int = 15) -> list[dict]:
        """Return list of segment configs.

        Args:
            total_seconds: Total video duration in seconds.
            fps: Frames per second.
            max_segment_seconds: Max duration per segment (15-30s).

        Returns:
            List of dicts: {start_frame, num_frames, segment_index}.
        """
        total_frames = total_seconds * fps
        max_frames = max_segment_seconds * fps
        segments = []
        pos = 0
        idx = 0
        while pos < total_frames:
            n = min(max_frames, total_frames - pos)
            segments.append({
                "start_frame": pos,
                "num_frames": n,
                "segment_index": idx,
            })
            pos += n
            idx += 1
        return segments

    @staticmethod
    def stitch(segment_files: list[str], output_path: str) -> str:
        """Stitch video segments using ffmpeg."""
        if not segment_files:
            raise ValueError("No segments to stitch")
        if len(segment_files) == 1:
            # Single segment, just copy/rename
            import shutil
            shutil.copy2(segment_files[0], output_path)
            return output_path

        # Create concat file
        list_path = os.path.join(os.path.dirname(output_path), "_segments.txt")
        with open(list_path, "w") as f:
            for seg in segment_files:
                f.write(f"file '{os.path.abspath(seg)}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(list_path)
        return output_path


# ── Generation Worker Thread ───────────────────────────────────────────────

class GenWorker(threading.Thread):
    """Runs LTX-2 generation in a separate thread."""

    def __init__(self, config: dict, callback, progress_callback):
        threading.Thread.__init__(self, daemon=True)
        self.config = config
        self.callback = callback
        self.progress_callback = progress_callback
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        try:
            self.progress_callback("Initializing device...", 0)
            import helpers

            device = helpers.get_device(self.config.get("device", "auto"))
            helpers.cleanup_memory()

            # Set up model paths
            model_dir = Path(self.config.get("models_dir", DEFAULT_MODELS_DIR))
            if not model_dir.exists():
                raise FileNotFoundError(f"Models directory not found: {model_dir}")

            # Determine total duration (from config or default)
            total_seconds = self.config.get("duration_seconds", 10)
            fps = self.config.get("fps", 25)
            max_seg_sec = self.config.get("max_segment_seconds", 15)

            if self._cancel.is_set():
                self.callback(None, "Cancelled")
                return

            # Split into segments
            segments = SegmentManager.split(total_seconds, fps, max_seg_sec)
            self.progress_callback(f"Split into {len(segments)} segment(s)", 5)

            output_dir = Path(self.config.get("output_dir", DEFAULT_OUTPUT_DIR))
            output_dir.mkdir(parents=True, exist_ok=True)
            segment_files = []

            for i, seg in enumerate(segments):
                if self._cancel.is_set():
                    self.callback(None, "Cancelled")
                    return

                seg_file = output_dir / f"segment_{i:04d}.mp4"
                segment_files.append(str(seg_file))

                pct = 10 + int(80 * (i / len(segments)))
                self.progress_callback(
                    f"Generating segment {i+1}/{len(segments)} "
                    f"(frames {seg['start_frame']}-{seg['start_frame']+seg['num_frames']})...",
                    pct,
                )

                # Build command
                cmd = [
                    sys.executable, "web_ui_v4.py",
                    "--device", self.config.get("device", "auto"),
                    "--output", str(seg_file),
                    "--frames", str(seg["num_frames"]),
                    "--start-frame", str(seg["start_frame"]),
                ]
                if self.config.get("prompt"):
                    cmd += ["--prompt", self.config["prompt"]]
                if self.config.get("image_path"):
                    cmd += ["--image", self.config["image_path"]]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(
                        f"Segment {i} failed: {result.stderr[:500]}"
                    )

            # Stitch
            self.progress_callback("Stitching segments...", 95)
            output_path = str(output_dir / "output.mp4")
            SegmentManager.stitch(segment_files, output_path)

            # Cleanup segments
            for sf in segment_files:
                try:
                    os.remove(sf)
                except OSError:
                    pass

            self.progress_callback("Done!", 100)
            self.callback(output_path, None)

        except Exception as e:
            logger.exception("Generation failed")
            self.callback(None, str(e))


# ── GUI Application ────────────────────────────────────────────────────────

class RoosterGUI:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LTX-2 AMD Video Generator")
        self.root.geometry("780x620")
        self.root.resizable(True, True)
        self._worker = None

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

    def _build_ui(self):
        # ── Device Selection ──
        dev_frame = ttk.LabelFrame(self.root, text="Device", padding=10)
        dev_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.device_var = tk.StringVar(value="auto")
        ttk.Radiobutton(dev_frame, text="Auto-detect", variable=self.device_var,
                        value="auto").pack(side="left", padx=5)
        ttk.Radiobutton(dev_frame, text="CUDA (NVIDIA)", variable=self.device_var,
                        value="cuda").pack(side="left", padx=5)
        ttk.Radiobutton(dev_frame, text="DirectML (AMD)", variable=self.device_var,
                        value="directml").pack(side="left", padx=5)
        ttk.Radiobutton(dev_frame, text="CPU", variable=self.device_var,
                        value="cpu").pack(side="left", padx=5)

        # ── Model Path ──
        model_frame = ttk.LabelFrame(self.root, text="Model Assets", padding=10)
        model_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(model_frame, text="Models folder:").grid(row=0, column=0, sticky="w")
        self.model_path_var = tk.StringVar(value=DEFAULT_MODELS_DIR)
        ttk.Entry(model_frame, textvariable=self.model_path_var, width=50).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(model_frame, text="Browse...",
                   command=self._browse_models).grid(row=0, column=2)

        ttk.Label(model_frame, text="Input image (optional):").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )
        self.image_path_var = tk.StringVar(value="")
        ttk.Entry(model_frame, textvariable=self.image_path_var, width=50).grid(
            row=1, column=1, padx=5, pady=(5, 0)
        )
        ttk.Button(model_frame, text="Browse...",
                   command=self._browse_image).grid(row=1, column=2, pady=(5, 0))

        # ── Output Path ──
        out_frame = ttk.LabelFrame(self.root, text="Output", padding=10)
        out_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(out_frame, text="Output folder:").grid(row=0, column=0, sticky="w")
        self.output_path_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        ttk.Entry(out_frame, textvariable=self.output_path_var, width=50).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(out_frame, text="Browse...",
                   command=self._browse_output).grid(row=0, column=2)

        # ── Generation Settings ──
        gen_frame = ttk.LabelFrame(self.root, text="Generation Settings", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(gen_frame, text="Resolution:").grid(row=0, column=0, sticky="w")
        self.res_var = tk.StringVar(value=RESOLUTIONS[1])
        ttk.Combobox(gen_frame, textvariable=self.res_var,
                     values=RESOLUTIONS, width=30, state="readonly").grid(
            row=0, column=1, padx=5, sticky="w"
        )

        ttk.Label(gen_frame, text="Duration (seconds):").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )
        self.duration_var = tk.IntVar(value=10)
        ttk.Spinbox(gen_frame, from_=1, to=120, textvariable=self.duration_var,
                    width=10).grid(row=1, column=1, padx=5, pady=(5, 0), sticky="w")

        ttk.Label(gen_frame, text="Segment length (sec):").grid(
            row=2, column=0, sticky="w", pady=(5, 0)
        )
        self.segment_var = tk.IntVar(value=15)
        ttk.Spinbox(gen_frame, from_=15, to=30, textvariable=self.segment_var,
                    width=10).grid(row=2, column=1, padx=5, pady=(5, 0), sticky="w")
        ttk.Label(gen_frame, text="15-30s (shorter = more stable, longer = fewer segments)",
                  font=("Segoe UI", 8)).grid(row=2, column=2, padx=5, pady=(5, 0), sticky="w")

        # ── Prompt ──
        prompt_frame = ttk.LabelFrame(self.root, text="Prompt", padding=10)
        prompt_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.prompt_text = tk.Text(prompt_frame, height=4, font=("Segoe UI", 10))
        self.prompt_text.pack(fill="both", expand=True)
        self.prompt_text.insert("1.0",
            "A cinematic shot of a person speaking naturally, "
            "well-lit studio, 4K quality."
        )

        # ── Progress ──
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var,
                  font=("Segoe UI", 9)).pack(anchor="w")

        # ── Buttons ──
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.gen_btn = ttk.Button(btn_frame, text="Generate Video",
                                  command=self._start_generation)
        self.gen_btn.pack(side="left", padx=5)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel",
                                     command=self._cancel_generation, state="disabled")
        self.cancel_btn.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Open Output Folder",
                   command=self._open_output).pack(side="right", padx=5)

    def _browse_models(self):
        path = filedialog.askdirectory(title="Select models folder")
        if path:
            self.model_path_var.set(path)

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title="Select input image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")]
        )
        if path:
            self.image_path_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_path_var.set(path)

    def _open_output(self):
        path = self.output_path_var.get()
        if os.path.isdir(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])

    def _start_generation(self):
        config = {
            "device": self.device_var.get(),
            "models_dir": self.model_path_var.get(),
            "output_dir": self.output_path_var.get(),
            "image_path": self.image_path_var.get(),
            "prompt": self.prompt_text.get("1.0", "end-1c").strip(),
            "duration_seconds": self.duration_var.get(),
            "max_segment_seconds": self.segment_var.get(),
        }

        self._worker = GenWorker(
            config=config,
            callback=self._on_complete,
            progress_callback=self._on_progress,
        )
        self._worker.start()
        self.gen_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

    def _cancel_generation(self):
        if self._worker:
            self._worker.cancel()
        self.status_var.set("Cancelled")
        self.gen_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def _on_progress(self, status: str, pct: int):
        self.root.after(0, lambda: self._update_progress(status, pct))

    def _update_progress(self, status: str, pct: int):
        self.status_var.set(status)
        self.progress_var.set(pct)

    def _on_complete(self, output_path: str | None, error: str | None):
        self.root.after(0, lambda: self._handle_result(output_path, error))

    def _handle_result(self, output_path, error):
        self.gen_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        if error:
            messagebox.showerror("Generation Failed", error)
            self.status_var.set(f"Error: {error[:80]}")
        elif output_path:
            messagebox.showinfo("Success",
                                f"Video saved to:\n{output_path}")
            self.status_var.set(f"Done: {os.path.basename(output_path)}")
        else:
            self.status_var.set("Cancelled")

    def run(self):
        self.root.mainloop()


# ── Entry Point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LTX-2 AMD Video Generator — Native GUI"
    )
    parser.add_argument(
        "--device", default="auto",
        choices=["auto", "cuda", "directml", "cpu"],
        help="Device to use (default: auto-detect)",
    )
    args, _ = parser.parse_known_args()

    app = RoosterGUI()
    if args.device != "auto":
        app.device_var.set(args.device)
    app.run()


if __name__ == "__main__":
    main()
