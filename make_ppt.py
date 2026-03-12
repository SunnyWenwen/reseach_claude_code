from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── White-background Color Palette ────────────────────────────
BG      = RGBColor(0xFF, 0xFF, 0xFF)   # white
CARD    = RGBColor(0xF4, 0xF6, 0xF9)   # light gray card
CARD2   = RGBColor(0xEA, 0xEE, 0xF4)   # slightly darker card
INK     = RGBColor(0x1A, 0x22, 0x2E)   # near-black text
MUTED   = RGBColor(0x60, 0x72, 0x88)   # secondary text
BLUE    = RGBColor(0x1D, 0x6F, 0xC8)   # primary accent
PURPLE  = RGBColor(0x6D, 0x28, 0xD9)   # secondary accent
GREEN   = RGBColor(0x05, 0x8A, 0x5E)   # green
ORANGE  = RGBColor(0xC2, 0x61, 0x00)   # orange (dark enough on white)
RED     = RGBColor(0xB9, 0x1C, 0x1C)   # red
YELLOW  = RGBColor(0x92, 0x60, 0x00)   # amber (dark for readability)
LBLUE   = RGBColor(0xDB, 0xEA, 0xFB)   # light blue tint
LGREEN  = RGBColor(0xD1, 0xFA, 0xEA)   # light green tint
LPURPLE = RGBColor(0xED, 0xE4, 0xFF)   # light purple tint
LORANGE = RGBColor(0xFF, 0xED, 0xCC)   # light orange tint
LRED    = RGBColor(0xFE, 0xE2, 0xE2)   # light red tint
LYELLOW = RGBColor(0xFE, 0xF3, 0xC7)   # light amber tint
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

# ── Helpers ────────────────────────────────────────────────────

def bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, fill_color=None, line_color=None, lw=Pt(1.2)):
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = lw
    else:
        shape.line.fill.background()
    return shape

def txt(slide, text, x, y, w, h,
        size=16, bold=False, color=INK, align=PP_ALIGN.LEFT, italic=False):
    txb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb

def hline(slide, y, x=0.0, w=13.33, color=CARD2, h=0.04):
    bar = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()

def accent_bar(slide, y=0.9, x=0.55, w=3.0, color=BLUE, h=0.055):
    bar = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()

def left_bar(slide, x, y, h, color, w=0.07):
    b = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = color; b.line.fill.background()

def slide_title(slide, title, subtitle=""):
    bg(slide)
    hline(slide, 0.0, w=13.33, color=BLUE, h=0.09)   # top stripe
    txt(slide, title, 0.55, 0.18, 12.2, 0.7, size=26, bold=True, color=INK)
    hline(slide, 0.96, color=CARD2, h=0.04)
    if subtitle:
        txt(slide, subtitle, 0.55, 1.02, 12, 0.42, size=13.5, color=MUTED, italic=True)

def section_slide(slide, num, title, subtitle=""):
    bg(slide)
    box(slide, 0, 0, 13.33, 7.5, fill_color=BLUE)
    box(slide, 0.45, 0.45, 12.43, 6.6, fill_color=WHITE)
    txt(slide, num, 0.6, 0.55, 2.8, 2.3, size=110, bold=True, color=LBLUE)
    txt(slide, title, 0.7, 2.1, 11.8, 1.1, size=40, bold=True, color=INK)
    accent_bar(slide, y=3.3, x=0.7, w=3.5, color=BLUE, h=0.06)
    if subtitle:
        txt(slide, subtitle, 0.7, 3.5, 11, 0.55, size=17, color=MUTED)

def arrow_v(slide, x, y1, y2, color=MUTED):
    c = slide.shapes.add_connector(1, Inches(x), Inches(y1), Inches(x), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(1.5)

def arrow_diag(slide, x1, y1, x2, y2, color=MUTED):
    c = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(1.5)

def tag(slide, x, y, label, fg=BLUE, bg_c=LBLUE, size=11):
    box(slide, x, y, len(label)*0.085+0.2, 0.3, fill_color=bg_c)
    txt(slide, label, x+0.06, y+0.02, len(label)*0.085+0.1, 0.28,
        size=size, bold=True, color=fg)


# ══════════════════════════════════════════════════════════════════
# SLIDE 1 – Title
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
# top color block
box(s, 0, 0, 13.33, 3.8, fill_color=BLUE)
# white content area
box(s, 0, 3.8, 13.33, 3.7, fill_color=BG)

txt(s, "Claude Code", 0.8, 0.5, 11.5, 1.3, size=58, bold=True, color=WHITE)
txt(s, "Internal Mechanism Deep Dive", 0.8, 1.85, 11, 0.75, size=26, color=RGBColor(0xBB,0xD6,0xF8))
hline(s, 3.82, color=BLUE, h=0.055)

txt(s, "How the agentic loop, tools, skills, agents, hooks, and permissions actually work",
    0.8, 4.15, 11.5, 0.65, size=16, color=INK)
txt(s, "Tech Sharing  ·  2026", 0.8, 5.1, 5, 0.38, size=13, color=MUTED)

# Research method badges
for i, (label, col, bg_c) in enumerate([
    ("JSONL Analysis", BLUE, LBLUE),
    ("Source Code Review", GREEN, LGREEN),
    ("Official Docs", PURPLE, LPURPLE),
]):
    tag(s, 0.8 + i * 3.1, 5.7, label, fg=col, bg_c=bg_c, size=12)


# ══════════════════════════════════════════════════════════════════
# SLIDE 2 – Research Methodology
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Research Methodology — Cross-Validation Approach",
            "All findings verified through three independent sources before being documented")

