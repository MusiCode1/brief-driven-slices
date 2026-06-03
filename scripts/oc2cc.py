#!/usr/bin/env python3
"""oc2cc.py — ‏ממיר ‏הגדרת ‏agent ‏מפורמט ‏OpenCode ‏לפורמט ‏Claude Code.

‏מקור-האמת ‏הוא ‏agents/<name>.md ‏בפורמט ‏OpenCode. ‏Claude Code ‏לא ‏מבין ‏את ‏אותו
‏frontmatter: ‏tools ‏הוא ‏מחרוזת ‏(לא ‏מפה ‏של ‏בוליאנים), ‏model ‏בלי ‏תחילית ‏anthropic/,
‏ואין ‏mode:/permission:. ‏הגוף ‏זהה ‏לחלוטין ‏בין ‏הפלטפורמות.

‏stdlib ‏בלבד ‏(אין ‏PyYAML — ‏מוסכמת ‏הריפו). ‏הפרסור ‏טקסטואלי ‏ומסתמך ‏על ‏המבנה
‏הקבוע ‏של ‏ה-frontmatter: ‏מפתחות ‏top-level ‏בעמודה ‏0, ‏בלוקים ‏מקוננים ‏בהזחה.

‏שימוש:
  oc2cc.py <agent.md>              # ‏פולט ‏את ‏גרסת ‏ה-CC ‏ל-stdout
  oc2cc.py <agent.md> -o <out.md>  # ‏כותב ‏לקובץ
  oc2cc.py <agent.md> --body-only  # ‏פולט ‏רק ‏את ‏הגוף ‏(ל---append-system-prompt)
"""
import argparse
import sys

# ‏מיפוי ‏שמות ‏כלים: ‏OpenCode ‏(lowercase) → Claude Code (CamelCase)
TOOL_MAP = {
    "read": "Read",
    "glob": "Glob",
    "grep": "Grep",
    "write": "Write",
    "edit": "Edit",
    "bash": "Bash",
    "webfetch": "WebFetch",
    "task": "Task",
    "todowrite": "TodoWrite",
}

# ‏מיפוי ‏מודל: ‏OpenCode ‏(provider/id) → Claude Code (alias)
MODEL_MAP = {
    "claude-opus-4-8": "opus",
    "claude-sonnet-4-6": "sonnet",
    "claude-haiku-4-5": "haiku",
}


def split_frontmatter(text):
    """‏מחזיר ‏(fm_lines, body). ‏מצפה ‏ש-text ‏מתחיל ‏ב---. ‏body ‏מועתק ‏מילולית."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("‏אין ‏frontmatter ‏פותח ‏(---) ‏בתחילת ‏הקובץ")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("‏frontmatter ‏לא ‏נסגר ‏(--- ‏שני ‏חסר)")
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])
    return fm_lines, body


def is_top_level_key(line):
    """‏שורה ‏שמתחילה ‏מפתח ‏top-level: ‏לא ‏מוזחת ‏ולא ‏ריקה."""
    return bool(line) and not line[0].isspace() and ":" in line


def map_model(value):
    value = value.strip()
    # ‏הסר ‏תחילית ‏provider ‏(anthropic/)
    if "/" in value:
        value = value.split("/", 1)[1]
    return MODEL_MAP.get(value, value)


def convert(text):
    fm_lines, body = split_frontmatter(text)
    out = []
    i = 0
    n = len(fm_lines)
    while i < n:
        line = fm_lines[i]
        # ‏מפתח ‏top-level?
        if is_top_level_key(line):
            key = line.split(":", 1)[0].strip()
            if key in ("mode", "permission"):
                # ‏דלג ‏על ‏המפתח ‏ועל ‏הבלוק ‏המקונן ‏שלו ‏(שורות ‏מוזחות/ריקות)
                i += 1
                while i < n and (not fm_lines[i].strip() or not is_top_level_key(fm_lines[i])):
                    i += 1
                continue
            if key == "model":
                val = line.split(":", 1)[1]
                out.append("model: " + map_model(val))
                i += 1
                continue
            if key == "tools":
                # ‏אסוף ‏את ‏הכלים ‏המקוננים ‏שהוגדרו ‏true, ‏בסדר ‏המקור
                tools = []
                i += 1
                while i < n and (not fm_lines[i].strip() or not is_top_level_key(fm_lines[i])):
                    sub = fm_lines[i].strip()
                    if sub and ":" in sub:
                        tname, tval = sub.split(":", 1)
                        if tval.strip().lower() == "true":
                            mapped = TOOL_MAP.get(tname.strip())
                            if mapped:
                                tools.append(mapped)
                    i += 1
                if tools:
                    out.append("tools: " + ", ".join(tools))
                continue
            # name / description ‏וכל ‏מפתח ‏אחר — ‏שמור ‏מילולית
            out.append(line)
            i += 1
            continue
        # ‏שורת ‏המשך ‏(הזחה/ריקה) ‏של ‏מפתח ‏שנשמר ‏(למשל ‏description ‏folded)
        out.append(line)
        i += 1

    return "---\n" + "\n".join(out) + "\n---\n" + body


def body_only(text):
    _, body = split_frontmatter(text)
    return body.lstrip("\n")


def main():
    ap = argparse.ArgumentParser(description="OpenCode agent → Claude Code converter")
    ap.add_argument("input", help="‏נתיב ‏ל-agent.md ‏(פורמט ‏OpenCode)")
    ap.add_argument("-o", "--output", help="‏נתיב ‏פלט ‏(ברירת ‏מחדל: ‏stdout)")
    ap.add_argument("--body-only", action="store_true",
                    help="‏פלוט ‏רק ‏את ‏הגוף ‏ללא ‏frontmatter ‏(ל---append-system-prompt)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        text = f.read()

    result = body_only(text) if args.body_only else convert(text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
