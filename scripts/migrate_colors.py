#!/usr/bin/env python3
"""One-shot color-token migration to Quips Palette 2.0.

Remaps every collection's legacy `colorName` to the new 16-token OKLCH palette
and adds a `colorLightHex` / `colorDarkHex` pair next to it (light + dark
appearance values). Runs over collections.json and every collections/<id>.json;
only collections carry color — no quote does. Idempotent: an object that
already has a new-palette colorName + matching hex pair is left untouched, which
also resolves the legacy/new `teal` collision (old teal -> cyan, but new teal
from mint must stay teal).

Formatting matches the repo convention (2-space indent, ensure_ascii=False,
trailing newline) so the diff shows only the color changes.

Usage: migrate_colors.py [--root ROOT] [--check]
    --check  don't write; exit 1 if any file would still change (for CI)
"""

import argparse
import json
import os
import sys

# Legacy token -> new token. Already-new tokens (red, orange, cyan, magenta,
# purple, gray, ...) are absent here and pass through unchanged. forestGreen is
# not in the migration guide's table but is plainly a green (mirrors
# mediumGreen -> green), so it is mapped explicitly rather than blanked.
OLD_TO_NEW = {
    "ruby": "red", "darkRed": "red", "orange": "orange", "gold": "amber",
    "brown": "amber", "lemon": "yellow", "leaf": "lime", "mediumGreen": "green",
    "forestGreen": "green", "mint": "teal", "teal": "cyan", "lightBlue": "sky",
    "primaryBlue": "blue", "navyBlue": "blue", "purple": "purple",
    "magenta": "magenta", "cloudy": "gray",
}

# New token -> (light hex, dark hex).
HEX = {
    "rose": ("#E03063", "#F66E89"), "red": ("#E92528", "#FA7064"),
    "orange": ("#E1791C", "#FDA260"), "amber": ("#E2A520", "#FBB620"),
    "yellow": ("#F7E120", "#DAC720"), "lime": ("#9EDB2A", "#9DDC21"),
    "green": ("#27AE57", "#2BD66A"), "teal": ("#27A98A", "#2BD1AA"),
    "cyan": ("#29ACB2", "#2DD3DA"), "sky": ("#1F9ED4", "#45C2FC"),
    "blue": ("#116BDF", "#4790FB"), "indigo": ("#494BEC", "#6A7BF3"),
    "violet": ("#8839E9", "#A174F0"), "purple": ("#B632CA", "#DE56F3"),
    "magenta": ("#D72D97", "#F762B7"), "gray": ("#8A8D90", "#9CA0A3"),
}


def migrate_color(color_name):
    """Return (token, light, dark) for a legacy or new colorName. Empty or
    unknown -> "" with the neutral gray pair."""
    token = OLD_TO_NEW.get(color_name, color_name)  # new tokens pass through
    if token not in HEX:                            # empty/unknown -> neutral
        token = ""
    light, dark = HEX.get(token, HEX["gray"])
    return token, light, dark


def already_migrated(obj):
    """True if obj already carries a new-palette colorName + matching hex pair.

    This is what makes the migration idempotent despite the token collision:
    legacy `teal` (#008080) maps to `cyan`, but new `teal` (from `mint`) is a
    distinct hue. Once an object has been migrated, its colorName is a new token
    whose stored hex already matches HEX[token] (or gray for ""), so we must NOT
    feed it back through OLD_TO_NEW and turn a new `teal` into `cyan`.
    """
    name = obj.get("colorName", None)
    if name is None or "colorLightHex" not in obj or "colorDarkHex" not in obj:
        return False
    light, dark = HEX.get(name) if name in HEX else (HEX["gray"] if name == "" else (None, None))
    return (obj["colorLightHex"], obj["colorDarkHex"]) == (light, dark)


def apply_to(obj):
    """Rewrite obj in place: remap colorName and insert the hex pair directly
    after it, preserving key order. Returns True if anything changed."""
    if "colorName" not in obj:
        return False
    if already_migrated(obj):
        return False
    token, light, dark = migrate_color(obj.get("colorName", ""))
    new = {}
    for k, v in obj.items():
        if k in ("colorLightHex", "colorDarkHex"):
            continue  # drop existing so a re-run re-inserts in the right place
        if k == "colorName":
            new["colorName"] = token
            new["colorLightHex"] = light
            new["colorDarkHex"] = dark
        else:
            new[k] = v
    changed = new != obj
    obj.clear()
    obj.update(new)
    return changed


def process(path, check):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    if isinstance(data, dict) and "collections" in data:  # the index
        for entry in data["collections"]:
            changed |= apply_to(entry)
    else:                                                  # a detail file
        changed |= apply_to(data)

    if changed and not check:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    paths = [os.path.join(args.root, "collections.json")]
    coll_dir = os.path.join(args.root, "collections")
    paths += sorted(
        os.path.join(coll_dir, fn)
        for fn in os.listdir(coll_dir) if fn.endswith(".json")
    )

    dirty = [p for p in paths if process(p, args.check)]

    if args.check:
        if dirty:
            for p in dirty:
                print(f"[STALE] {p}: colorName not migrated")
            print(f"\n{len(dirty)} file(s) need migration")
            return 1
        print(f"ok — {len(paths)} file(s) already migrated")
        return 0

    print(f"migrated {len(dirty)} file(s) of {len(paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