methods = [
    (BLUE,   LBLUE,   "01", "Session JSONL",
     "Claude Code logs every conversation as structured JSONL.\n"
     "Tool calls, token counts, subagent steps, hook events — all\n"
     "recorded at runtime. This is the ground truth for what\n"
     "actually happened, not what should have happened."),
    (GREEN,  LGREEN,  "02", "Source Code",
     "Claude Code ships as a single Node.js exe with an embedded\n"
     "(unencrypted) minified JS bundle. Key logic — permission\n"
     "matching, tool loading, hook schemas — directly readable\n"
     "via grep/strings on the binary (~237 MB)."),
    (PURPLE, LPURPLE, "03", "Official Docs",
     "Anthropic's public documentation (docs.anthropic.com)\n"
     "describes intended behavior and security guarantees.\n"
     "When docs and runtime evidence diverge, the JSONL\n"
     "and source code take precedence."),
]

for i, (col, bg_c, num, title, body) in enumerate(methods):
    x = 0.45 + i * 4.3
    box(s, x, 1.45, 4.1, 5.7, fill_color=CARD, line_color=col)
    box(s, x, 1.45, 4.1, 0.62, fill_color=bg_c)
    txt(s, f"{num}  {title}", x+0.18, 1.5, 3.8, 0.5, size=16, bold=True, color=col)
    txt(s, body, x+0.18, 2.22, 3.75, 4.75, size=13, color=INK)
    # bottom rule
    hline(s, 6.9, x=x, w=4.1, color=col, h=0.06)

txt(s, "Rule: if all three sources agree → high confidence. "
    "If JSONL / source contradict docs → runtime evidence wins.",
    0.45, 7.15, 12.4, 0.3, size=12, color=MUTED, italic=True)


# ══════════════════════════════════════════════════════════════════
# SLIDE 3 – Agenda
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Agenda")

topics = [
    ("01", "Agentic Loop",       BLUE,   LBLUE,   "How Claude executes tool calls in a loop"),
    ("02", "Tool System",        GREEN,  LGREEN,  "Pre-loaded / Deferred / MCP classification"),
    ("03", "ToolSearch",         YELLOW, LYELLOW, "The meta-tool that loads other tools"),
    ("04", "Skill System",       PURPLE, LPURPLE, "SKILL.md, trigger paths, execution modes"),
    ("05", "Agent Tool",         ORANGE, LORANGE, "Subagents, IPC, multi-model execution"),
    ("06", "Hooks",              RED,    LRED,    "21 lifecycle events, command & prompt types"),
    ("07", "Permission System",  BLUE,   LBLUE,   "Two-layer design, Bash matching logic"),
    ("08", "Extended Thinking",  GREEN,  LGREEN,  "Plaintext vs encrypted thinking states"),
]

for i, (num, title, col, bg_c, desc) in enumerate(topics):
    row, col_idx = i % 4, i // 4
    x = 0.45 + col_idx * 6.45
    y = 1.3 + row * 1.52
    box(s, x, y, 6.1, 1.38, fill_color=CARD, line_color=col, lw=Pt(1.0))
    box(s, x, y, 0.55, 1.38, fill_color=bg_c)
    txt(s, num, x+0.04, y+0.45, 0.5, 0.48, size=13, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, title, x+0.7, y+0.12, 5.2, 0.48, size=16, bold=True, color=INK)
    txt(s, desc, x+0.7, y+0.65, 5.2, 0.55, size=12.5, color=MUTED)


# ══════════════════════════════════════════════════════════════════
# SLIDE 4 – Section 01
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "01", "Agentic Loop",
              "The fundamental execution architecture of Claude Code")


# ══════════════════════════════════════════════════════════════════
# SLIDE 5 – Agentic Loop Detail
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Agentic Loop — How Tool Execution Works")

# Flow diagram (left)
flow = [
    (1.3,  "User Input",              MUTED,  CARD2),
    (2.38, "LLM Inference",           BLUE,   LBLUE),
    (3.46, "Tool Execution Layer",    GREEN,  LGREEN),
    (4.54, "Collect tool_results",    GREEN,  LGREEN),
    (5.62, "Return to User  ✓",       MUTED,  CARD2),
]
for fy, label, col, bg_c in flow:
    box(s, 0.45, fy, 3.5, 0.72, fill_color=bg_c, line_color=col)
    txt(s, label, 0.45, fy, 3.5, 0.72, size=13.5, bold=True, color=col,
        align=PP_ALIGN.CENTER)

for ya, yb in [(2.02, 2.38), (3.1, 3.46), (4.18, 4.54)]:
    arrow_v(s, 2.2, ya, yb, color=MUTED)
arrow_v(s, 3.65, 5.26, 5.62, color=MUTED)
arrow_diag(s, 3.95, 4.54, 3.95, 3.1, color=BLUE)
txt(s, "loop", 4.0, 3.7, 0.7, 0.32, size=11, color=BLUE, italic=True)
txt(s, "no tool_use", 4.0, 5.45, 1.3, 0.32, size=10, color=MUTED, italic=True)

