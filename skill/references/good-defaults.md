# Good defaults: what to reach for instead

The fix for almost every tell is "make a deliberate choice instead of the default." This
sheet makes that cheap. None of these are mandatory; they are concrete, non-AI starting
points so you are not stuck staring at a blank theme. The only hard rule is the meta one:
do not ship the untouched starter look.

## Color

The tell is violet/indigo-as-primary and purple-to-blue gradients. Pick a primary outside
that band and commit to it.

- Strong non-purple primary directions: deep teal/pine, warm clay/terracotta, oxblood/
  maroon, forest green, navy with a warm accent, mustard/ochre, slate-blue only if paired
  off-default. Anything but the stock indigo.
- Build a real neutral ramp instead of stock `slate`/`zinc`. Warm grays (slight brown) or
  cool grays you actually chose read as deliberate.
- One accent, used sparingly, beats a gradient. If you must gradient, keep stops analogous
  and low-contrast, and never on text.
- Pull a palette from a real source (a photo, a brand, a physical object) so it has a
  reason to exist.

## Type

The tell is Inter/Geist/Roboto/system as the only face. Pair two faces with intent.

- Pattern that always looks considered: a distinctive display face for headings + a clean,
  readable face for body. Even keeping a neutral body sans is fine if the headings have
  character.
- Free faces with personality (examples, not a mandate): for headings, things like
  Fraunces, Instrument Serif, Bricolage Grotesque, Space Grotesk, Clash Display, Libre
  Franklin, Schibsted Grotesk; for body, things like Source Serif, Newsreader, IBM Plex,
  Public Sans, Literata. Mix a serif and a sans for instant differentiation.
- Set a real type scale and generous line-height on body. Type does more for "not AI" than
  almost anything else.

## Radius

The tell is one big radius on everything and pill buttons everywhere.

- Define a small scale (for example 2px / 6px / 12px) and apply by role, not uniformly.
- Sharp or lightly rounded corners often look more intentional than `rounded-2xl`
  everywhere. Reserve full pills for the rare case, not every button.

## Motion

The tell is fade-in-on-scroll and hover-grow on everything, plus scrolljacking.

- Motion should communicate: state changes, focus, a deliberate reveal of one key thing.
  Not a uniform wrapper on every section.
- Always gate decorative motion behind `prefers-reduced-motion: reduce`.
- If you cannot say what a given animation tells the user, delete it.

## Layout

The tell is the centered hero + 3 feature cards + CTA skeleton.

- Asymmetric hero: copy on one side, a real product screenshot or short screen-capture on
  the other. Show the actual thing.
- Vary section structure down the page instead of stacking identical centered card grids.
  Alternate alignment, density, and media.
- Prefer real screenshots, real numbers, and real UI over three icon-with-blurb cards.
- Whitespace with intent: tighten where density helps, open up where it earns attention.
  Endless uniform padding is its own tell.

## Icons and imagery

- Real icon set rendered as SVG (Lucide, Phosphor, Heroicons) or custom, never emoji as
  icons.
- Real screenshots and photography over undraw-style blob illustrations and generic 3D.

## Copy

- Cut "Transform your X," "Supercharge," "Unleash," "Effortlessly," "reimagined." Say what
  the product literally does, with specifics and real numbers.

## The fastest single move

If you do only one thing: feed the model a real reference site you like and tell it to
match that design language, instead of asking for "a modern landing page." Unspecified is
how you get the median. A specific reference is how you get a look.
