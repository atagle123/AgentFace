import tempfile
import os
import shutil
import sys
import importlib.util
from fastmcp import FastMCP
from manim import config, Scene
from manim import *


manim_mcp = FastMCP(name="manim_server",
                    # instructions="""
                    # This is the Manim server for rendering animations.
                    # You can send Manim code to this server to execute and generate animations.
                    # Use the `execute_manim_code` tool to run your Manim scripts.
                    # After execution, you can clean up temporary directories using the `cleanup_manim_temp_dir` tool.
                    # """
                    )

# TEMP_DIRS = {}
# BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
# os.makedirs(BASE_DIR, exist_ok=True)

# @manim_mcp.tool()
# def execute_manim_code(manim_code: str) -> str:
#     """Execute the Manim code using direct rendering"""
#     tmpdir = os.path.join(BASE_DIR, "manim_tmp")
#     os.makedirs(tmpdir, exist_ok=True)
#     script_path = os.path.join(tmpdir, "scene.py")
    
#     try:
#         # Write the Manim script
#         with open(script_path, "w") as script_file:
#             script_file.write(manim_code)
        
#         # Configure Manim output directory
#         config.media_dir = tmpdir
#         config.preview = False  # Don't auto-open the video
#         config.write_to_movie = True
        
#         # Import and execute the scene dynamically
#         spec = importlib.util.spec_from_file_location("scene_module", script_path)
#         scene_module = importlib.util.module_from_spec(spec)
        
#         # Add manim imports to the module's namespace
#         scene_module.__dict__.update(globals())
#         scene_module.__dict__.update({k: v for k, v in globals().items() if not k.startswith('_')})
        
#         # Execute the module
#         spec.loader.exec_module(scene_module)
        
#         # Find Scene classes in the module
#         scene_classes = []
#         for name, obj in vars(scene_module).items():
#             if (isinstance(obj, type) and 
#                 issubclass(obj, Scene) and 
#                 obj is not Scene):
#                 scene_classes.append(obj)
        
#         if not scene_classes:
#             return "No Scene classes found in the provided code"
        
#         # Render the first scene found
#         scene_class = scene_classes[0]
#         scene_instance = scene_class()
#         scene_instance.render()
        
#         TEMP_DIRS[tmpdir] = True
#         output_path = os.path.join(tmpdir, "videos")
        
#         return f"Execution successful. Video generated at: {output_path}"
        
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


@manim_mcp.tool()
def rules_before_build_animation() -> str:
    """
    Returns the rules for using Manim animations.
    """
    return """
    1. Render exactly one Scene per run.
    2. Use PROMPT string verbatim; no extra interpretation.
    3. If “circle” in PROMPT → draw BLUE circle; elif “square” → draw GREEN square; elif “text:” → write text after “text:”.
    4. If none of the above → write entire PROMPT as text.
    5. If PROMPT contains 'quoted' or "quoted", extract that substring and attach it below the shape.
    6. All numeric values (run_time, font_size) must come from predefined constants; no literals in scene logic.
    7. Animate with Create(...) or Write(...) using DEFAULT_RUN_TIME.
    8. Name the scene class “PromptScene” and exit (return) immediately after drawing & labeling.
    9. Keep code branches flat (simple if/elif/else), so adding new keywords is trivial.
    """
    