# Key facts (right)
facts = [
    (BLUE,   LBLUE,   "Batch Parallel Tool Calls",
     "One LLM inference can emit multiple tool_use blocks simultaneously.\n"
     "All execute in parallel; all results return before next inference."),
    (GREEN,  LGREEN,  "Loop Termination Condition",
     "Loop ends when LLM response contains no tool_use block.\n"
     "No special stop token — the model simply stops calling tools."),
    (YELLOW, LYELLOW, "Background Bash is Non-blocking",
     "run_in_background: inference continues immediately.\n"
     "Result delivered later via <task-notification>."),
    (PURPLE, LPURPLE, "Subagents Have Independent Loops",
     "They don't consume parent's inference budget.\n"
     "Progress reported via agent_progress records in parent JSONL."),
]
cy = 1.22
for col, bg_c, title, body in facts:
    box(s, 4.2, cy, 8.9, 1.42, fill_color=bg_c, line_color=col)
    txt(s, title, 4.42, cy+0.1, 8.5, 0.42, size=14, bold=True, color=col)
    txt(s, body,  4.42, cy+0.57, 8.5, 0.72, size=12.5, color=INK)
    cy += 1.52


# ══════════════════════════════════════════════════════════════════
# SLIDE 6 – Section 02
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "02", "Tool System",
              "Pre-loaded · Deferred · MCP — and why the split matters")


# ══════════════════════════════════════════════════════════════════
# SLIDE 7 – Tool Classification
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Tool Classification — Three Loading Strategies")

col_defs = [
    (BLUE,   LBLUE,   "Pre-loaded  (9 tools)",
     "Schema in context at session start.\nNo extra round-trip needed.",
     ["Read", "Write", "Edit", "Glob", "Grep",
      "Bash", "Agent", "Skill", "ToolSearch"],
     "Zero latency to call"),
    (GREEN,  LGREEN,  "Deferred  (16 tools)",
     "Schema NOT in context. Must ToolSearch first.\nTagged in system prompt as <available-deferred-tools>.",
     ["WebFetch", "WebSearch", "AskUserQuestion",
      "NotebookEdit", "EnterPlanMode / ExitPlanMode",
      "EnterWorktree", "TaskCreate / Update / Stop",
      "CronCreate / CronDelete", "..."],
     "+1 round-trip via ToolSearch"),
    (PURPLE, LPURPLE, "MCP  (variable)",
     "Provided by external MCP servers.\nAvailable only when server is connected.",
     ["mcp__ide__getDiagnostics",
      "mcp__ide__executeCode",
      "(any user-configured MCP tool)",
      ""],
     "Depends on server connection"),
]

for i, (col, bg_c, title, desc, tools, note) in enumerate(col_defs):
    x = 0.35 + i * 4.35
    box(s, x, 1.12, 4.15, 6.08, fill_color=CARD)
    box(s, x, 1.12, 4.15, 0.58, fill_color=bg_c)
    txt(s, title, x+0.14, 1.16, 3.9, 0.48, size=15, bold=True, color=col)
    txt(s, desc,  x+0.14, 1.76, 3.88, 0.65, size=12, color=MUTED, italic=True)
    cy = 2.55
    for t in tools:
        if t:
            box(s, x+0.14, cy, 3.75, 0.36, fill_color=bg_c, line_color=col, lw=Pt(0.8))
            txt(s, t, x+0.22, cy+0.04, 3.6, 0.3, size=11.5, color=col, bold=True)
        cy += 0.42
    txt(s, f"→ {note}", x+0.14, 6.7, 3.88, 0.35, size=12, bold=True, color=col)


# ══════════════════════════════════════════════════════════════════
# SLIDE 8 – Why Read/Write not Bash
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Design: Why Read/Write/Edit Instead of Just Bash?",
            "Dedicated tools are not syntax sugar — they have fundamentally different architecture")

# Table
headers = ["Dimension", "Read / Write / Edit", "Bash"]
col_colors = [INK, BLUE, ORANGE]
hx = [0.4, 3.25, 8.0]
hw = [2.75, 4.65, 4.95]

# header row
box(s, 0.4, 1.32, 12.55, 0.5, fill_color=CARD2)
for j, (hdr, col, x, w) in enumerate(zip(headers, col_colors, hx, hw)):
    txt(s, hdr, x+0.12, 1.36, w-0.2, 0.42, size=13, bold=True, color=col)

rows = [
    ("Default Permission",   "Read: auto-allow  |  Write/Edit: separate setting",    "Needs prefix / exact / wildcard rule"),
    ("Matching Logic",       "filePatternTools  (path-based)",                        "bashPrefixTools  (command-based)"),
    ("Token Limit",          "Read: hard 25,000-token cap → returns error string",    "No enforced limit"),
    ("Diff Display",         "Auto structuredPatch + gitDiff shown to user",           "None"),
    ("Write Scope",          "Locked to working directory and subdirectories",         "Unrestricted"),
    ("Special Formats",      "Images (base64 · vision), .ipynb (parsed), PDF (paged)","Raw bytes / text only"),
    ("Shell Injection Risk", "None — parameters assembled by framework",               "Command string parsed by shell"),
]

for ri, row in enumerate(rows):
    y = 1.86 + ri * 0.73
    bg_r = BG if ri % 2 == 0 else CARD
    box(s, 0.4, y, 12.55, 0.68, fill_color=bg_r)
    hline(s, y, x=0.4, w=12.55, color=CARD2, h=0.02)
    for j, (cell, x, w) in enumerate(zip(row, hx, hw)):
        c = MUTED if j == 0 else (BLUE if j == 1 else ORANGE)
        b = j == 0
        txt(s, cell, x+0.12, y+0.1, w-0.2, 0.5, size=11.5, color=c, bold=b)


# ══════════════════════════════════════════════════════════════════
# SLIDE 9 – Section 03
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "03", "ToolSearch",
              "The meta-tool — its sole job is loading other tool schemas into context")


