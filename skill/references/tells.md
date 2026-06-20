# The vibe-coded tells: full catalog

Each entry has the data evidence (so you can weight it), a real quote from the threads,
the code-level signatures the scanner keys on, and the fix. Ordered by priority (comment
share in the on-topic data, which is the cleanest signal). Source: ~3.2M posts across 47
AI/SaaS subreddits and 3,033 comments from 125 "why do AI sites all look the same"
threads, 2020 to 2026.

A note on weighting. The Reddit data was collected through mid-2026 and the loudest
single tell in it is the *old* default (purple gradient, dark hero). But defaults move.
The fastest-rising tell now is the "tasteful default" the previous generation of
anti-slop advice created, so it leads this catalog even though its raw count in the
historical data is still climbing. Treat tell 0 and tell 1 as co-top-priority.

## Contents

0. The new "tasteful default" (cream + serif + sage) — the 2026 tell
1. Default shadcn / Tailwind look
2. AI purple (violet / indigo primary)
3. Gradients everywhere / gradient text
4. Too many animations
5. Rounded corners on everything
6. Dark mode + neon glow
7. Emoji as icons
8. Generic sans fonts (Inter / Geist / Instrument Serif / Fraunces)
9. The hero + three feature cards + CTA skeleton
10. Layout-quality tells (overflow, spacing, alignment)
11. Lower-signal and copy tells
12. Cleared by the data (do not chase)

---

## 0. The new "tasteful default" (cream + serif + sage)

