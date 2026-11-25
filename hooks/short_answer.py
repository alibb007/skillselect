#!/usr/bin/env python3
"""SkillSelect: a UserPromptSubmit hook.
Short answers (on until you switch it off): adds one sentence to the request, so nobody has to type it.
The sentence is the short one from round 3 (42 requests): half the words of a plain answer, no blanks left to fill in.
Switch: /skillselect short on|off, or SKILLSELECT_SHORT = 1 or 0."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def finder():
    path = os.path.join(os.path.dirname(HERE), "skills", "skillselect", "scripts", "find_skills.py")
    spec = importlib.util.spec_from_file_location("find_skills", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    try:
        fs = finder()
    except Exception:  # a broken install must never block a request
        return 0
    out = []
    if fs.setting("short_answers", True):
        out.append(fs.SHORT_SENTENCE)
    if out:
        print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