# ══════════════════════════════════════════════════════════════════
# SLIDE 10 – ToolSearch
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "ToolSearch — Dynamic Tool Loading")

# Flow
flow2 = [
    (1.32, "Claude needs a tool",                MUTED,  CARD2),
    (2.38, 'ToolSearch("select:WebFetch")',       YELLOW, LYELLOW),
    (3.44, "WebFetch schema loaded into context", GREEN,  LGREEN),
    (4.5,  "WebFetch(...) called directly",       BLUE,   LBLUE),
]
for fy, label, col, bg_c in flow2:
    box(s, 0.4, fy, 3.8, 0.72, fill_color=bg_c, line_color=col)
    txt(s, label, 0.4, fy, 3.8, 0.72, size=13, bold=True, color=col, align=PP_ALIGN.CENTER)
for ya, yb in [(2.04, 2.38), (3.1, 3.44), (4.16, 4.5)]:
    arrow_v(s, 2.3, ya, yb, color=MUTED)

# Query modes
box(s, 4.6, 1.28, 8.5, 2.65, fill_color=CARD)
box(s, 4.6, 1.28, 8.5, 0.52, fill_color=LYELLOW)
txt(s, "Query Modes", 4.8, 1.32, 5, 0.44, size=15, bold=True, color=YELLOW)
modes = [
    ("Direct select",   'ToolSearch("select:WebFetch")',        "Know the tool name"),
    ("Multi select",    'ToolSearch("select:Read,Edit,Grep")',   "Load several at once"),
    ("Keyword search",  'ToolSearch("list directory")',          "Don't know the exact name"),
]
cy2 = 1.88
for label, example, note in modes:
    txt(s, f"▸  {label}", 4.8, cy2, 2.8, 0.35, size=13, bold=True, color=INK)
    txt(s, example, 4.8, cy2+0.37, 8.1, 0.3, size=12, color=BLUE, italic=True)
    txt(s, f"→ {note}", 4.8, cy2+0.68, 8.1, 0.28, size=11.5, color=MUTED)
    cy2 += 1.05

# Cost
box(s, 4.6, 4.1, 8.5, 1.65, fill_color=LORANGE, line_color=ORANGE)
txt(s, "Performance Cost", 4.8, 4.18, 5, 0.4, size=14, bold=True, color=ORANGE)
txt(s, "Each ToolSearch = 1 extra tool call + 1 LLM inference (~2–3 sec extra latency).\n"
    "Pre-loaded tools skip this entirely.\n"
    "Loaded schema persists for the session — not across sessions.",
    4.8, 4.63, 8.1, 0.98, size=13, color=INK)

# Design insight
box(s, 0.4, 5.5, 12.7, 1.35, fill_color=LBLUE, line_color=BLUE)
txt(s, "Design insight:", 0.65, 5.58, 2.5, 0.38, size=13, bold=True, color=BLUE)
txt(s, "ToolSearch is the only pre-loaded tool whose job is loading other tools. "
    "Lazy-loading keeps the default context smaller (tool schemas are long) — "
    "you pay the latency only when a deferred tool is actually needed.",
    0.65, 5.58, 12.2, 1.1, size=13, color=INK)


# ══════════════════════════════════════════════════════════════════
# SLIDE 11 – Section 04
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "04", "Skill System",
              "SKILL.md — reusable task templates with dynamic injection")


# ══════════════════════════════════════════════════════════════════
# SLIDE 12 – Skill System
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Skill System — Two Trigger Paths, One Pipeline")

# SKILL.md structure (left)
box(s, 0.4, 1.3, 5.0, 5.9, fill_color=CARD)
box(s, 0.4, 1.3, 5.0, 0.5, fill_color=LPURPLE)
txt(s, "SKILL.md Structure", 0.62, 1.35, 4.6, 0.4, size=14, bold=True, color=PURPLE)
code = (
    "---\n"
    "name: session-analyze\n"
    "description: When to trigger (for LLM)\n"
    "argument-hint: <path>\n"
    "allowed-tools: Bash(python3 *), Read\n"
    "disable-model-invocation: true\n"
    "context: fork\n"
    "agent: Explore\n"
    "model: claude-haiku-4-5\n"
    "---\n\n"
    "# Instructions for Claude...\n\n"
    '!`python3 "${CLAUDE_SKILL_DIR}/parse.py" "$ARGUMENTS"`'
)
txt(s, code, 0.58, 1.88, 4.7, 5.1, size=11, color=GREEN)

# Two trigger paths (right)
box(s, 5.65, 1.3, 7.45, 2.6, fill_color=CARD)
box(s, 5.65, 1.3, 7.45, 0.5, fill_color=LBLUE)
txt(s, "Trigger A — User types /skill-name", 5.85, 1.35, 7.1, 0.4, size=13, bold=True, color=BLUE)
txt(s, "CLI reads SKILL.md at framework layer.\n"
    "Injects as isMeta:true user message — Claude sees\n"
    "expanded instructions without calling the Skill tool.",
    5.85, 1.88, 7.1, 1.85, size=12.5, color=INK)

box(s, 5.65, 4.05, 7.45, 2.6, fill_color=CARD)
box(s, 5.65, 4.05, 7.45, 0.5, fill_color=LPURPLE)
txt(s, "Trigger B — Claude calls Skill tool", 5.85, 4.1, 7.1, 0.4, size=13, bold=True, color=PURPLE)
txt(s, "Claude first ToolSearch-loads the Skill schema.\n"
    "Then calls Skill(\"name\", args).\n"
    "Framework processes SKILL.md → tool_result returned.",
    5.85, 4.63, 7.1, 1.85, size=12.5, color=INK)

