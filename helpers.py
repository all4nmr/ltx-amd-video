"""
helpers.py — AMD DirectML device helpers for LTX-2 OPTIMIZED.

Provides unified device detection and memory management for
CUDA (NVIDIA) and DirectML (AMD) backends.
"""

import torch
import logging

logger = logging.getLogger(__name__)

_DIRECTML_AVAILABLE = False
try:
    import torch_directml
    _DIRECTML_AVAILABLE = True
except ImportError:
    pass


def get_device(prefer: str = "auto") -> torch.device:
    """Resolve the optimal torch device.

    Args:
        prefer: "auto" (default), "cuda", "directml", or "cpu".

    Returns:
        A torch.device instance.  Also sets a global ``device``
        attribute on this module so callers can write
        ``helpers.device`` after calling this once.
    """
    global device

    if prefer == "cuda" and torch.cuda.is_available():
        device_ = torch.device("cuda")
        logger.info("Using CUDA device: %s", torch.cuda.get_device_name(0))
    elif prefer == "directml" and _DIRECTML_AVAILABLE:
        dml_device = torch_directml.device()
        device_ = dml_device
        logger.info("Using DirectML device")
    elif prefer == "auto":
        if torch.cuda.is_available():
            device_ = torch.device("cuda")
            logger.info("Auto-select: CUDA device: %s", torch.cuda.get_device_name(0))
        elif _DIRECTML_AVAILABLE:
            dml_device = torch_directml.device()
            device_ = dml_device
            logger.info("Auto-select: DirectML device")
        else:
            device_ = torch.device("cpu")
            logger.warning("Auto-select: no GPU found, falling back to CPU (slow!)")
    else:
        device_ = torch.device("cpu")
        logger.warning("Requested device %r not available, falling back to CPU", prefer)

    device = device_
    return device_


def is_directml(device_: torch.device = None) -> bool:
    """Return True if *device_* (or the module-level device) is DirectML."""
    d = device_ if device_ is not None else getattr(globals(), "device", None)
    if d is None:
        return False
    return d.type == "privateuseone"


def sync_device(device_: torch.device = None):
    """Synchronize the current device, equivalent to ``cuda.synchronize()``.

    Works for both CUDA and DirectML backends.
    """
    d = device_ if device_ is not None else getattr(globals(), "device", None)
    if d is None:
        return
    if d.type == "cuda":
        torch.cuda.synchronize(d)
    elif is_directml(d):
        # DirectML uses a different sync mechanism
        # torch_directml.synchronize() is called internally
        pass


def cleanup_memory():
    """Run garbage collection and clear GPU cache.

    Compatible with both CUDA and DirectML.
    """
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def auto_device_cli_arg(parser):
    """Add a ``--device`` argument to an argparse parser.

    Usage::

        parser = argparse.ArgumentParser()
        auto_device_cli_arg(parser)
        args = parser.parse_args()
        device = get_device(args.device)
    """
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "directml", "cpu"],
        help="Device to run on (default: auto-detect)",
    )
