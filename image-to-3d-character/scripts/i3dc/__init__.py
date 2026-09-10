"""image-to-3d-character skill automation core.

Offline-testable engine used by the OpenCode skill to orchestrate a
2D-image -> animation-ready 3D character pipeline on the user's machine.

Everything in this package runs on plain CPython (Pillow/numpy optional) so it
can be tested on any machine, including a CPU-only box with no Blender and no
GPU. Heavy steps (Blender, image-to-3D inference, Stable Diffusion) are executed
as subprocesses only when the matching tool is actually detected; otherwise the
pipeline reports exactly what is missing and what to install. It never fakes a
successful mesh.
"""

__version__ = "1.0.0"