box(s, 5.65, 6.82, 7.45, 0.5, fill_color=CARD2)
txt(s, "Shared pipeline: variable substitution → ! prefix exec → allowed-tools merge → frontmatter routing",
    5.75, 6.86, 7.25, 0.4, size=11, color=MUTED)


# ══════════════════════════════════════════════════════════════════
# SLIDE 13 – Skill Frontmatter Details
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Skill Frontmatter — What Each Field Actually Does",
            "Source: binary analysis of alwaysAllowRules, disableModelInvocation, context fork")

fields = [
    (BLUE,   LBLUE,   "allowed-tools",
     "Merged into alwaysAllowRules (soft). Auto-allows listed tools — does NOT restrict others.\n"
     "Skill shares main context: LLM can still call other tools, but they require user confirmation."),
    (GREEN,  LGREEN,  "disable-model-invocation: true",
     "After tool_result returns, skip LLM inference. Loop stops immediately.\n"
     "Used for pure-script skills that don't need Claude to process output."),
    (PURPLE, LPURPLE, "context: fork",
     "Creates independent fork context — does not share main session history.\n"
     "Prevents skill from contaminating the main conversation state."),
    (ORANGE, LORANGE, "agent: <subagent_type>",
     "Routes execution to a specific subagent type (e.g. Explore, Plan).\n"
     "Runs inside that agent's isolated context with its tool whitelist."),
    (YELLOW, LYELLOW, "! prefix commands",
     "Executed by framework BEFORE LLM sees the content. Output replaces the line.\n"
     "Used for heavy preprocessing (e.g. compress 92 KB JSONL into a summary)."),
    (RED,    LRED,    "allowed-tools vs Agent tools",
     "Skill allowed-tools = soft, shared context  |  Agent tools = hard, API-level isolation.\n"
     "Agent LLM literally cannot see tools outside its whitelist; Skill LLM can still call them."),
]

cy = 1.32
for col, bg_c, title, body in fields:
    h = 1.0
    box(s, 0.4, cy, 12.6, h, fill_color=bg_c)
    left_bar(s, 0.4, cy, h, col, w=0.35)
    txt(s, title, 0.92, cy+0.1, 3.8, 0.4, size=13.5, bold=True, color=col)
    txt(s, body, 4.85, cy+0.1, 7.95, 0.8, size=12.5, color=INK)
    hline(s, cy+h, x=0.4, w=12.6, color=CARD2, h=0.02)
    cy += h + 0.06


# ══════════════════════════════════════════════════════════════════
# SLIDE 14 – Section 05
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "05", "Agent Tool",
              "Subagents · IPC · multi-model execution · memory architecture")


# ══════════════════════════════════════════════════════════════════
# SLIDE 15 – Subagent Types
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Agent Tool — 5 Built-in Subagent Types")

types = [
    (BLUE,   LBLUE,   "general-purpose",    "All tools (*)",
     "Complex multi-step tasks; full toolset available"),
    (GREEN,  LGREEN,  "Explore",            "All except Agent, ExitPlanMode, Edit, Write, NotebookEdit",
     "Fast codebase exploration; 3 depth levels (quick / medium / very thorough)"),
    (PURPLE, LPURPLE, "Plan",               "Same as Explore",
     "Architecture planning; returns step-by-step implementation plan"),
    (YELLOW, LYELLOW, "claude-code-guide",  "Glob, Grep, Read, WebFetch, WebSearch",
     "Answers Claude Code / SDK / API questions; supports resume parameter"),
    (ORANGE, LORANGE, "statusline-setup",   "Read, Edit only",
     "Configures Claude Code status line settings"),
]

cy = 1.22
for col, bg_c, name, tools, desc in types:
    box(s, 0.4, cy, 12.6, 1.05, fill_color=bg_c)
    left_bar(s, 0.4, cy, 1.05, col, w=0.35)
    txt(s, name, 0.92, cy+0.08, 3.0, 0.42, size=14.5, bold=True, color=col)
    txt(s, f"Tools: {tools}", 4.0, cy+0.08, 9.0, 0.38, size=12, color=MUTED)
    txt(s, desc, 4.0, cy+0.52, 9.0, 0.42, size=13, color=INK)
    cy += 1.12

box(s, 0.4, 6.85, 12.6, 0.48, fill_color=CARD2)
txt(s, "Verified: Explore subagent runs on claude-haiku-4-5-20251001 "
    "while main agent runs claude-sonnet-4-6 — different models within one session.",
    0.6, 6.9, 12.2, 0.38, size=12, color=MUTED, italic=True)


# ══════════════════════════════════════════════════════════════════
# SLIDE 16 – Subagent Architecture
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Subagent Architecture — Isolation, IPC, Memory")

props = [
    (BLUE,   LBLUE,   "Independent Context",
     "Each subagent has its own context window.\nMain agent's conversation history is NOT shared."),
    (GREEN,  LGREEN,  "Recorded in Parent JSONL",
     "Subagent activity stored as agent_progress in parent session.\nNo separate JSONL file generated."),
    (PURPLE, LPURPLE, "Resume Support",
     "Agent tool returns agentId (prefix 'a' = local_agent).\nPass to resume parameter to continue same subagent."),
    (ORANGE, LORANGE, "Full Cost Accounting",
     "tool_result includes totalDurationMs, totalTokens, totalToolUseCount\n— per-subagent cost visibility."),
]
cy = 1.25
for col, bg_c, title, body in props:
    box(s, 0.4, cy, 5.85, 1.48, fill_color=bg_c)
    left_bar(s, 0.4, cy, 1.48, col, w=0.35)
    txt(s, title, 0.92, cy+0.1, 5.1, 0.42, size=14, bold=True, color=col)
    txt(s, body,  0.92, cy+0.58, 5.1, 0.78, size=12.5, color=INK)
    cy += 1.57

