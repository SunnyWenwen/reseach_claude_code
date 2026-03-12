from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Color Palette ──────────────────────────────────────────────
BG       = RGBColor(0x0D, 0x11, 0x17)   # near-black navy
CARD     = RGBColor(0x16, 0x1D, 0x27)   # card background
ACCENT   = RGBColor(0x00, 0xC8, 0xFF)   # cyan
ACCENT2  = RGBColor(0x7C, 0x3A, 0xED)   # purple
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
MUTED    = RGBColor(0x8B, 0x9C, 0xB1)
GREEN    = RGBColor(0x10, 0xB9, 0x81)
ORANGE   = RGBColor(0xF5, 0x9E, 0x0B)
RED      = RGBColor(0xEF, 0x44, 0x44)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]   # completely blank


# ── Helpers ────────────────────────────────────────────────────

def bg(slide, color=BG):
    """Fill slide background."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, fill_color=None, line_color=None, line_width=Pt(0)):
    from pptx.util import Pt
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.line.width = line_width
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def txt(slide, text, x, y, w, h,
        size=20, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
        italic=False, wrap=True):
    txb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb

def accent_bar(slide, y=0.55, color=ACCENT):
    """Thin horizontal accent line under title."""
    bar = slide.shapes.add_shape(1, Inches(0.6), Inches(y), Inches(3), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

def section_header(slide, number, title, subtitle=""):
    bg(slide)
    # large number watermark
    txt(slide, number, 0.3, 0.5, 3, 2.5, size=120, bold=True,
        color=RGBColor(0x1A, 0x25, 0x35), align=PP_ALIGN.LEFT)
    txt(slide, title, 0.6, 1.6, 11, 1.2, size=44, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, 0.6, 2.9, 10, 0.6, size=20, color=MUTED)

def slide_title(slide, title, subtitle=""):
    txt(slide, title, 0.6, 0.22, 11.5, 0.7, size=28, bold=True, color=WHITE)
    accent_bar(slide, y=0.98)
    if subtitle:
        txt(slide, subtitle, 0.6, 1.05, 11, 0.45, size=15, color=MUTED)

def bullet_block(slide, items, x, y, w, h, title=None, title_color=ACCENT,
                 bullet="▸", size=16, spacing=0.38):
    if title:
        txt(slide, title, x, y, w, 0.35, size=17, bold=True, color=title_color)
        y += 0.38
    for item in items:
        txt(slide, f"{bullet}  {item}", x, y, w, 0.35, size=size, color=WHITE)
        y += spacing

def card(slide, x, y, w, h, title, body_lines,
         title_color=ACCENT, border_color=ACCENT):
    box(slide, x, y, w, h, fill_color=CARD, line_color=border_color, line_width=Pt(1.2))
    txt(slide, title, x+0.15, y+0.12, w-0.3, 0.35,
        size=15, bold=True, color=title_color)
    cy = y + 0.52
    for line in body_lines:
        txt(slide, line, x+0.15, cy, w-0.3, 0.32, size=13, color=WHITE)
        cy += 0.32

def arrow(slide, x1, y1, x2, y2, color=MUTED):
    """Simple line arrow between two points (in inches)."""
    from pptx.util import Emu
    connector = slide.shapes.add_connector(
        1,
        Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    connector.line.color.rgb = color
    connector.line.width = Pt(1.5)


# ══════════════════════════════════════════════════════════════════
# SLIDE 1 – Title
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
# gradient band
box(s, 0, 2.5, 13.33, 3.2, fill_color=RGBColor(0x0A, 0x1A, 0x2E))
# cyan accent stripe
bar = s.shapes.add_shape(1, Inches(0), Inches(2.48), Inches(13.33), Inches(0.06))
bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()

txt(s, "Agent Architecture", 0.8, 2.7, 11.7, 1.1, size=54, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
txt(s, "Best Practices & Patterns for Production Systems", 0.8, 3.85, 11, 0.6, size=22, color=ACCENT, align=PP_ALIGN.LEFT)
txt(s, "Tech Sharing  ·  2026", 0.8, 4.6, 6, 0.4, size=15, color=MUTED)
# decorative dots
for i, (cx, cy, cr, col) in enumerate([
    (11.5, 1.2, 1.2, RGBColor(0x00,0x50,0x70)),
    (12.3, 0.5, 0.6, RGBColor(0x40,0x10,0x80)),
    (10.5, 0.4, 0.35, RGBColor(0x00,0x40,0x60)),
]):
    circle = s.shapes.add_shape(9, Inches(cx-cr), Inches(cy-cr), Inches(cr*2), Inches(cr*2))
    circle.fill.solid(); circle.fill.fore_color.rgb = col; circle.line.fill.background()


# ══════════════════════════════════════════════════════════════════
# SLIDE 2 – Agenda
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Agenda")

topics = [
    ("01", "Why Architecture Matters",   "Common failure modes when scaling agents"),
    ("02", "Core Building Blocks",        "Tools · Memory · Planning · Execution"),
    ("03", "Single vs Multi-Agent",       "When to split, when to stay monolithic"),
    ("04", "Orchestration Patterns",      "Router · Parallel · Pipeline · Supervisor"),
    ("05", "Reliability & Guardrails",    "Retries, self-critique, human-in-the-loop"),
    ("06", "Observability",               "Tracing, evals, cost management"),
    ("07", "Real-world Design Walk-through", "End-to-end case study"),
]

for i, (num, title, desc) in enumerate(topics):
    row = i % 4
    col = i // 4
    x = 0.5 + col * 6.55
    y = 1.15 + row * 1.52
    if i >= 4:
        y = 1.15 + (i-4) * 1.52
    bx = box(s, x, y, 6.1, 1.35, fill_color=CARD, line_color=ACCENT if i==0 else RGBColor(0x25,0x35,0x45))
    txt(s, num, x+0.15, y+0.08, 0.7, 0.45, size=22, bold=True, color=ACCENT)
    txt(s, title, x+0.8, y+0.08, 5.1, 0.45, size=17, bold=True, color=WHITE)
    txt(s, desc, x+0.8, y+0.58, 5.1, 0.5, size=13, color=MUTED)


# ══════════════════════════════════════════════════════════════════
# SLIDE 3 – Section 01
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "01", "Why Architecture Matters",
               "The gap between a demo and a production agent")


# ══════════════════════════════════════════════════════════════════
# SLIDE 4 – Common Failure Modes
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Common Failure Modes in Naive Agent Designs")

failures = [
    ("Context Overflow",   RED,    ["Long task chains exceed context window",  "No summarization → hallucination spikes"]),
    ("Cascading Errors",   ORANGE, ["One bad tool call poisons all downstream", "No retry / validation boundary"]),
    ("Runaway Loops",      RED,    ["No termination condition", "Infinite self-correction loops"]),
    ("God-Agent",          ORANGE, ["Everything in one prompt → unmaintainable", "Hard to debug, impossible to unit-test"]),
    ("Blind Execution",    ACCENT2,["No observability into sub-steps",          "Can't diagnose failures post-hoc"]),
    ("Trust Without Verify", ACCENT2,["Tool outputs accepted verbatim",          "Prompt injection via environment"]),
]

positions = [
    (0.4,  1.2), (4.65, 1.2), (8.9,  1.2),
    (0.4,  3.55),(4.65, 3.55),(8.9,  3.55),
]
for (title, col, lines), (x, y) in zip(failures, positions):
    card(s, x, y, 4.1, 2.1, title, lines, title_color=col, border_color=col)


# ══════════════════════════════════════════════════════════════════
# SLIDE 5 – Section 02
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "02", "Core Building Blocks",
               "The four pillars every agent is composed of")


# ══════════════════════════════════════════════════════════════════
# SLIDE 6 – Four Pillars
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "The Four Pillars of an Agent")

pillars = [
    ("🛠  Tools",    ACCENT,  [
        "Wrap every external call as a typed function",
        "Return structured errors, never raw exceptions",
        "Idempotent where possible",
        "Rate-limit & timeout at the tool layer",
    ]),
    ("🧠  Memory",   ACCENT2, [
        "In-context  – current scratchpad",
        "External    – vector store / DB lookup",
        "Episodic    – past conversation summaries",
        "Procedural  – learned skill / few-shot cache",
    ]),
    ("📋  Planning", GREEN,   [
        "ReAct: reason then act, one step at a time",
        "Plan-and-Execute: upfront decomposition",
        "Tree-of-Thought for branching decisions",
        "Reflection loop for quality gates",
    ]),
    ("⚙️  Execution", ORANGE,  [
        "Sequential vs parallel tool calls",
        "Structured output (JSON schema) enforced",
        "Deterministic seed for reproducibility",
        "Hard stop on iteration budget",
    ]),
]

for i, (title, col, items) in enumerate(pillars):
    x = 0.35 + i * 3.22
    box(s, x, 1.1, 3.05, 5.9, fill_color=CARD, line_color=col)
    # top colored bar
    top = s.shapes.add_shape(1, Inches(x), Inches(1.1), Inches(3.05), Inches(0.08))
    top.fill.solid(); top.fill.fore_color.rgb = col; top.line.fill.background()
    txt(s, title, x+0.12, 1.22, 2.8, 0.45, size=16, bold=True, color=col)
    cy = 1.72
    for item in items:
        txt(s, f"• {item}", x+0.12, cy, 2.8, 0.4, size=12.5, color=WHITE)
        cy += 0.44


# ══════════════════════════════════════════════════════════════════
# SLIDE 7 – Section 03
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "03", "Single vs Multi-Agent",
               "Choosing the right scope for your use case")


# ══════════════════════════════════════════════════════════════════
# SLIDE 8 – Single vs Multi comparison
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Single-Agent vs Multi-Agent: Decision Framework")

# left column
box(s, 0.4, 1.1, 5.9, 5.8, fill_color=CARD, line_color=GREEN)
txt(s, "✅  Single Agent", 0.55, 1.18, 5.6, 0.5, size=18, bold=True, color=GREEN)
single_items = [
    "Task fits in one context window",
    "Linear, sequential workflow",
    "Low latency is critical",
    "Simple tool surface (< ~8 tools)",
    "Easy to test end-to-end",
    "No parallelism needed",
    "",
    "Examples:",
    "  • Customer support bot",
    "  • Code review assistant",
    "  • Single-document summarizer",
]
cy = 1.75
for item in single_items:
    col = MUTED if item.startswith("  •") else (ACCENT if item == "Examples:" else WHITE)
    txt(s, item, 0.7, cy, 5.4, 0.35, size=13.5, color=col)
    cy += 0.35

# right column
box(s, 6.8, 1.1, 6.1, 5.8, fill_color=CARD, line_color=ACCENT2)
txt(s, "🔀  Multi-Agent", 6.95, 1.18, 5.8, 0.5, size=18, bold=True, color=ACCENT2)
multi_items = [
    "Task too large for one context",
    "Subtasks can run in parallel",
    "Need independent verification",
    "Domain specialists reduce errors",
    "Independent scaling per sub-task",
    "Fault isolation between agents",
    "",
    "Examples:",
    "  • Full-stack code generation",
    "  • Research + analysis pipeline",
    "  • Multi-step data transformation",
]
cy = 1.75
for item in multi_items:
    col = MUTED if item.startswith("  •") else (ACCENT if item == "Examples:" else WHITE)
    txt(s, item, 6.95, cy, 5.7, 0.35, size=13.5, color=col)
    cy += 0.35

txt(s, "vs", 6.1, 3.6, 0.6, 0.5, size=22, bold=True, color=MUTED, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════
# SLIDE 9 – Section 04
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "04", "Orchestration Patterns",
               "How agents coordinate and delegate")


# ══════════════════════════════════════════════════════════════════
# SLIDE 10 – Router Pattern
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Pattern 1 — Router / Classifier",
            "Dispatch requests to specialized sub-agents based on intent")

# diagram
box(s, 5.4, 1.5, 2.5, 0.7, fill_color=ACCENT2)
txt(s, "Router Agent", 5.4, 1.5, 2.5, 0.7, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

agents = [
    (1.5,  3.2, "Code Agent",    ACCENT),
    (5.4,  3.2, "Search Agent",  GREEN),
    (9.3,  3.2, "Data Agent",    ORANGE),
]
for ax, ay, label, col in agents:
    box(s, ax, ay, 2.5, 0.7, fill_color=col)
    txt(s, label, ax, ay, 2.5, 0.7, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# arrows (approximate connectors via lines)
for ax, ay, _, _ in agents:
    arrow(s, 6.65, 2.2, ax+1.25, ay, color=MUTED)

txt(s, "User Request", 5.4, 0.5, 2.5, 0.6, size=14, color=MUTED, align=PP_ALIGN.CENTER)
arrow(s, 6.65, 1.1, 6.65, 1.5, color=MUTED)

# key points
box(s, 0.4, 4.2, 12.5, 2.8, fill_color=CARD, line_color=ACCENT2)
txt(s, "Design Principles", 0.6, 4.3, 6, 0.4, size=15, bold=True, color=ACCENT2)
points = [
    "Router uses cheap/fast model (e.g. Haiku) — save expensive calls for specialists",
    "Intent classification should be a structured output with confidence score",
    "Fallback to 'general' agent when confidence < threshold",
    "Routing decision is logged for offline analysis and retraining",
]
cy = 4.75
for p in points:
    txt(s, f"▸  {p}", 0.6, cy, 12, 0.38, size=13.5, color=WHITE)
    cy += 0.42


# ══════════════════════════════════════════════════════════════════
# SLIDE 11 – Parallel Pattern
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Pattern 2 — Parallel Fan-out / Fan-in",
            "Run independent sub-tasks concurrently, aggregate results")

box(s, 5.4, 1.3, 2.5, 0.7, fill_color=CARD, line_color=ACCENT)
txt(s, "Orchestrator", 5.4, 1.3, 2.5, 0.7, size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

workers = [
    (0.4,  3.0, "Worker A"),
    (3.5,  3.0, "Worker B"),
    (6.6,  3.0, "Worker C"),
    (9.7,  3.0, "Worker D"),
]
for wx, wy, label in workers:
    box(s, wx, wy, 2.7, 0.65, fill_color=CARD, line_color=GREEN)
    txt(s, label, wx, wy, 2.7, 0.65, size=14, bold=True, color=GREEN, align=PP_ALIGN.CENTER)
    arrow(s, 6.65, 2.0, wx+1.35, wy, color=MUTED)

box(s, 5.4, 4.1, 2.5, 0.7, fill_color=CARD, line_color=ACCENT2)
txt(s, "Aggregator", 5.4, 4.1, 2.5, 0.7, size=14, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
for wx, wy, _ in workers:
    arrow(s, wx+1.35, wy+0.65, 6.65, 4.1, color=MUTED)

tips = [
    "Use asyncio / thread pool — don't serialize parallel work",
    "Aggregator does dedup, conflict resolution, and synthesis",
    "Set timeout per worker; partial results are still useful",
    "Workers are stateless — all context passed via input payload",
]
cy = 5.1
box(s, 0.4, 4.95, 12.5, 2.15, fill_color=CARD, line_color=GREEN)
for tip in tips:
    txt(s, f"▸  {tip}", 0.6, cy, 12, 0.38, size=13.5, color=WHITE)
    cy += 0.42


# ══════════════════════════════════════════════════════════════════
# SLIDE 12 – Pipeline Pattern
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Pattern 3 — Pipeline (Sequential Stages)",
            "Each stage transforms output and passes it forward")

stages = [
    (0.5,  "Ingest\n& Parse",   ACCENT),
    (3.1,  "Enrich\n& Research",GREEN),
    (5.7,  "Reason\n& Plan",    ACCENT2),
    (8.3,  "Execute\n& Act",    ORANGE),
    (10.9, "Validate\n& Output",RED),
]
y_box = 2.0
for x, label, col in stages:
    box(s, x, y_box, 2.3, 1.1, fill_color=col)
    txt(s, label, x+0.05, y_box+0.15, 2.2, 0.8, size=14, bold=True,
        color=WHITE, align=PP_ALIGN.CENTER)
    if x < 10.9:
        arrow(s, x+2.3, y_box+0.55, x+3.1, y_box+0.55, color=WHITE)

# stage details below
details = [
    ["PDF/HTML parse", "Chunk & embed", "Schema validate"],
    ["Web search", "DB lookup", "Knowledge graph"],
    ["Decompose task", "Build plan tree", "Resource alloc"],
    ["Call APIs/tools", "Write files/code", "Retry on error"],
    ["Unit test / eval", "Human gate", "Structured output"],
]
for i, (x, _, col) in enumerate(stages):
    cy = 3.35
    for d in details[i]:
        txt(s, f"• {d}", x+0.05, cy, 2.2, 0.35, size=12, color=MUTED)
        cy += 0.37

box(s, 0.4, 5.25, 12.5, 1.85, fill_color=CARD, line_color=ACCENT2)
txt(s, "Key principle: each stage has a defined input/output contract — test them independently",
    0.6, 5.35, 12, 0.45, size=15, color=WHITE)
txt(s, "Add a 'circuit breaker' between stages — abort early rather than propagating bad data downstream",
    0.6, 5.82, 12, 0.45, size=15, color=WHITE)
txt(s, "Store intermediate artifacts — enable resumption without re-running expensive early stages",
    0.6, 6.29, 12, 0.45, size=15, color=WHITE)


# ══════════════════════════════════════════════════════════════════
# SLIDE 13 – Supervisor Pattern
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Pattern 4 — Supervisor / Hierarchical",
            "A meta-agent monitors, validates, and re-tasks workers")

box(s, 4.4, 1.2, 4.5, 0.85, fill_color=RGBColor(0x1A,0x10,0x40), line_color=ACCENT2)
txt(s, "Supervisor Agent", 4.4, 1.2, 4.5, 0.85, size=17, bold=True,
    color=ACCENT2, align=PP_ALIGN.CENTER)

workers2 = [(0.4, 3.0), (4.7, 3.0), (9.0, 3.0)]
wlabels  = ["Researcher", "Coder", "Reviewer"]
wcolors  = [ACCENT, GREEN, ORANGE]
for (wx, wy), label, col in zip(workers2, wlabels, wcolors):
    box(s, wx, wy, 3.6, 0.75, fill_color=CARD, line_color=col)
    txt(s, label, wx, wy, 3.6, 0.75, size=15, bold=True, color=col, align=PP_ALIGN.CENTER)
    arrow(s, 6.65, 2.05, wx+1.8, wy, color=MUTED)
    arrow(s, wx+1.8, wy+0.75, 6.65, 1.2+0.85, color=MUTED)

responsibilities = [
    "Evaluates each worker's output against a rubric before passing it on",
    "Can re-task the same worker with corrective feedback (reflection loop)",
    "Maintains a shared state / working memory visible to all workers",
    "Enforces iteration budget — escalates to human if not converging",
    "Can spawn additional workers dynamically based on task complexity",
]
box(s, 0.4, 4.15, 12.5, 3.0, fill_color=CARD, line_color=ACCENT2)
txt(s, "Supervisor Responsibilities", 0.6, 4.22, 8, 0.38, size=15, bold=True, color=ACCENT2)
cy = 4.65
for r in responsibilities:
    txt(s, f"▸  {r}", 0.6, cy, 12.1, 0.38, size=13.5, color=WHITE)
    cy += 0.42


# ══════════════════════════════════════════════════════════════════
# SLIDE 14 – Section 05
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "05", "Reliability & Guardrails",
               "Building agents that fail gracefully")


# ══════════════════════════════════════════════════════════════════
# SLIDE 15 – Reliability Patterns
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Reliability Patterns")

patterns = [
    ("Structured Output Validation", ACCENT, [
        "Enforce JSON schema on every LLM response",
        "Re-prompt up to N times on parse failure",
        "Fallback to a simpler model if still failing",
    ]),
    ("Self-Critique / Reflection", GREEN, [
        "After each major action, ask: 'Is this correct?'",
        "Use a separate evaluator prompt (not self-review)",
        "Stop if reflection score > threshold",
    ]),
    ("Human-in-the-Loop Gates", ACCENT2, [
        "Define irreversible actions (delete, send, deploy)",
        "Pause and surface for human approval",
        "Async approval queue for non-blocking flow",
    ]),
    ("Iteration Budget", ORANGE, [
        "Hard cap on tool calls per task (e.g. 25)",
        "Soft warning at 80% budget consumed",
        "Return partial result rather than timing out",
    ]),
    ("Idempotency & Rollback", RED, [
        "Tag each action with a correlation ID",
        "Write-ahead log before any side effect",
        "Automated rollback on agent failure",
    ]),
    ("Prompt Injection Defense", MUTED, [
        "Sanitize tool output before inserting to context",
        "Separate system / user / tool content clearly",
        "Validate that instructions come from trusted source",
    ]),
]
positions_r = [
    (0.35, 1.1), (4.55, 1.1), (8.75, 1.1),
    (0.35, 3.75),(4.55, 3.75),(8.75, 3.75),
]
for (title, col, lines), (x, y) in zip(patterns, positions_r):
    card(s, x, y, 4.1, 2.45, title, lines, title_color=col, border_color=col)


# ══════════════════════════════════════════════════════════════════
# SLIDE 16 – Section 06
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "06", "Observability",
               "You can't improve what you can't measure")


# ══════════════════════════════════════════════════════════════════
# SLIDE 17 – Observability Stack
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Observability Stack for Agents")

layers = [
    (0.4, 1.15, 12.5, "Tracing  —  full span tree per agent run (OpenTelemetry / LangSmith / Langfuse)", ACCENT),
    (0.4, 2.1,  12.5, "Evals    —  automated quality scoring: correctness, groundedness, tool accuracy",  GREEN),
    (0.4, 3.05, 12.5, "Metrics  —  latency p50/p95, token usage, tool call count, success rate",           ACCENT2),
    (0.4, 4.0,  12.5, "Logging  —  structured JSON logs: every prompt, every tool call, every output",     ORANGE),
    (0.4, 4.95, 12.5, "Alerts   —  anomaly detection on token spike, error rate, cost per task",           RED),
]
for x, y, w, text, col in layers:
    box(s, x, y, w, 0.75, fill_color=CARD, line_color=col)
    left_bar = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(0.07), Inches(0.75))
    left_bar.fill.solid(); left_bar.fill.fore_color.rgb = col; left_bar.line.fill.background()
    txt(s, text, x+0.2, y+0.16, w-0.3, 0.42, size=14.5, color=WHITE)

box(s, 0.4, 6.0, 12.5, 1.25, fill_color=CARD, line_color=MUTED)
txt(s, "Golden Rule:", 0.6, 6.08, 3, 0.38, size=14, bold=True, color=ACCENT)
txt(s, "Every agent decision must be reproducible from logs alone — no black-box failures allowed.",
    0.6, 6.08, 12, 0.38, size=14, color=WHITE)
txt(s, "Store: full conversation history · tool schemas used · model version · temperature · seed",
    0.6, 6.52, 12, 0.45, size=13, color=MUTED)


# ══════════════════════════════════════════════════════════════════
# SLIDE 18 – Section 07
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
section_header(s, "07", "Design Walk-through",
               "End-to-end: AI-powered code review system")


# ══════════════════════════════════════════════════════════════════
# SLIDE 19 – Case Study Architecture
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Case Study: Multi-Agent Code Review System")

# Row 1: Input + Router
box(s, 0.4, 1.1, 2.5, 0.75, fill_color=CARD, line_color=MUTED)
txt(s, "PR / Diff Input", 0.4, 1.1, 2.5, 0.75, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
arrow(s, 2.9, 1.47, 3.3, 1.47, color=MUTED)

box(s, 3.3, 1.1, 2.5, 0.75, fill_color=CARD, line_color=ACCENT)
txt(s, "Router Agent\n(Haiku)", 3.3, 1.1, 2.5, 0.75, size=12, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

# Row 2: Specialists
specialists = [
    (0.4,  2.5, "Security\nAnalyst",  RED),
    (3.5,  2.5, "Code Quality\nAgent", GREEN),
    (6.6,  2.5, "Test Coverage\nAgent", ACCENT2),
    (9.7,  2.5, "Doc Check\nAgent",  ORANGE),
]
for sx, sy, label, col in specialists:
    box(s, sx, sy, 2.7, 0.85, fill_color=CARD, line_color=col)
    txt(s, label, sx, sy, 2.7, 0.85, size=12, bold=True, color=col, align=PP_ALIGN.CENTER)
    arrow(s, 4.55, 1.85, sx+1.35, sy, color=MUTED)

# Row 3: Supervisor + Output
arrow(s, 1.75, 3.35, 5.5, 4.1, color=MUTED)
arrow(s, 4.85, 3.35, 5.9, 4.1, color=MUTED)
arrow(s, 7.95, 3.35, 6.3, 4.1, color=MUTED)
arrow(s, 11.05, 3.35, 6.7, 4.1, color=MUTED)

box(s, 4.5, 4.1, 4.3, 0.85, fill_color=RGBColor(0x1A,0x10,0x40), line_color=ACCENT2)
txt(s, "Supervisor Agent  (Sonnet)", 4.5, 4.1, 4.3, 0.85, size=13, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)

arrow(s, 6.65, 4.95, 6.65, 5.35, color=MUTED)
box(s, 4.5, 5.35, 4.3, 0.75, fill_color=CARD, line_color=GREEN)
txt(s, "Final Review Report", 4.5, 5.35, 4.3, 0.75, size=13, bold=True, color=GREEN, align=PP_ALIGN.CENTER)

# Annotations
txt(s, "Parallel execution\n~3× faster", 0.1, 2.1, 2.5, 0.5, size=10, color=MUTED, italic=True)
txt(s, "Human gate for\ncritical issues", 9.2, 4.1, 3.8, 0.5, size=10, color=MUTED, italic=True)


# ══════════════════════════════════════════════════════════════════
# SLIDE 20 – Key Takeaways
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
slide_title(s, "Key Takeaways")

takeaways = [
    (ACCENT,  "1",  "Start with the simplest architecture that works — add multi-agent complexity only when needed"),
    (GREEN,   "2",  "Define clear contracts (input/output schemas) at every boundary — agents, tools, and stages"),
    (ACCENT2, "3",  "Reliability is architecture, not afterthought — budget, retry, validate, and rollback by design"),
    (ORANGE,  "4",  "Observability is non-negotiable — trace every decision, eval every output, alert on anomalies"),
    (RED,     "5",  "Use the right model for the right job — cheap/fast for routing; powerful for complex reasoning"),
    (MUTED,   "6",  "Think in patterns — Router, Parallel, Pipeline, Supervisor cover 90% of production use cases"),
]

for i, (col, num, text) in enumerate(takeaways):
    y = 1.15 + i * 1.02
    box(s, 0.4, y, 12.5, 0.88, fill_color=CARD, line_color=col)
    circle = s.shapes.add_shape(9, Inches(0.52), Inches(y+0.12), Inches(0.62), Inches(0.62))
    circle.fill.solid(); circle.fill.fore_color.rgb = col; circle.line.fill.background()
    txt(s, num, 0.52, y+0.1, 0.62, 0.62, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, text, 1.3, y+0.2, 11.4, 0.55, size=15, color=WHITE)


# ══════════════════════════════════════════════════════════════════
# SLIDE 21 – Thank You / Q&A
# ══════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
bg(s)
bar2 = s.shapes.add_shape(1, Inches(0), Inches(3.0), Inches(13.33), Inches(0.06))
bar2.fill.solid(); bar2.fill.fore_color.rgb = ACCENT; bar2.line.fill.background()

txt(s, "Questions?", 1.0, 1.2, 11.3, 1.5, size=60, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(s, "Let's build better agents together.", 1.0, 3.3, 11.3, 0.65,
    size=22, color=ACCENT, align=PP_ALIGN.CENTER)

resources = [
    "Anthropic Agent SDK Docs",
    "LangGraph — stateful multi-agent graphs",
    "Langfuse / LangSmith — observability",
    "Evals: RAGAS, PromptFoo, DeepEval",
]
txt(s, "Further Reading", 1.5, 4.3, 10, 0.45, size=16, bold=True, color=MUTED, align=PP_ALIGN.CENTER)
cy = 4.8
for r in resources:
    txt(s, f"→  {r}", 3.5, cy, 6.3, 0.38, size=14, color=MUTED, align=PP_ALIGN.LEFT)
    cy += 0.42

# ── Save ───────────────────────────────────────────────────────
out = "/home/user/reseach_claude_code/agent_architecture.pptx"
prs.save(out)
print(f"Saved → {out}")
print(f"Slides: {len(prs.slides)}")
