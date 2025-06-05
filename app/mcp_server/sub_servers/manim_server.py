import asyncio
import subprocess
import tempfile
import os
import shutil
from fastmcp import FastMCP


manim_mcp = FastMCP(name="manim_server") 

MANIM_EXECUTABLE = os.getenv("MANIM_EXECUTABLE", "manim")  # Default to 'manim' if not set
TEMP_DIRS = {}
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
os.makedirs(BASE_DIR, exist_ok=True)

# @manim_mcp.tool()
# async def execute_manim_code(manim_code: str = "") -> str:
#     """
#     Takes Manim code as a string, renders it, and generates an animation video.
    
#     IMPORTANT: All arguments MUST be provided by keyword.
    
#     Parameters:
#         manim_code : str, default=""
#         A string containing valid Manim Python code that defines at least one Scene class.
        
#     Returns:
#         Success message with video path or error message with details.
        
#     Notes:
#         - Creates a temp directory for execution
#         - Identifies and renders the first Scene class found
#         - Stores output in 'videos' subdirectory
#     """
#     tmpdir = os.path.join(BASE_DIR, "manim_tmp")  
#     os.makedirs(tmpdir, exist_ok=True)  # Ensure the temp folder exists
#     script_path = os.path.join(tmpdir, "scene.py")
    
#     try:
#         # Write the Manim script to the temp directory
#         with open(script_path, "w") as script_file:
#             script_file.write(manim_code)
        
#         try:
#             # Try async subprocess execution first
#             process = await asyncio.create_subprocess_exec(
#                 MANIM_EXECUTABLE, script_path,
#                 stdout=asyncio.subprocess.PIPE,
#                 stderr=asyncio.subprocess.PIPE,
#                 cwd=tmpdir,
#                 env=dict(os.environ, PYTHONPATH=tmpdir)
#             )
            
#             stdout, stderr = await process.communicate()
#             returncode = process.returncode
#             stdout_text = stdout.decode() if stdout else ""
#             stderr_text = stderr.decode() if stderr else ""
            
#         except Exception as async_error:
#             # Fallback to synchronous subprocess if async fails
#             print(f"Async subprocess failed, falling back to sync: {async_error}")
#             result = subprocess.run(
#                 [MANIM_EXECUTABLE, script_path],
#                 capture_output=True,
#                 text=True,
#                 cwd=tmpdir,
#                 env=dict(os.environ, PYTHONPATH=tmpdir)
#             )
#             returncode = result.returncode
#             stdout_text = result.stdout
#             stderr_text = result.stderr

#         if returncode == 0:
#             TEMP_DIRS[tmpdir] = True
#             print(f"Check the generated video at: {tmpdir}")
#             return f"Execution successful. Video generated at: {tmpdir}"
#         else:
#             return f"Execution failed: {stderr_text}\nStdout: {stdout_text}"

#     except Exception as e:
#         return f"Error during execution: {str(e)}"

# @manim_mcp.tool()
# def cleanup_manim_temp_dir(directory: str) -> str:
#     """Clean up the specified Manim temporary directory after execution."""
#     try:
#         if os.path.exists(directory):
#             shutil.rmtree(directory)
#             if directory in TEMP_DIRS:
#                 del TEMP_DIRS[directory]
#             return f"Cleanup successful for directory: {directory}"
#         else:
#             return f"Directory not found: {directory}"
#     except Exception as e:
#         return f"Failed to clean up directory: {directory}. Error: {str(e)}"


# @manim_mcp.tool()
# def rules_before_build_manim_animation() -> str:
#     """
#     Returns the rules for using Manim animations.
#     """
#     return """
#     1. Render exactly one Scene per run.
#     2. Use PROMPT string verbatim; no extra interpretation.
#     3. If “circle” in PROMPT → draw BLUE circle; elif “square” → draw GREEN square; elif “text:” → write text after “text:”.
#     4. If none of the above → write entire PROMPT as text.
#     5. If PROMPT contains 'quoted' or "quoted", extract that substring and attach it below the shape.
#     6. All numeric values (run_time, font_size) must come from predefined constants; no literals in scene logic.
#     7. Animate with Create(...) or Write(...) using DEFAULT_RUN_TIME.
#     8. Name the scene class “PromptScene” and exit (return) immediately after drawing & labeling.
#     9. Keep code branches flat (simple if/elif/else), so adding new keywords is trivial.
#     """
    
