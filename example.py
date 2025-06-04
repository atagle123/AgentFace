from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(Create(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))

scene = SquareToCircle()
scene.render()

#  manim -p -ql example.py SquareToCircle

# python -m frontend.gradioapp.agent_call --prompt 
# ' make me a simple square moving animation. 
# 1. Render exactly one Scene per run.
# 2. Use PROMPT string verbatim; no extra interpretation.
# 3. If “circle” in PROMPT → draw BLUE circle; elif “square” → draw GREEN square; elif “text:” → write text after “text:”.
# 4. If none of the above → write entire PROMPT as text.
# 5. If PROMPT contains 'quoted' or "quoted", extract that substring and attach it below the shape.
# 6. All numeric values (run_time, font_size) must come from predefined constants; no literals in scene logic.
# 7. Animate with Create(...) or Write(...) using DEFAULT_RUN_TIME.
# 8. Name the scene class “PromptScene” and exit (return) immediately after drawing & labeling.
# 9. Keep code branches flat (simple if/elif/else), so adding new keywords is trivial.'