**Why it leads:** this is the look the previous wave of anti-slop advice (including
Claude's own frontend-design skill) converged on, so it is now the single most
recognizable "AI tried to be tasteful" signal. Reddit clocks it instantly and calls it
out by name: a warm cream or beige background, a serif display font (Instrument Serif,
Fraunces, Playfair), and a sage or forest green accent, often with a generated product
"screenshot" card on the right. It reads as AI for the same reason the purple gradient
did: nobody chose it, the model did.

**Why people react so strongly:** it is dishonest slop. The purple gradient at least
looked like a default. This one looks like taste, so being told it is also a default
lands harder. Comments single out "the beige and green theme alone is a dead giveaway,"
"piss colored background copied from Anthropic branding," and "Instrument Serif is a
top-5 vibecoded title font."

**Code signatures (scanner):**
- Cream/beige page background: `#faf8f5`, `#f5f1e8`, `#f3eee3`, `#fdfbf7`, `#f7f3ec`,
  Tailwind `bg-stone-50/100`, `bg-amber-50`, `bg-orange-50` as the *page* background.
- Serif display font: `Instrument Serif`, `Fraunces`, `Playfair Display`, `Spectral`,
  `Cormorant`, `DM Serif` used for headings.
- Sage/forest green primary: `#15573a`, `#1a4d3a`, hues around emerald/green 700-900 as
  the brand color, especially paired with the cream background.
- The combination of any two of those three is the strong signal.

**Fix:** the fix is not "use a different nice palette," because that is how you got here.
Anchor the look to the actual brand or a real reference, and if there is none, pick a
direction that is specific and uncommon rather than the current tasteful average. If the
project genuinely is a warm editorial brand and cream + serif is a real decision, mark it
`unslop-ignore` and move on. The tell is reaching for it because it is what "good" auto-
completes to.

---

## 1. Default shadcn / Tailwind look

**Evidence:** named in 2.5% of on-topic comments, the single most-cited concrete cause
of the "they all look the same" reaction. Independent commenters across 6+ subreddits.

**Quote:** "Every Claude/Cursor project defaults to the same shadcn components with
identical slate gray cards, that specific blue accent, and the same padding rhythm. You
can spot it from a screenshot." (r/ClaudeAI). Also: "It is because everyone use shadcn/ui."

**Why it reads as AI:** shadcn/ui and Tailwind are excellent, but their *defaults* are
the most common output a model produces. The slate/zinc/gray neutral cards, the default
ring/border, the uniform `p-6` padding rhythm, and the stock `rounded-lg` are a
fingerprint. shadcn is not the problem; shipping it untouched is.

**Code signatures (scanner):**
- Tailwind neutrals left as the card surface everywhere: heavy repeated `bg-slate-*`,
  `bg-zinc-*`, `bg-gray-*` on `Card`/`div` with `border` + `rounded-lg` + `shadow-sm`.
- Default shadcn New York / default theme tokens unedited: `--primary`, `--ring`,
  `--radius: 0.5rem` left at generated values; `components.json` present with default
  `baseColor: "slate"` or `"zinc"` and `cssVars` untouched.
- The trio `rounded-lg border bg-card text-card-foreground shadow-sm` (the stock Card)
  repeated many times with no theming.

**Fix:** override the theme before building. Set a real `--primary` (not the default),
a deliberate `--radius`, a custom neutral ramp, and your own spacing rhythm. Point
people at theme generators (for example tweakcn) if they want a fast non-default token
set. The test: could someone tell your Card from the shadcn docs Card in a screenshot?
If not, you have not themed it.

---

## 2. AI purple (violet / indigo primary)

**Evidence:** named in 2.3% of comments, the top color tell, and it co-occurs with
"gradients" more than any other pair (32 times). Commenters trace it directly to
Tailwind's default indigo.

**Quote:** "this purple is used way too much everywhere." And: "That black/purple theme
80% of the time for me." And from Anthropic's own frontend-design guidance, quoted by a
user: avoid "cliched color schemes (particularly purple gradients on white background)."

**Why it reads as AI:** Tailwind's default-ish accent and a lot of starter templates land
on indigo/violet (#6366f1, violet-500/600). Models reach for it when no brand color is
given, so purple-as-primary is a strong "nobody chose this" signal.

**Code signatures (scanner):**
- Tailwind: `indigo-*`, `violet-*`, `purple-*`, `fuchsia-*` used as the primary/CTA/link
  color (not just an accent dot).
- Hex/HSL: `#6366f1`, `#7c3aed`, `#8b5cf6`, `#a855f7`, `#6d28d9` and neighbors as primary.
- CSS vars: `--primary`/`--brand` set to a violet/indigo hue (HSL hue ~255 to 280).

**Fix:** choose a brand color that is not in the violet/indigo/purple band, or if purple
is genuinely the brand, make it a specific, off-default purple and pair it with a
non-default neutral so it does not read as the Tailwind swatch. The point is a chosen
color, not the default one.

---

## 3. Gradients everywhere / gradient text

**Evidence:** named in 2.0% of comments. The single highest-scored design comment in the
entire dataset (373 upvotes) leads with it.

**Quote:** "the purple-to-blue gradient is the biggest tell lol. also bento grid layouts,
rounded corners on everything, hero section with gradient text that says 'transform your
X', and way too much whitespace." (r/ClaudeAI, 373 upvotes)

**Why it reads as AI:** the purple-to-blue (or purple-to-pink) gradient on the hero,
gradient-filled headings, and gradient buttons are a template default. Gradient *body
text* especially screams generated, because almost no deliberate brand does it on real
copy.

**Code signatures (scanner):**
- Gradient text: `bg-gradient-to-* ... bg-clip-text text-transparent`, or CSS
  `background: linear-gradient(...); -webkit-background-clip: text`.
- Purple-to-blue/pink gradients: `from-purple-* to-blue-*`, `from-violet-* to-indigo-*`,
  `from-indigo-* to-pink-*`; CSS `linear-gradient(...#6366f1...#3b82f6...)`.
- Gradient on many surfaces: repeated `bg-gradient-to-*` across hero, buttons, and cards.

**Fix:** default to solid fills. Allow at most one restrained gradient as an accent (and
prefer analogous, low-contrast stops over the rainbow purple-to-blue). Never put a
gradient on running headings or paragraph text. A single solid, confident brand color
beats a gradient almost every time.

---

## 4. Too many animations (fade-ins, hover-grow, parallax, scrolljacking)

**Evidence:** named in ~1.1% of comments. Flagged as a real but **minor and noisier**
signal (the keyword catches tool mentions and positive notes too), so weight it below
the color and layout tells.

**Quote:** "It's always the unnecessary hover animations and gradients that give it away
in my opinion." Also: "What triggers me is the grow animation on hover." And complaints
about scrolljacking (the page hijacking your scroll to play transitions).

**Why it reads as AI:** generated sites tend to bolt fade-in-on-scroll onto every section
and a scale-up on every card hover, because the starter components include it. The motion
is decorative, uniform, and unmotivated.

**Code signatures (scanner):**
- Framer Motion fade/scale boilerplate: `initial={{ opacity: 0, y: 20 }}` /
  `whileInView` / `whileHover={{ scale: 1.05 }}` repeated across sections.
- Tailwind/AOS: `data-aos="fade-up"` everywhere, `animate-*` on most sections,
  `hover:scale-105` on every card.
- Scrolljacking libraries wired to the whole page.

**Fix:** use motion only when it communicates state or guides attention, and make it the
exception, not the wrapper around every element. Always honor `prefers-reduced-motion`.
If every section animates the same way, none of it means anything; cut it.

---

## 5. Rounded corners and pill buttons on everything

**Evidence:** named in 0.8% of comments, and it appears in the top-scored comment's list.

**Quote:** "The blue and purple with the rounded boxes looks very vibecoded to me." And:
"Purple gradients and the urge to put a box around everything."

**Why it reads as AI:** one large radius applied uniformly (cards, inputs, buttons,
images, the whole page) plus fully-pill buttons is a default. Real design uses radius
intentionally, often a smaller scale, and varies it.

**Code signatures (scanner):**
- `rounded-2xl` / `rounded-3xl` / `rounded-full` applied broadly to cards and containers.
- Pill buttons: `rounded-full` on every button.
- CSS: a single large `border-radius` token reused everywhere; `border-radius: 9999px`
  on buttons.

**Fix:** define a small radius scale and apply it on purpose. Not everything needs to be
maximally rounded. Sharp or lightly-rounded corners often read as more deliberate. Pill
buttons are fine occasionally, not as the only button shape.

---

## 6. Dark mode with neon glow (added unprompted)

**Evidence:** named in 0.7% of comments, multi-author and multi-subreddit, several noting
the model adds the glow even when never asked.

**Quote:** "AI loves this glowing shit. for no reason. but at least there is no purple
gradients. it's something." (r/webdev)

**Why it reads as AI:** dark background plus neon `text-shadow`/`box-shadow` glow on
headings, buttons, or borders, unprompted, is a generated-template default. Dark mode
itself is fine; the unrequested glow is the tell.

**Code signatures (scanner):**
- Glow shadows: `shadow-[0_0_*]`, large colored `box-shadow` / `text-shadow` with low
  blur spread and a saturated color, `drop-shadow-[0_0_*]`.
- Neon-on-dark combos: bright `text-cyan-400`/`text-green-400`/`text-fuchsia-400` on
  `bg-black`/`bg-slate-950` with glow.

**Fix:** remove glow you did not deliberately design. If the brand is genuinely
neon/cyberpunk, keep it sparing and intentional. Default dark mode should rely on
contrast and spacing, not glow.

---

## 7. Emoji used as icons or section bullets

**Evidence:** named in 0.5% of comments. Verified as real specifically as the
"emoji-as-icons" pattern (the post-level count is inflated by emoji appearing in post
bodies generally, so weight the *icon* usage, not emoji in copy broadly).

**Quote:** "Emojis as icons. If I see them, I instantly doubt the creators ability to
even vibe-code properly. And it gives me a hint of the 'quality' of the backend." (r/ClaudeAI)

**Why it reads as AI:** 🚀 ✨ ⚡ 🔒 used as feature-card icons or section bullets is a
generated default (it needs no asset pipeline, so models reach for it). It renders
inconsistently across platforms and signals low effort.

**Code signatures (scanner):**
- Emoji inside heading/feature markup: emoji characters in `<h1>`/`<h2>`/`<h3>`, in
  feature-card titles, or as list bullets.
- The usual suspects as UI: 🚀 ✨ ⚡ 🔥 💡 🔒 ✅ 🎯 🌟 used as icons.

**Fix:** use a real icon set (Lucide, Phosphor, Heroicons rendered as SVG, or custom),
or no icon at all. Keep emoji out of headings and feature lists. Emoji in genuine body
copy where a person would actually use one is fine; emoji standing in for UI icons is not.

---

## 8. Generic sans fonts (Inter / Geist / Roboto / system default)

**Evidence:** named in 0.4% of comments by literal name, but the verifier flags this as
**understated**, because many more people just say "generic font" or "same fonts over and
over" without naming one.

**Quote:** Anthropic's own frontend-design skill, quoted by a user, says to avoid
"overused font families (Inter, Roboto, Arial, system fonts)." And: "Black background,
neon and lime green text. Inter font. 3 cards with thick border on left only" (offered as
a checklist of giveaways).

**Why it reads as AI:** Inter and Geist are the default sans for Tailwind/Next starters,
so leaving them is "nobody chose the type." Good type is one of the fastest ways to look
deliberate.

There are two default fonts now, not one. Inter/Geist is the "I didn't pick a font"
default. Instrument Serif/Fraunces is the "I tried to pick a tasteful font" default (see
tell 0). Both are autopilot. Reaching for either because it is what shows up first is the
tell, not the font itself.

**Code signatures (scanner):**
- Sans defaults: `font-family: Inter` / `Geist` / `Roboto` / `system-ui` as the only face.
- "Tasteful" serif defaults: `Instrument Serif`, `Fraunces`, `Playfair Display`,
  `Spectral`, `Cormorant`, `DM Serif Display` as the heading face.
- `next/font/google` importing one of the above with no real second face.
- Tailwind `font-sans` left at default with no custom font config.

**Fix:** choose a typeface with character for a reason, and pair it. A distinctive
display face over a clean body face breaks the default look, but only if the display
face is a real choice and not the current default-tasteful serif. The goal is a chosen
type system you can justify, not the starter font and not the starter "nice" font.

---

## 9. The centered hero + three feature cards + CTA skeleton

**Evidence:** named in 0.4% of comments and 1.6% of posts. Tied directly to shadcn
defaults by commenters.

**Quote:** "the issue usually isn't the prompt, it's that shadcn defaults give you
symmetric centered hero + 3 feature cards + cta, which is the dead giveaway. break the
grid: asymmetric hero, one oversized screenshot or loom-style video." (r/ClaudeCode)

**Why it reads as AI:** the exact page skeleton (centered hero with a big headline and two
buttons, then a 3-column grid of icon feature cards, then a centered CTA band) is the most
common generated landing page. The structure itself is the tell, before any color.

**Code signatures (scanner, heuristic):**
- A centered hero (`text-center` + big `text-5xl/6xl` headline + two buttons) immediately
  followed by `grid grid-cols-1 md:grid-cols-3` of cards with an icon + title + blurb.
- `gap-*` symmetric 3-up card grids repeated for "Features," "Benefits," "How it works."

**Fix:** break the grid. Use an asymmetric hero (content left, a real product screenshot
or short video right). Vary section layouts instead of stacking identical centered card
grids. Show the actual product over abstract icon-cards. Real screenshots beat three
icons-with-blurbs almost every time.

---

## 10. Layout-quality tells (overflow, spacing, alignment)

These are not color or font choices, so the scanner mostly cannot see them, but they are
a large part of why a generated page reads as AI. They were the most specific technical
complaints on the demo that prompted this rewrite ("text going behind the container,"
"heading needs an overflow," "inconsistent paddings, misaligned elements, no logic
behind the UI"). Check them by eye on every build.

- **Text overflow and clipping.** A heading or label that runs past or behind its
  container, or a fixed-width card that does not handle long content. Generated layouts
  often place absolutely-positioned text near a card and never test a real string. Give
  text room, let it wrap, and test with real content lengths.
- **Inconsistent spacing.** A page that mixes many unrelated padding and gap values
  (`p-3` here, `p-7` there, arbitrary `mt-[37px]`) has no spacing system, and the eye
  reads that as machine-made. Use one spacing scale and apply it consistently.
- **Misalignment.** Elements that almost line up but do not (off-by-a-few-pixels edges,
  inconsistent column gutters). Align to a grid.
- **No information hierarchy.** Every section the same weight, nothing leading the eye.
  Decide what the user should see first and make the layout say so.

Fixing color and font on an incoherent layout still leaves a site that reads as AI. The
scanner gives you a clean surface; these give you a coherent structure.

## 11. Lower-signal and copy tells

Real but minor; fix if cheap, do not over-rotate.

- **Centered everything / endless whitespace** (0.2% comments): huge vertical padding and
  everything centered. Vary alignment and tighten spacing.
- **Stock illustrations / clipart** (0.2%): undraw-style blobs and generic 3D. Use real
  screenshots or commissioned art.
- **Gradient hero copy clichés**: "Transform your X," "Supercharge," "Unleash,"
  "Effortlessly," "Your X, reimagined." These pair with the gradient-text tell. Write
  specific copy about what the thing actually does.
- **Glassmorphism** (0.2%) and **bento grids** (0.1%): low signal and contested. Allowed.

---

## 12. Cleared by the data (do not chase)

- **Mesh / blob / aurora backgrounds**: investigated and **rejected** as a keyword
  artifact (most matches were github "/blob/" URLs and metaphors). Not a real complaint.
- **Bento grids**: dead last at 0.1%, and people actively defend them. Not a tell.
- **Dark mode itself**: only the unprompted *glow* is flagged, not dark mode.
- **shadcn / Tailwind themselves**: the *defaults* are the tell, not the tools. A themed
  shadcn site is invisible to this complaint.

Flag what the data supports, at the weight it supports. Over-flagging makes the audit
noise.
