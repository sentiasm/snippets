from functools import lru_cache
from contextlib import contextmanager
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import time
import itertools
import traceback


# -----------------------------
# Timing / Performance
# -----------------------------

@contextmanager
def timer(label: str = "block"):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"[{label}] {elapsed:.4f}s")


@lru_cache(maxsize=None)
def memoize_unbounded(fn):
    return fn


# -----------------------------
# Collections / Data
# -----------------------------

def unique_preserve_order(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


def chunked(iterable, size: int):
    it = iter(iterable)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


def flatten(iterable):
    return itertools.chain.from_iterable(iterable)


def most_common(items, n=1):
    return Counter(items).most_common(n)


# -----------------------------
# Filesystem
# -----------------------------

def ensure_dir(path: str | Path):
    Path(path).expanduser().resolve().mkdir(parents=True, exist_ok=True)


def read_text_safe(path: str | Path, default=""):
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return default


def atomic_write(path: str | Path, text: str):
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text)
    tmp.replace(path)


# -----------------------------
# Error Handling
# -----------------------------

def retry(fn, retries=3, delay=0.5, exceptions=(Exception,)):
    for i in range(retries):
        try:
            return fn()
        except exceptions:
            if i == retries - 1:
                raise
            time.sleep(delay)


def swallow_exceptions(fn, default=None):
    try:
        return fn()
    except Exception:
        traceback.print_exc()
        return default


# -----------------------------
# Concurrency
# -----------------------------

def parallel_map(fn, iterable, workers=None):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, iterable))


# -----------------------------
# Functional Utilities
# -----------------------------

def compose(*funcs):
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed


def tap(fn):
    def wrapper(x):
        fn(x)
        return x
    return wrapper


# -----------------------------
# Sentinel Object
# -----------------------------

class _Missing:
    def __repr__(self):
        return "<MISSING>"

MISSING = _Missing()