# IPC + Memory (right)
box(s, 6.55, 1.25, 6.5, 3.2, fill_color=CARD)
box(s, 6.55, 1.25, 6.5, 0.52, fill_color=LBLUE)
txt(s, "IPC Message Types (Main ↔ Sub)", 6.75, 1.3, 6.1, 0.42, size=14, bold=True, color=BLUE)
ipc = [
    "task_assignment       →  main sends task to subagent",
    "idle_notification     ←  sub reports task done",
    "agent_progress        ←  sub reports each step",
    "permission_request    ←  sub asks for permission",
    "permission_response   →  main approves/denies",
    "plan_approval_request / response",
    "shutdown_request / approved / rejected",
]
cy2 = 1.84
for m in ipc:
    txt(s, m, 6.75, cy2, 6.1, 0.33, size=11.5, color=INK)
    cy2 += 0.33

box(s, 6.55, 4.6, 6.5, 2.65, fill_color=CARD)
box(s, 6.55, 4.6, 6.5, 0.52, fill_color=LGREEN)
txt(s, "Agent Memory Directories", 6.75, 4.65, 6.1, 0.42, size=14, bold=True, color=GREEN)
mem = [
    (".claude/agent-memory/",       "Project scope — version-controlled, shared"),
    ("~/.claude/agent-memory/",     "User scope — cross-project"),
    (".claude/agent-memory-local/", "Local — not committed to git"),
]
cy3 = 5.22
for path, note in mem:
    txt(s, path, 6.75, cy3, 3.5, 0.33, size=12, bold=True, color=GREEN)
    txt(s, note, 6.75, cy3+0.35, 6.1, 0.28, size=11.5, color=MUTED)
    cy3 += 0.72


# ══════════════════════════════════════════════════════════════════
# SLIDE 17 – Section 06
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "06", "Hooks",
              "21 lifecycle events · command & prompt hook types")


# ══════════════════════════════════════════════════════════════════
# SLIDE 18 – Hooks
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Hooks — Lifecycle Event System  (Source: binary 2.1.72)")

events = [
    "PreToolUse", "PostToolUse", "PostToolUseFailure",
    "UserPromptSubmit", "Notification", "SessionStart",
    "SessionEnd", "Stop", "SubagentStart", "SubagentStop",
    "PreCompact", "PermissionRequest", "Setup", "TeammateIdle",
    "TaskCompleted", "Elicitation", "ElicitationResult",
    "ConfigChange", "WorktreeCreate", "WorktreeRemove",
    "InstructionsLoaded",
]
txt(s, "21 supported events:", 0.4, 1.15, 4, 0.38, size=13, bold=True, color=INK)
cols_e = 7
for i, ev in enumerate(events):
    col_e = i % cols_e
    row_e = i // cols_e
    x = 0.4 + col_e * 1.85
    y = 1.55 + row_e * 0.42
    bg_ev = LBLUE if "Tool" in ev else CARD
    fg_ev = BLUE if "Tool" in ev else MUTED
    box(s, x, y, 1.78, 0.34, fill_color=bg_ev, line_color=fg_ev, lw=Pt(0.8))
    txt(s, ev, x+0.06, y+0.03, 1.68, 0.3, size=10, color=fg_ev, bold=("Tool" in ev))

# Two hook type tables
box(s, 0.4, 3.12, 6.0, 4.05, fill_color=CARD)
box(s, 0.4, 3.12, 6.0, 0.52, fill_color=LGREEN)
txt(s, "command  hook type", 0.62, 3.17, 5.6, 0.42, size=15, bold=True, color=GREEN)
cmd_fields = [
    ("command",       True,  "Shell command to run"),
    ("timeout",       False, "Seconds before kill"),
    ("statusMessage", False, "Spinner label in UI"),
    ("once",          False, "Remove after first run"),
    ("async",         False, "Non-blocking background"),
    ("asyncRewake",   False, "Background; exit code 2 wakes model"),
]
cy4 = 3.72
for field, req, note in cmd_fields:
    c4 = GREEN if req else MUTED
    txt(s, field, 0.62, cy4, 2.3, 0.38, size=12.5, bold=req, color=c4)
    txt(s, note,  3.0,  cy4, 3.2, 0.38, size=12.5, color=INK)
    cy4 += 0.42

box(s, 6.9, 3.12, 6.1, 4.05, fill_color=CARD)
box(s, 6.9, 3.12, 6.1, 0.52, fill_color=LPURPLE)
txt(s, "prompt  hook type", 7.1, 3.17, 5.8, 0.42, size=15, bold=True, color=PURPLE)
prm_fields = [
    ("prompt",        True,  "Prompt text ($ARGUMENTS = hook input JSON)"),
    ("model",         False, "LLM model to use (default: small fast model)"),
    ("timeout",       False, "Seconds before abort"),
    ("statusMessage", False, "Spinner label"),
    ("once",          False, "Remove after first run"),
]
cy5 = 3.72
for field, req, note in prm_fields:
    c5 = PURPLE if req else MUTED
    txt(s, field, 7.1, cy5, 2.3, 0.38, size=12.5, bold=req, color=c5)
    txt(s, note,  9.45, cy5, 3.3, 0.38, size=12.5, color=INK)
    cy5 += 0.42

