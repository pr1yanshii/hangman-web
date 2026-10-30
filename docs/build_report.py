"""Build docs/report.pdf (1–2 pages). Requires reportlab: python3 docs/build_report.py"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).parent / "report.pdf"
GITHUB = "https://github.com/pr1yanshii/hangman-web"
LIVE = "https://hangman-web-0je9.onrender.com"

base = getSampleStyleSheet()
body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=8.6, leading=10.4,
                      spaceAfter=3, alignment=TA_LEFT)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=10, bulletIndent=2, spaceAfter=1.2)
h1 = ParagraphStyle("h1", parent=base["Title"], fontName="Helvetica-Bold", fontSize=14, leading=17, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, fontSize=8.4, textColor=colors.HexColor("#444444"), alignment=1, spaceAfter=5)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=10, leading=12.5, spaceBefore=5,
                    spaceAfter=2, textColor=colors.HexColor("#1f3a68"))
prompt = ParagraphStyle("prompt", parent=body, fontName="Courier", fontSize=7.6, leading=9.2, spaceAfter=0)
note = ParagraphStyle("note", parent=body, fontSize=8.2, leading=10.2, spaceAfter=0)


def link(url):
    return f'<link href="{url}" color="#1f4fb4">{url}</link>'


def bullets(items):
    return [Paragraph(i, bullet, bulletText="•") for i in items]


def prompt_box(title, text, outcome):
    rows = [[Paragraph(f"<b>{title}</b>", note)], [Paragraph(text, prompt)], [Paragraph(outcome, note)]]
    t = Table(rows, colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f2f4f7")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c5cbd3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return [t, Spacer(1, 4)]


story = [
    Paragraph("Hangman Web Application — Development Report", h1),
    Paragraph(f"CSE 4095 Individual Assignment · Priyanshi Sitlani · GitHub: {link(GITHUB)} · Live: {link(LIVE)}", sub),

    Paragraph("1. What I Built", h2),
    Paragraph(
        "For this assignment, I built a Hangman game that you play in a web browser. It is a smaller version of the "
        "course specification. As planned in my <i>TODO.md</i>, I left out the terminal client, bots, evaluation mode, "
        "scoring, leaderboard, and replay system. The project has three parts:", body),
    *bullets([
        "<b>The web page</b> (<i>static/</i> folder): HTML, CSS, and plain JavaScript. This is what the player sees and clicks.",
        "<b>The Flask server</b> (<i>server.py</i>): it receives requests from the page and sends back JSON. It keeps each "
        "game in memory under its own random ID.",
        "<b>The game logic</b> (<i>game.py</i> and <i>words.py</i>): plain Python with no Flask code, so I could test the "
        "rules on their own.",
    ]),
    Paragraph("The most important rule is that the server is in charge. The browser never gets the hidden word until "
              "the game is over.", body),

    Paragraph("2. The Game Logic and the API", h2),
    Paragraph(
        "The <i>HangmanGame</i> class remembers every guess and which ones were wrong. It shows the word as blanks, like "
        "<font face='Courier'>_ i _ _ _ _</font>, and fills in letters as they are guessed. You win when every letter is "
        "showing, and you lose after six wrong guesses. A guess that is not a single letter, was already guessed, or comes "
        "after the game ended is rejected, and nothing changes. The word is only added to the game data once the game is "
        "over, so it can't slip out during play. Each difficulty (Easy, Medium, Hard) has its own list of 55 words.", body),
    Paragraph(
        "The API has three endpoints: <font face='Courier'>POST /api/games</font> starts a game (201), "
        "<font face='Courier'>GET /api/games/&lt;id&gt;</font> returns the current game (200), and "
        "<font face='Courier'>POST /api/games/&lt;id&gt;/guess</font> sends a letter (200). When something goes wrong, the "
        "server sends back a JSON error message with a status code: 400 for a bad request or a repeated guess, 404 if the "
        "game doesn't exist, 405 for the wrong method, and 409 if the game is already over.", body),

    Paragraph("3. The Web Page", h2),
    Paragraph(
        "The page has a difficulty menu, a New Game button, the word as letter tiles, the number of tries left, lists of "
        "correct and wrong guesses, a hangman drawing, and an A–Z keyboard. You can click the letters or type them on your "
        "own keyboard. The drawing has six parts, and one more appears with each wrong guess.", body),
    Paragraph(
        "This is how the page talks to the server. When you press New Game, <i>app.js</i> uses <i>fetch()</i> to send a "
        "POST request to <font face='Courier'>/api/games</font> with the difficulty you picked, and the server "
        "replies with JSON describing the new game. When you guess a letter, the page sends another POST request with that letter and "
        "redraws itself from the reply. The page doesn't decide anything by itself; it just shows what the server sends "
        "back. That is also why New Game works without reloading the page. If the server can't be reached, or the game no "
        "longer exists (for example after a server restart), the page shows a message instead of just breaking. On phones, "
        "the layout switches to one column with a smaller keyboard.", body),

    Paragraph("4. Testing and Deployment", h2),
    *bullets([
        "<b>Automated tests:</b> 103 pytest tests pass: 17 for the word lists, 32 for the game logic, 41 for the API, and "
        "13 integration tests. They check every error code, broken JSON, two games not mixing up, and that no response "
        "contains the word while the game is still going. The integration tests also play full games with the real word "
        "lists and start the app from a different folder.",
        "<b>Browser checks:</b> a script controlled Chrome in the background and ran 36 checks on a local copy of the site, "
        "and all of them passed. It tested both keyboards, the drawing, winning and losing, New Game, error messages, and "
        "phone and tablet screen sizes. The checklist for testing by hand is in <i>docs/manual_tests.md</i>.",
        "<b>Deployment:</b> the code is on GitHub, and Render runs the live site. Render installs the packages with "
        "<font face='Courier'>pip install -r requirements.txt</font> and starts the server with "
        "<font face='Courier'>gunicorn server:app --workers 1 --bind 0.0.0.0:$PORT</font>. A script I ran against the live "
        "HTTPS site passed all 12 API checks, including the error codes and the hidden-word check.",
    ]),

    Paragraph("5. How I Used Claude Code", h2),
    Paragraph(
        "I used <b>Claude Code</b> (by Anthropic, with the Opus 5.5 model) inside VS Code. First, I had it turn the course "
        "<i>TODO.md</i> into seven phases, each with tasks, tests, and a clear meaning of \"done\". After that, I asked "
        "it to build one or two phases at a time and gave it rules to follow. Claude Code wrote the code, tests, and "
        "documentation, ran the tests, and told me the results. I read each report, answered its questions about the "
        "scope, and set up the GitHub repository and the Render service myself. It only made commits when I approved "
        "them. One rule I kept repeating was: only tick a TODO item after it has been checked, and never say a manual "
        "test passed unless someone actually did it.", body),

    Paragraph("6. Challenges I Ran Into", h2),
    *bullets([
        "<b>Deciding how strict to be.</b> The specification says repeated guesses can be \"ignored or rejected.\" I "
        "decided to reject them with a 400 error, and to send 409 if someone guesses after the game is over. I listed "
        "both choices in the README so they don't surprise anyone.",
        "<b>Games disappearing.</b> The games live in the server's memory. Gunicorn can run several workers, and each "
        "one has its own memory, so a game made in one worker wouldn't exist in another. I solved this by running only "
        "one worker. I also learned that a Render restart, or the free plan going to sleep, wipes all games. So the page "
        "shows a message and lets you start a new game.",
        "<b>Problems on my own computer.</b> Port 5000 was already taken by the macOS AirPlay Receiver, so I ran the app "
        "on port 8000 instead. Halfway through building the web page, my disk filled up and everything stopped until I "
        "cleared some space. When I tested the live site with a Python script, I got an SSL certificate error even "
        "though curl worked fine. The problem was my Python install, not the site, and pointing the script to the "
        "system's certificate file fixed it.",
        "<b>Tests failing for the wrong reason.</b> One test makes sure the hidden word never appears in a response. "
        "But game IDs are random hex characters (a–f and 0–9), so a word like \"cafe\" could show up inside an ID by "
        "accident. The tests use \"python\" instead, since none of its letters can appear in an ID. Another browser "
        "check failed only because the CSS shows letters in capitals. The app was fine; the test needed fixing.",
        "<b>Understanding how the page uses the API.</b> While checking the final work, I found a TODO item saying the "
        "page uses all three endpoints. That wasn't true. The page only uses the two POST requests, because each reply "
        "already contains the full game, so it never needs GET. I unchecked the item and explained it in the README. "
        "In my demo script, I call GET myself from the Chrome DevTools console.",
    ]),

    KeepTogether([Paragraph("7. Three Prompts I Used (exact wording; [...] means I skipped some lines)", h2),
    *prompt_box(
        "Prompt 1 — Planning the smaller scope",
        "2. Revise TODO.md to match the reduced assignment scope.<br/>"
        "4. Organize the work into clear development phases.<br/>"
        "5. Include every required feature, test, and deliverable.<br/>[...]<br/>"
        "For every phase, include:<br/>- Tasks<br/>- Acceptance criteria<br/>- Tests<br/>- Required deliverables<br/>"
        "Add a final rubric-compliance checklist.<br/>Do not implement code yet.<br/>"
        "Do not mark incomplete tasks as completed.",
        "<b>What happened:</b> Claude Code wrote a seven-phase TODO.md with an API plan and a grading checklist, with "
        "every box unchecked. (The original TODO had every box ticked, even though no code existed yet.) A follow-up "
        "prompt added the submission rules, such as HTTPS, prompts in the report, and the demo video.")]),
    KeepTogether(prompt_box(
        "Prompt 2 — Game logic, word lists, and API (Phases 1–3)",
        "Implement Phases 1, 2, and 3 from TODO.md sequentially.<br/>[...]<br/>"
        "- Complete and test each phase before starting the next.<br/>- Keep the game engine independent of Flask.<br/>"
        "- Use in-memory game storage with unique IDs.<br/>- Validate inputs and return appropriate JSON errors.<br/>"
        "- Never expose hidden words during active games.<br/>- Create comprehensive pytest tests for each phase.<br/>"
        "[...]<br/>- Update TODO.md only for verified completed tasks.",
        "<b>What happened:</b> it created <i>words.py</i>, <i>game.py</i>, and <i>server.py</i> with 90 passing tests, "
        "and ran a live check of all three endpoints. It left the main-page item unchecked until the real page was built "
        "in Phase 4.")),
    KeepTogether(prompt_box(
        "Prompt 3 — Web page and testing (Phases 4–5)",
        "Implement Phases 4 and 5 from TODO.md sequentially.<br/>[...]<br/>"
        "- Draw all six Hangman stages.<br/>[...]<br/>- Support New Game without refreshing.<br/>"
        "- Use fetch() with the existing Flask API.<br/>- Keep the hidden word server-side.<br/>"
        "- Handle network and API errors.<br/>[...]<br/>- Do not claim manual browser tests passed unless performed.",
        "<b>What happened:</b> it built the web page, added integration tests, ran the background Chrome checks, and "
        "left the manual checklist blank for a person to fill in.")),

    Paragraph("8. What I Learned", h2),
    Paragraph(
        "Letting the server make every decision made hiding the word simple: one rule in one "
        "place. Writing down what \"done\" means before coding made each step easy to check. I also learned not to "
        "trust work just because it looks finished, even when an AI wrote it. The mistake above was only caught by "
        "comparing the checklist with the actual code.", body),
]

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                        title="Hangman Web — Development Report", author="Priyanshi Sitlani")
doc.build(story)
print(OUT)
