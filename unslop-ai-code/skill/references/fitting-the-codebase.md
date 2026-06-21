# Fitting the codebase (a method, not a style guide)

This file does not give you a coding style to copy. The point of the data is that AI code
reads as AI precisely because it reaches for the most common pattern in its training set
instead of the one your project actually uses. Any fixed style, applied by default, is just a
different average. So this is a way to make code deliberate and project-specific, which is the
one property that stops it reading as machine-generated.

The single most repeated fix in the whole dataset was the same every time: make the model
follow the existing code instead of letting it guess the average. Everything below is how.

## Start from the codebase, always

The highest-leverage input is the repo itself. Before generating, give the model the files it
will sit next to: the module it is extending, the nearest sibling that already does something
similar, the project's conventions (how errors are handled, how things are logged, how modules
are structured, the naming vocabulary). A change that follows the existing patterns is small
and invisible. A change that ignores them is the 2000-line PR that should have been 50. If you
generate against a blank slate, you get the tutorial.

If there is genuinely no precedent in the repo (a brand new project), make one deliberate
decision and write it down (a short conventions note the model can read), rather than letting
each file invent its own approach. The tell is not any one pattern; it is the absence of a
chosen one.

## The requirement, not the demo

State what the code actually has to do, including the cases that matter, before generating.
Boilerplate / tutorial-shaped code is the loudest tell because the model defaults to the
sample-app shape (one page, dummy data, no real backend) when the requirement is vague. Name
the real inputs, the real failure modes, the real integration. If you cannot state the
requirement precisely, you will get the demo.

## Verify what a regex cannot

The tells that bite are the ones no scanner can see. Two questions catch most of them:

- Does it call anything that does not exist? Run it. Check every import and method against the
  real docs, not the model's confidence. Hallucinated APIs compile-and-fail or read-right-and-
  run-wrong, and only a compiler, a type checker, or a test will catch them.
- Does it match how this repo already does things? Read the diff against the neighboring code.
  A new logging approach, a new error pattern, a new structure mid-file is the style-mismatch
  tell.

If you cannot explain a line the model wrote, do not ship it. The mixed-skill tell is exactly
advanced code next to beginner mistakes that the author cannot account for.

## The surface tells are the cheap part

The scanner handles the mechanical layer: emoji, leftover chat artifacts, placeholder
comments, swallowed errors, narrating comments, generic placeholder names. Strip those, but do
not mistake stripping them for the job. A file with no emoji and a clean lint that is still
tutorial-shaped, calls a made-up API, and ignores the repo is still AI slop. The surface is
quick to fix and the shape is what actually matters.

## The escape hatch

A pattern chosen on purpose is not a tell. A project may genuinely want broad exception
handling at a boundary, an emoji in a CLI banner, a `process_data` step in a one-off script.
The skill flags *unchosen defaults*, not banned constructs. When a flagged line is a real
decision, keep it and mark it `unslop-ignore` so the audit stays honest.

## The one-line version

If you do only one thing, feed the model the surrounding code and tell it to match it, then
run the result and check every call is real. Everything else here is detail. The scanner
removes the surface tells; this method removes the ones that ship bugs.