box(s, 0.4, 7.24, 12.6, 0.2, fill_color=CARD2)
txt(s, "Hook executions appear in JSONL as progress records  ·  "
    "hookName format: \"PostToolUse:Read\"",
    0.6, 7.22, 12.2, 0.22, size=11, color=MUTED, italic=True)


# ══════════════════════════════════════════════════════════════════
# SLIDE 19 – Section 07
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "07", "Permission System",
              "Two-layer design · Bash matching logic · permission modes")


# ══════════════════════════════════════════════════════════════════
# SLIDE 20 – Permission System
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Permission System — Two Independent Layers")

# Layer 1
box(s, 0.4, 1.22, 12.6, 2.75, fill_color=LBLUE)
left_bar(s, 0.4, 1.22, 2.75, BLUE, w=0.38)
txt(s, "Layer 1 — Tool Permission System  (configurable via settings.json)",
    0.95, 1.3, 10, 0.42, size=15, bold=True, color=BLUE)
txt(s, 'permissions.allow: ["Edit", "Bash(git:*)", "WebFetch(domain:docs.anthropic.com)"]',
    0.95, 1.78, 12, 0.38, size=13, color=INK, italic=True)

txt(s, "Bash Matching Rules  (Source: binary functions Nc$, IKL, aVH):",
    0.95, 2.22, 8, 0.38, size=13, bold=True, color=BLUE)
bash_rules = [
    ("prefix  Bash(git:*)",     BLUE,   "matches: git / git status / xargs git — but NEVER compound commands"),
    ("exact   Bash(git status)", GREEN,  "matches only that exact string"),
    ("wildcard Bash(git *)",     ORANGE, "glob-style pattern matching"),
]
cy6 = 2.65
for rule, col6, note in bash_rules:
    txt(s, rule, 1.1, cy6, 3.0, 0.32, size=12.5, bold=True, color=col6)
    txt(s, note, 4.2, cy6, 8.6, 0.32, size=12.5, color=INK)
    cy6 += 0.36

# Anti-jailbreak
box(s, 0.9, 3.7, 12.1, 0.4, fill_color=LRED, line_color=RED, lw=Pt(1.0))
txt(s, "Security: compound commands (&&, ||, ;, |) NEVER match prefix rules — "
    "prevents \"git status && rm -rf /\" bypass",
    1.1, 3.74, 11.7, 0.32, size=12.5, bold=True, color=RED)

# Layer 2
box(s, 0.4, 4.22, 12.6, 1.45, fill_color=LPURPLE)
left_bar(s, 0.4, 4.22, 1.45, PURPLE, w=0.38)
txt(s, "Layer 2 — Judgement Confirmation  (NOT configurable)",
    0.95, 4.3, 10, 0.42, size=15, bold=True, color=PURPLE)
txt(s, "Claude independently pauses when: action exceeds request scope · unexpected state detected · request is ambiguous.\n"
    "Cannot be turned off by allow rules. This reflects Claude's own risk assessment.",
    0.95, 4.78, 12, 0.78, size=13, color=INK)

# Permission Modes
box(s, 0.4, 5.82, 12.6, 1.52, fill_color=CARD)
box(s, 0.4, 5.82, 12.6, 0.5, fill_color=CARD2)
txt(s, "Permission Modes  (global behaviour, separate from allow rules)",
    0.6, 5.88, 9, 0.38, size=14, bold=True, color=INK)
modes2 = [
    ("default",            MUTED,  "Ask for everything not explicitly allowed"),
    ("acceptEdits",        BLUE,   "Auto-accept file edits; Bash still needs confirmation"),
    ("bypassPermissions",  RED,    "Skip all tool permission checks (dangerous)"),
    ("dontAsk",            ORANGE, "No confirmations at all"),
    ("plan",               PURPLE, "Planning only — restricts actual execution"),
    ("auto",               MUTED,  "Non-interactive (claude -p); internal use"),
]
cx7, cy7 = 0.6, 6.4
for mode, col7, note in modes2:
    txt(s, mode, cx7, cy7, 2.0, 0.3, size=11.5, bold=True, color=col7)
    txt(s, note, cx7+2.05, cy7, 3.8, 0.3, size=11, color=INK)
    cx7 += 4.1
    if cx7 > 8.5:
        cx7 = 0.6; cy7 += 0.38


# ══════════════════════════════════════════════════════════════════
# SLIDE 21 – Section 08
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_slide(s, "08", "Extended Thinking",
              "Plaintext vs encrypted — two states of the thinking block")


# ══════════════════════════════════════════════════════════════════
# SLIDE 22 – Extended Thinking
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Extended Thinking — What's Actually in the JSONL")

# Two states
box(s, 0.4, 1.28, 6.05, 4.35, fill_color=CARD)
box(s, 0.4, 1.28, 6.05, 0.52, fill_color=LGREEN)
txt(s, "State A — Plaintext  (legacy enabled mode)", 0.62, 1.33, 5.7, 0.42, size=14, bold=True, color=GREEN)
code_a = ('{\n'
          '  "type": "thinking",\n'
          '  "thinking": "Let me reason about...",\n'
          '  "signature": "EpYCC..."\n'
          '}')
