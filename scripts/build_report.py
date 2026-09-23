#!/usr/bin/env python3
"""Generate the project verification report from redacted execution evidence."""

import json
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
from fpdf.enums import XPos, YPos


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs' / 'execution-evidence.json'
SCREENSHOT = ROOT / 'assets' / 'n8n-workflow-canvas.png'
OUTPUT = ROOT / 'docs' / 'social-intelligence-publisher-report.pdf'

NAVY = (15, 23, 42)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
LINE = (203, 213, 225)
PALE = (248, 250, 252)
TEAL = (13, 148, 136)
AMBER = (180, 83, 9)


def rtl(value):
    return get_display(arabic_reshaper.reshape(str(value or '')))


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('DejaVu', '', 8)
        self.set_text_color(*MUTED)
        self.cell(0, 6, 'SOCIAL INTELLIGENCE PUBLISHER  /  VERIFICATION REPORT')
        self.ln(8)
        self.set_draw_color(*LINE)
        self.line(10, 17, 200, 17)

    def footer(self):
        self.set_y(-13)
        self.set_font('DejaVu', '', 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f'Verified evidence  |  Page {self.page_no()} of {{nb}}', align='C')

    def section(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(*NAVY)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*TEAL)
        self.set_line_width(0.7)
        self.line(10, self.get_y(), 44, self.get_y())
        self.ln(4)

    def paragraph(self, text, size=8.5, color=SLATE, line_height=4.5):
        self.set_font('DejaVu', '', size)
        self.set_text_color(*color)
        self.multi_cell(0, line_height, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def metric(self, x, y, width, label, value, accent=TEAL):
        self.set_fill_color(*PALE)
        self.set_draw_color(*LINE)
        self.rect(x, y, width, 20, 'DF')
        self.set_xy(x + 4, y + 3)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(*MUTED)
        self.cell(width - 8, 4, label)
        self.set_xy(x + 4, y + 9)
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(*accent)
        self.cell(width - 8, 6, str(value))


def build():
    data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    execution = data['execution']
    counts = data['sources']['counts']
    final = data['final_output']

    pdf = Report()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 18)
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    pdf.set_title('Social Intelligence Publisher — Verification Report')
    pdf.set_author('Hazem Elerefey')

    # Cover
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 82, 'F')
    pdf.set_xy(14, 20)
    pdf.set_font('DejaVu', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'SOCIAL INTELLIGENCE PUBLISHER', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(14)
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(153, 246, 228)
    pdf.cell(0, 7, 'Real n8n execution evidence / production-readiness report', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(14)
    pdf.set_font('DejaVu', '', 8.5)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(0, 6, 'Generated from n8n execution ID 3  |  23 September 2026', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(94)
    pdf.section('Verified outcome')
    pdf.paragraph(
        'The workflow completed a real manual execution using live Hacker News and Dev.to data, '
        'deterministic scoring, and two OpenRouter requests. The final Arabic content pack was '
        'parsed successfully and marked draft_ready.'
    )
    y = pdf.get_y() + 7
    pdf.metric(10, y, 43, 'STATUS', execution['status'].upper())
    pdf.metric(57, y, 43, 'DURATION', f"{execution['duration_ms'] / 1000:.3f}s")
    pdf.metric(104, y, 43, 'LIVE INPUTS', '24')
    pdf.metric(151, y, 49, 'AI COST', f"${data['ai']['total_cost_usd']:.7f}")
    pdf.set_y(y + 29)

    pdf.section('Verification boundary')
    pdf.set_fill_color(255, 247, 237)
    pdf.set_draw_color(253, 186, 116)
    box_y = pdf.get_y()
    pdf.rect(10, box_y, 190, 39, 'DF')
    pdf.set_xy(15, box_y + 5)
    pdf.set_font('DejaVu', 'B', 8.5)
    pdf.set_text_color(*AMBER)
    pdf.cell(0, 5, 'META RELEASE STAGE: NOT YET VERIFIED', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(15)
    pdf.set_font('DejaVu', '', 8)
    pdf.set_text_color(*SLATE)
    pdf.multi_cell(
        180, 4.5,
        'The six Facebook release nodes were disabled during this run while the exposed token is '
        'rotated and replaced with an n8n credential. No Facebook post or comment is claimed as '
        'published in this report.',
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.set_y(box_y + 47)
    pdf.paragraph('No generated screenshots, fabricated HTTP responses, or synthetic execution records are used.')

    # Architecture / source page
    pdf.add_page()
    pdf.section('01  /  Workflow architecture')
    stages = [
        ('CONTROL', '2 nodes', 'Brand policy and editorial angles'),
        ('DISCOVER', '4 nodes', 'Three live feeds, normalization, scoring'),
        ('COMPOSE', '4 nodes', 'Topic selection, generation, validation'),
        ('RELEASE', '6 nodes', 'Facebook post, comment, audit result'),
    ]
    for index, (name, count, note) in enumerate(stages):
        y = pdf.get_y()
        pdf.set_fill_color(*PALE)
        pdf.set_draw_color(*LINE)
        pdf.rect(10, y, 190, 17, 'DF')
        pdf.set_xy(14, y + 3)
        pdf.set_font('DejaVu', 'B', 8)
        pdf.set_text_color(*TEAL)
        pdf.cell(28, 5, f'{index + 1:02d}')
        pdf.set_text_color(*NAVY)
        pdf.cell(34, 5, name)
        pdf.set_font('DejaVu', '', 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(28, 5, count)
        pdf.set_text_color(*SLATE)
        pdf.cell(90, 5, note)
        pdf.set_y(y + 20)

    pdf.ln(2)
    pdf.section('02  /  Live source evidence')
    y = pdf.get_y()
    pdf.metric(10, y, 59, 'HN / AI AUTOMATION', counts['hnAutomationCount'])
    pdf.metric(75, y, 59, 'HN / OPENAI AGENTS', counts['hnOpenAICount'])
    pdf.metric(140, y, 60, 'DEV.TO / AI', counts['devtoCount'])
    pdf.set_y(y + 28)

    pdf.set_font('DejaVu', 'B', 7.5)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(15, 7, 'Rank', border=1, fill=True, align='C')
    pdf.cell(92, 7, 'Candidate', border=1, fill=True)
    pdf.cell(48, 7, 'Source', border=1, fill=True)
    pdf.cell(35, 7, 'Score', border=1, fill=True, align='C')
    pdf.ln()
    for index, candidate in enumerate(data['ranking']['top_candidates'], 1):
        pdf.set_font('DejaVu', '', 7)
        pdf.set_text_color(*SLATE)
        pdf.set_fill_color(*(PALE if index % 2 else (255, 255, 255)))
        pdf.cell(15, 7, str(index), border=1, fill=True, align='C')
        pdf.cell(92, 7, (candidate['title'] or '')[:55], border=1, fill=True)
        pdf.cell(48, 7, (candidate['source'] or '')[:29], border=1, fill=True)
        pdf.cell(35, 7, str(candidate['total_score']), border=1, fill=True, align='C')
        pdf.ln()

    # Output page
    pdf.add_page()
    pdf.section('03  /  Real generated output')
    pdf.set_font('DejaVu', 'B', 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, 'Selected topic', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.paragraph(final['topic'], size=8.5)
    pdf.set_font('DejaVu', '', 7.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, f"Source: {final['source']}  /  Score: {final.get('source_score')}  /  {final['source_url']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.set_fill_color(*PALE)
    pdf.set_draw_color(*LINE)
    start_y = pdf.get_y()
    pdf.rect(10, start_y, 190, 112, 'DF')
    pdf.set_xy(15, start_y + 5)
    pdf.set_font('DejaVu', 'B', 9)
    pdf.set_text_color(*TEAL)
    pdf.cell(180, 6, 'FACEBOOK DRAFT', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(15)
    pdf.set_font('DejaVu', '', 8.5)
    pdf.set_text_color(*NAVY)
    for line in final['facebook_post'].splitlines():
        if not line.strip():
            pdf.ln(2)
            continue
        pdf.set_x(15)
        pdf.multi_cell(180, 5, rtl(line.replace('👇', '↓')), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_y(start_y + 121)
    pdf.set_font('DejaVu', 'B', 8)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 5, 'First comment', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    for line in final['facebook_first_comment'].splitlines():
        pdf.set_font('DejaVu', '', 8)
        pdf.set_text_color(*SLATE)
        pdf.multi_cell(0, 5, rtl(line) if any('\u0600' <= c <= '\u06ff' for c in line) else line, align='R' if any('\u0600' <= c <= '\u06ff' for c in line) else 'L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_font('DejaVu', '', 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, f"Model: {data['ai']['topic_selection']['model']}  /  Final status: {final['status']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Verification page
    pdf.add_page()
    pdf.section('04  /  Node-level execution audit')
    pdf.paragraph('Every node appears in the saved n8n execution. Disabled release nodes passed data through and are marked clearly below.')
    pdf.ln(2)
    pdf.set_font('DejaVu', 'B', 7.2)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(105, 7, 'Node', border=1, fill=True)
    pdf.cell(28, 7, 'Status', border=1, fill=True, align='C')
    pdf.cell(28, 7, 'Time', border=1, fill=True, align='C')
    pdf.cell(29, 7, 'Disabled', border=1, fill=True, align='C')
    pdf.ln()
    for index, node in enumerate(data['node_execution']):
        pdf.set_font('DejaVu', '', 6.9)
        pdf.set_fill_color(*(PALE if index % 2 == 0 else (255, 255, 255)))
        pdf.set_text_color(*SLATE)
        pdf.cell(105, 6.5, node['node'][:62], border=1, fill=True)
        pdf.cell(28, 6.5, node['status'], border=1, fill=True, align='C')
        pdf.cell(28, 6.5, f"{node['duration_ms']} ms", border=1, fill=True, align='C')
        pdf.cell(29, 6.5, 'yes' if node['disabled_during_test'] else 'no', border=1, fill=True, align='C')
        pdf.ln()

    pdf.ln(5)
    pdf.section('05  /  Canvas evidence')
    if SCREENSHOT.exists():
        pdf.paragraph('Authenticated capture of the real n8n canvas after final layout refinement.')
        available_w = 190
        pdf.image(str(SCREENSHOT), x=10, y=pdf.get_y() + 2, w=available_w)
    else:
        pdf.paragraph(
            'Canvas capture pending authenticated browser sign-in. The report generator will embed '
            'assets/n8n-workflow-canvas.png automatically once captured.',
            color=AMBER,
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(OUTPUT)


if __name__ == '__main__':
    build()