@manim_mcp.tool()
def thing_to_know_for_build_animation() -> str:
    """Provide summary documentation on how to use Manim animations."""
    return """
    # 1. OBJETOS BÁSICOS (MOJBJECTS)
    - Circle(), Square(), Rectangle(), Dot(): formas geométricas simples.
    - Line(a, b): línea entre puntos a y b; muy útil para ejes y conexiones.
    - Polygon(*puntoses): para triángulos, polígonos regulares o irregulares.
    - Text("texto", font_size=…): texto estático; usar MathTex("…") para fórmulas TeX.
    - ImageMobject("ruta.png"): incluye imágenes externas (gráficos, logotipos).

    2. ANIMACIONES COMUNES
    - Create(objeto, run_time=…): dibuja la forma desde cero.
    - Write(texto, run_time=…): escribe texto o fórmulas caracter por caracter.
    - FadeIn(objeto, run_time=…), FadeOut(objeto): aparece/desaparece con diluido.
    - Transform(orig, dest, run_time=…): interpola de orig a dest; clave para morphing.
    - MoveToTarget(objeto, run_time=…): simplifica animar un objeto que tenga “target” definido.
    - Uncreate(objeto): invierte Create(); útil para “borrar” de forma animada.

    3. MÉTODOS DE POSICIONAMIENTO
    - .next_to(otro, direction, buff=…): posiciona relativo a “otro” con margen.
    - .to_edge(DOWN/UP/LEFT/RIGHT, buff=…): alinea con un borde de la pantalla.
    - .move_to(punto): mueve al centroide en “punto” (coordenadas).
    - .shift(vector): desplazamiento absoluto en ejes (ej. RIGHT*2 + UP).

    4. GRUPOS Y LAYERS
    - VGroup(obj1, obj2, …): agrupa varios mobjects para mover/animar juntos.
    - .bring_to_front(objeto) / .send_to_back(objeto): controla orden en el canvas.
    - .set_z_index(valor): idéntico a bring/send; valores mayores aparecen arriba.

    5. ACTUALIZADORES (UPDATERS)
    - obj.add_updater(lambda m, dt: …): modifica “m” cada frame; ej. mantener etiqueta encima.
    - obj.clear_updaters(): quita todos; esencial para detener animaciones continuas.
    - Útil para: barras de progreso, cronómetros, etiquetas que “siguen” un objeto móvil.

    6. CONTROLES DE TIEMPO
    - run_time=segundos: define duración exacta; nunca confiar en default si quieres consistencia.
    - lag_ratio (en AnimationGroup): retrasa animaciones parciales en un grupo.
    - rate_func=smooth/linear/there_and_back: curva de interpolación para suavizar o rebotar.
    - wait(tiempo): pausa fija antes de siguiente animación; evitable si usas FadeIn(..., lag_ratio).

    7. CAPAS Y FONDOS
    - BackgroundRectangle(texto, color=…): caja detrás de texto para contraste; usa .behind_mobject(texto).
    - self.camera.background_color = DARK_BLUE: cambia color de fondo de toda la escena.
    - Always: evita superposiciones accidentales con .bring_to_back o .set_opacity(valor <1).

    8. TEXTO AVANZADO
    - BulletedList("item1", "item2", dot_scale_factor=…): lista con viñetas automática.
    - NumberPlane(): crea ejes coordinados con cuadricula; sirve de base para gráficas.
    - Axes(x_range=…, y_range=…): ejes con ticks y etiquetas; luego usar.plot() para funciones.

    9. FORMAS PARAMÉTRICAS y FUNCIONES
    - ParametricFunction(lambda t: [x(t), y(t), 0], t_range=…): dibuja curvas arbitrarias.
    - FunctionGraph(lambda x: f(x), x_range=…): gráfica de función y = f(x); ideal para matemáticas.
    - always redraw una curva usando updaters si f(t) cambia en el tiempo.

    10. REUTILIZACIÓN y LIMPIEZA
    - .copy(): clona objetos sin reconstruirlos manualmente.
    - .clear(): quita todos los subobjetos; útil para limpiar grupos antes de reutilizar.
    - .remove(mobject): elimina un objeto específico de la escena sin animación.

    11. TEXTO ANIMADO y TRANSFORMACIONES
    - Write, FadeIn, FadeOut son básicos; para efectos especiales:
    · .animate.scale(factor) → animación de escalado.
    · .animate.rotate(ángulo) → rotación suave en tiempo.
    · .animate.shift(vector) → mueve con suavidad.
    - Ejemplo: self.play(text.animate.scale(1.5).shift(UP)) realiza dos transformaciones a la vez.

    12. CONSEJO FINAL
    Aislá cada funcionalidad en funciones/pequeñas clases (p. ej., un método que regrese un gráfico de barras listo para animar).
    Esto simplifica incorporar bloques reutilizables sin redundancia de código.
    """
    
@manim_mcp.tool()
def execute_manim_code(scene) -> str:
    """Executes the given Manim code."""
    scene.render()
    return "Manim code executed successfully."
