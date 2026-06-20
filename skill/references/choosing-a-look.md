# Choosing a look (a method, not a palette)

This file used to be a list of recommended colors and fonts. That was a mistake. Any
specific recommendation, repeated, becomes the next default and the next tell. The first
version of this skill recommended cream backgrounds, a forest-green accent, and Fraunces,
which is exactly the look people now recognize as AI-tasteful on sight. So this file
gives you a way to decide, not a thing to copy.

The goal is one outcome: a design where every major choice has a reason that is specific
to this project. That is the single property a default can never have, and it is what
makes a site stop reading as machine-made.

## Start from a reference, always

The highest-leverage input is a real reference. Ask the user for one site, brand, or
screenshot whose feel they want. Anchor color, type, and density to it. If they cannot
name one, that is the conversation to have before writing CSS, because without it you are
choosing the median for them. A reference is how a human injects taste into a model that
otherwise averages.

If there is genuinely no reference and you must choose, pick a *named direction* and
commit to it, rather than "modern and clean." For example: dense and utilitarian (think
trading terminal), editorial and text-forward (think a magazine), warm and consumer
(think a friendly app), stark and technical (think developer tooling), expressive and
brand-loud. Naming the direction forces specificity and steers away from the center.

## Color

Decide a primary from the project, not the framework. A real brand color is best. If you
are choosing, sample from something concrete (a product photo, a logo, a physical object,
a place) so the palette has a source. Build a neutral ramp you actually picked rather than
stock slate or stock cream. The test is not "is this color nice," it is "can I say why
this project uses it." Avoid the current defaults on both ends: framework indigo/violet,
and tasteful cream/sage. Either is fine as a *stated decision*, neither is fine as a
fallback.

## Type

Pick type for a reason and pair it. The reason can be tone (a geometric sans for
precision, a humanist serif for warmth), but it has to be a reason. Pairing a display
face with a separate body face almost always reads as more considered than one face
everywhere. Steer away from the autopilot picks on both sides: Inter and Geist (the "no
choice" defaults) and Instrument Serif, Fraunces, Playfair (the "tasteful choice"
defaults). They are not banned, they are overexposed, so use them only as a real
decision, ideally not for the headline that sets the whole tone.

## Layout

Structure follows the goal, not a template. Decide what the page is for and what the user
should do first, and let that determine the sections. This is how you avoid the centered
hero plus three identical feature cards: that skeleton appears when structure is chosen by
default instead of by purpose. Show the real product (a true screenshot, real data, real
numbers) over abstract icon cards. Vary section shape and density down the page.

## Motion, radius, detail

Make these decisions consciously and sparingly. Motion should communicate something and
respect `prefers-reduced-motion`. Radius should be a small intentional scale, not one
value on everything. Glow, gradients, and effects are decisions to justify, not defaults
to accept.

## The one-line version

If you do only one thing, get a real reference from the user and match it. Everything
else in this file is what to do when you cannot. The skill removes the tells; this method
is how you replace them with something chosen rather than something defaulted.
