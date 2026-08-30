from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "frames"
OUT.mkdir(exist_ok=True)
W, H = 1920, 1080
NAVY = "#07111f"
PANEL = "#0e1d2f"
TEAL = "#2dd4bf"
ORANGE = "#fb923c"
WHITE = "#f8fafc"
MUTED = "#a8b6c8"
RED = "#fb7185"
GREEN = "#86efac"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def f(size, bold=False): return ImageFont.truetype(BOLD if bold else FONT, size)
def wrap(draw, text, font, width):
    words = text.split(); lines=[]; cur=""
    for word in words:
        nxt = (cur + " " + word).strip()
        if draw.textbbox((0,0), nxt, font=font)[2] <= width: cur=nxt
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def base(kicker, title, subtitle=""):
    im=Image.new("RGB", (W,H), NAVY); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,12), fill=TEAL)
    d.text((90,70), kicker.upper(), font=f(27,True), fill=TEAL)
    d.text((90,120), title, font=f(72,True), fill=WHITE)
    if subtitle:
        y=215
        for line in wrap(d, subtitle, f(30), 1450): d.text((90,y), line, font=f(30), fill=MUTED); y+=44
    d.text((90,1015), "RECRUITMENT GUARD  /  EVIDENCE OPERATIONS", font=f(22,True), fill=MUTED)
    return im,d

def card(d, xy, title, body, accent=TEAL, value=None):
    x,y,w,h=xy; d.rounded_rectangle((x,y,x+w,y+h), radius=22, fill=PANEL, outline="#20354d", width=2)
    d.rectangle((x,y,x+8,y+h), fill=accent)
    d.text((x+32,y+25), title, font=f(27,True), fill=WHITE)
    yy=y+78
    if value is not None:
        d.text((x+32,yy), value, font=f(62,True), fill=accent); yy+=86
    for line in wrap(d, body, f(25), w-64): d.text((x+32,yy), line, font=f(25), fill=MUTED); yy+=37

# 01
im,d=base("A safer handoff", "Recruitment Guard", "A source-bound evidence layer for one role, one recruiter, and one consequential decision boundary.")
card(d,(90,400,700,300),"The promise","Turn scattered hiring evidence into a reviewable brief without hiding contradictions or stale evidence.",TEAL)
card(d,(850,400,700,300),"The boundary","The system never ranks candidates or makes a hire/no-hire decision. It makes the evidence traceable.",ORANGE)
im.save(OUT/"01_title.png")
# 02
im,d=base("The problem", "Fluent summaries can hide broken evidence", "Priya is closing a Backend Engineer role after six weeks. Her bottleneck is reconciliation, not prose.")
card(d,(90,365,500,380),"CV","“Led a team of eight”\n\nStrong ownership claim",ORANGE)
card(d,(650,365,500,380),"Interview","“Mostly me”\n\nDifferent team context",RED)
card(d,(1210,365,500,380),"Assessment","Missing or stale\n\nQuietly omitted by a smooth summary",TEAL)
d.line((590,555,635,555), fill=WHITE, width=5); d.line((1150,555,1195,555), fill=WHITE, width=5)
im.save(OUT/"02_problem.png")
# 03
im,d=base("The baseline", "One prompt. One coherent story.", "The baseline summarizes the CV and transcript, but has no structured comparison, freshness check, or checkpoint.")
card(d,(90,355,820,405),"Baseline output","A polished paragraph can preserve the tone of the packet while dropping the conflict between sources.",ORANGE,value="0 / 3")
card(d,(960,355,750,405),"What it cannot do","Extract comparable facts\nVerify source spans\nBlock stale evidence\nRequest human resolution",RED)
im.save(OUT/"03_baseline.png")
# 04
im,d=base("The guarded path", "The model proposes. Code verifies.", "A compact sequential pipeline turns narrative risk into explicit evidence and an operational checkpoint.")
steps=[("1","Extract","Fixed taxonomy + exact source span"),("2","Validate","Compare subjects + freshness"),("3","Pause","Create owner + due date"),("4","Export","Only after human resolution")]
for i,(n,t,b) in enumerate(steps):
    x=90+i*430; card(d,(x,380,360,300),n,b,TEAL if i<2 else ORANGE,value=t)
im.save(OUT/"04_guarded.png")
# 05
im,d=base("Live product path", "v2.1: ingest → review → brief", "A folder, CSV, or JSON manifest becomes a traceable workflow run with consent, evidence, review, and export events.")
card(d,(90,355,480,390),"01  INGEST","Normalize packet\nValidate consent\nEmit packet_ingested",TEAL)
card(d,(610,355,480,390),"02  REVIEW","Find stale assessment\nAssign recruiter\nSet due date",ORANGE)
card(d,(1130,355,580,390),"03  EXPORT","Resolve with an attributable note\nResume only through the gate\nWrite brief.md + audit.json",GREEN)
im.save(OUT/"05_workflow.png")
# 06
im,d=base("The human checkpoint", "A warning is not a gate", "Packet 004 is withheld because its assessment is stale. The recruiter resolves it; only then can the brief exist.")
card(d,(90,360,470,390),"PENDING_REVIEW","owner: recruiter\ndue: 2026-09-02\nbrief: withheld",ORANGE,value="BLOCK")
card(d,(725,360,470,390),"RECRUITER","Attributable resolution note\n“Reviewer confirmed the evidence context.”",TEAL,value="HUMAN")
card(d,(1360,360,470,390),"FINALIZED","Citations + gaps + audit\nNo score. No rank. No recommendation.",GREEN,value="BRIEF")
d.line((575,555,700,555),fill=WHITE,width=5); d.line((1210,555,1335,555),fill=WHITE,width=5)
im.save(OUT/"06_checkpoint.png")
# 07
im,d=base("Measured comparison", "The guardrail catches what prose misses", "Identical 12-packet synthetic benchmark. Three planted issues, nine clean controls.")
card(d,(90,360,520,390),"Baseline","Simple summarizer",ORANGE,value="0 / 3")
card(d,(700,360,520,390),"Guarded","Extraction + validation + checkpoint",TEAL,value="3 / 3")
card(d,(1310,360,520,390),"Clean controls","False positives",GREEN,value="0 / 9")
im.save(OUT/"07_metrics.png")
# 08
im,d=base("The insight", "Pause is a feature", "In consequential workflows, the best agent output is often a precisely cited reason to pause—not a confident recommendation.")
card(d,(90,390,1650,300),"What reliability means","Make evidence traceable. Surface uncertainty before synthesis. Prevent a review question from silently becoming a hiring decision.",TEAL)
im.save(OUT/"08_hot_take.png")