txt(s, code_a, 0.62, 1.88, 5.7, 1.6, size=12, color=GREEN)
txt(s, "thinking field contains readable text.\n"
    "Beta flag: interleaved-thinking-2025-05-14\n"
    "Status: deprecated",
    0.62, 3.55, 5.7, 1.0, size=12.5, color=INK)

box(s, 6.95, 1.28, 6.05, 4.35, fill_color=CARD)
box(s, 6.95, 1.28, 6.05, 0.52, fill_color=LPURPLE)
txt(s, "State B — Encrypted  (adaptive mode, current default)", 7.17, 1.33, 5.7, 0.42, size=14, bold=True, color=PURPLE)
code_b = ('{\n'
          '  "type": "thinking",\n'
          '  "thinking": "",\n'
          '  "signature": "EpYCCkYIARAAGiA... (longer)"\n'
          '}')
txt(s, code_b, 7.17, 1.88, 5.7, 1.6, size=12, color=PURPLE)
txt(s, "thinking field is empty string.\n"
    "Server processes thinking internally.\n"
    "Beta flag: adaptive-thinking-2026-01-28",
    7.17, 3.55, 5.7, 1.0, size=12.5, color=INK)

# Signature
box(s, 0.4, 5.8, 12.6, 0.88, fill_color=LPURPLE, line_color=PURPLE, lw=Pt(1.0))
txt(s, "signature field:", 0.65, 5.88, 2.5, 0.38, size=13, bold=True, color=PURPLE)
txt(s, "Cryptographic proof that the thinking block is genuine — "
    "prevents injecting fake thinking into subsequent turns.",
    3.15, 5.88, 9.7, 0.38, size=13, color=INK)

# Settings
box(s, 0.4, 6.8, 12.6, 0.55, fill_color=CARD2)
txt(s, "Settings: alwaysThinkingEnabled (default true)  ·  "
    "showThinkingSummaries: show in ctrl+o transcript view (default false)  ·  "
    "Toggle in Claude Code UI Settings dialog",
    0.6, 6.86, 12.2, 0.42, size=12, color=MUTED)


# ══════════════════════════════════════════════════════════════════
# SLIDE 23 – Key Takeaways
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_title(s, "Key Takeaways")

takeaways = [
    (BLUE,   LBLUE,   "Agentic Loop",
     "One inference can batch-emit multiple tool_use blocks (parallel execution). "
     "Loop ends only when LLM returns no tool_use. Subagents have independent loops."),
    (GREEN,  LGREEN,  "Tool Loading Strategy",
     "9 pre-loaded (zero latency) vs 16 deferred (save tokens, +1 round-trip via ToolSearch). "
     "Dedicated tools bypass shell — finer permission granularity than Bash."),
    (PURPLE, LPURPLE, "Skill System",
     "allowed-tools is soft (context shared). Agent tool is hard (API-level isolation). "
     "! prefix runs preprocessing before LLM sees content."),
    (ORANGE, LORANGE, "Subagent Design",
     "Different models can coexist in one session (Haiku for Explore, Sonnet for main). "
     "All subagent activity captured in parent JSONL as agent_progress."),
    (RED,    LRED,    "Permission Security",
     "Compound commands never match prefix rules — anti-jailbreak by design (verified in source). "
     "Layer 2 judgement confirmation is not configurable."),
    (YELLOW, LYELLOW, "Observability",
     "JSONL records everything: tool calls, hooks, subagent steps, token usage. "
     "Permission dialogs go through IPC only — they do NOT appear in JSONL."),
]

cy = 1.22
for col, bg_c, title, body in takeaways:
    box(s, 0.4, cy, 12.6, 0.95, fill_color=bg_c)
    left_bar(s, 0.4, cy, 0.95, col, w=0.35)
    txt(s, title, 0.92, cy+0.1, 2.5, 0.38, size=13.5, bold=True, color=col)
    txt(s, body,  3.5,  cy+0.1, 9.35, 0.75, size=12.5, color=INK)
    cy += 1.02


# ══════════════════════════════════════════════════════════════════
# SLIDE 24 – Q&A
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
box(s, 0, 0, 13.33, 7.5, fill_color=BLUE)
box(s, 0.5, 0.5, 12.33, 6.5, fill_color=BG)

txt(s, "Q & A", 1.0, 1.2, 11.3, 1.8, size=72, bold=True, color=INK, align=PP_ALIGN.CENTER)
hline(s, 3.3, x=0.5, w=12.33, color=CARD2, h=0.055)
txt(s, "All findings cross-validated through:",
    1.0, 3.55, 11.3, 0.5, size=17, color=MUTED, align=PP_ALIGN.CENTER)

sources = [
    (BLUE,   LBLUE,   "Session JSONL",    "Runtime ground truth — what actually happened"),
    (GREEN,  LGREEN,  "Source Code",      "Binary 2.1.72 — permission logic, hook schema, tool list"),
    (PURPLE, LPURPLE, "Official Docs",    "docs.anthropic.com — intended design & security guarantees"),
]
cx8 = 1.5
for col, bg_c, label, note in sources:
    box(s, cx8, 4.25, 3.4, 1.35, fill_color=bg_c, line_color=col)
    txt(s, label, cx8+0.15, 4.32, 3.1, 0.45, size=15, bold=True, color=col)
    txt(s, note,  cx8+0.15, 4.82, 3.1, 0.65, size=12, color=INK)
    cx8 += 3.6

# ── Save ───────────────────────────────────────────────────────
out = "/home/user/reseach_claude_code/agent_architecture.pptx"
prs.save(out)
print(f"Saved → {out}")
print(f"Slides: {len(prs.slides)}")