@manim_mcp.tool()
def rules_manim_animation() -> str:
    """
        # Manim CodeAgent Rules

        ## Core Structure Requirements

        1. **Always import Manim**: Start every script with `from manim import *`

        2. **Scene Class Structure**: 
        - Create a class that inherits from `Scene`
        - Use descriptive class names (e.g., `GeometryAnimation`, `MathVisualization`)
        - Include a `construct(self)` method containing all scene logic

        3. **Scene Instantiation and Rendering**:
        - Instantiate the scene class: `scene = ClassName()`
        - Call render method: `scene.render()`
        - **IMPORTANT**: Always return the output file path after rendering

        ## Object Creation Guidelines

        4. **Basic Shapes**:
        - Use `Circle()`, `Square()`, `Rectangle()`, `Triangle()` for geometric shapes
        - Use `Dot()` for points, `Line()` for line segments
        - Use `Arrow()` for directional indicators

        5. **Mathematical Objects**:
        - Use `MathTex()` for LaTeX mathematical expressions
        - Use `Text()` for regular text
        - Use `DecimalNumber()` for numeric displays
        - Use `NumberPlane()` or `Axes()` for coordinate systems

        6. **Positioning**:
        - Use directional constants: `UP`, `DOWN`, `LEFT`, `RIGHT`, `UL`, `UR`, `DL`, `DR`
        - Use `.shift()` for relative positioning
        - Use `.move_to()` for absolute positioning
        - Use `.next_to()` for relative positioning to other objects

        ## Animation Rules

        7. **Adding Objects**:
        - Use `self.add()` to place objects without animation
        - Use `self.play(Create())` to animate object creation
        - Use `self.play(Write())` for text/math expressions

        8. **Transform Animations**:
        - Use `.animate` property for smooth transformations
        - Chain transformations: `object.animate.shift(RIGHT).scale(2)`
        - Use `Transform()` for morphing between objects
        - Use `ReplacementTransform()` for object replacement

        9. **Timing Control**:
        - Use `self.wait()` for pauses (default 1 second)
        - Use `self.wait(duration)` for specific pause lengths
        - Use `run_time` parameter in `self.play()` for animation speed

        ## Visual Styling

        10. **Colors**:
            - Use color constants: `RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, `ORANGE`
            - Use `.set_color()` method to change object colors
            - Use `.set_fill()` for fill colors with opacity

        11. **Styling Methods**:
            - Use `.scale()` for resizing
            - Use `.rotate()` for rotation (in radians)
            - Use `.set_stroke()` for border properties

        ## Content Interpretation

        12. **Prompt Analysis**:
            - Identify key mathematical concepts, shapes, or visual elements
            - Determine appropriate animation sequence (intro → main content → conclusion)
            - Choose relevant Manim objects based on content type

        13. **Mathematical Content**:
            - For equations: Use `MathTex()` with LaTeX syntax
            - For graphs: Use `Axes()` and `ParametricFunction()`
            - For geometry: Use appropriate shape classes with transformations

        14. **Educational Flow**:
            - Start with simple elements, build complexity
            - Use highlighting (color changes, scaling) to draw attention
            - Include brief pauses (`self.wait()`) for comprehension

        ## Error Prevention

        15. **Common Pitfalls**:
            - Always use `self.` prefix for scene methods
            - Don't forget to call `scene.render()` at the end
            - Use parentheses for object instantiation: `Circle()` not `Circle`
            - Remember that rotations use radians, not degrees

        16. **Import Requirements**:
            - Manim import must be first: `from manim import *`
            - No additional imports needed for basic functionality

        ## Template Structure

        ```python
        from manim import *

        class YourSceneName(Scene):
            def construct(self):
                # Create objects
                
                # Add or animate object creation
                
                # Perform animations
                
                # Add pauses for viewing
                
                # Final state or cleanup

        scene = YourSceneName()
        scene.render()
        scene_path = scene.renderer.file_writer.movie_file_path
        print(scene_path)
        ```

        ## Quality Guidelines

        19. **Animation Principles**:
            - Use smooth, purposeful movements
            - Maintain consistent timing
            - Guide viewer attention through deliberate sequencing

        17. **Scene Composition**:
            - Keep scenes focused (30-60 seconds typical)
            - Use logical animation sequences
            - Maintain visual balance and clarity

        18. **Code Quality**:
            - Use descriptive variable names
            - Group related operations
            - Comment complex mathematical expressions or logic

        ## Output Path Management

        20. **File Path Handling**:
            - After rendering, capture and return the output file path
            - Use `scene.renderer.file_writer.movie_file_path` to get the video path
            - Always return this path as the final result of the function

        21. **Path Return Pattern**:
            ```python
            scene = YourSceneName()
            scene.render()
            scene_path = scene.renderer.file_writer.movie_file_path
            print(scene_path)
            ```
    """
    return rules_manim_animation.__doc__

@manim_mcp.tool()
def return_scene_path(scene_path: str) -> str:
    """
    Returns the path of the rendered Manim scene.
    
    Parameters:
        scene_path (str): The path to the rendered video file.
        
    Returns:
        str: The path to the rendered video file.
    """
    return scene_path