"""GLFW transparent, click-through overlay process."""
from __future__ import annotations
import ctypes
import logging
import time
from multiprocessing.synchronize import Event

from src.config import AegisConfig
from src.ipc import StateRingBuffer

log = logging.getLogger(__name__)
GWL_EXSTYLE, WS_EX_NOACTIVATE, WS_EX_TOPMOST, WS_EX_TOOLWINDOW, WS_EX_TRANSPARENT = -20, 0x08000000, 0x00000008, 0x00000080, 0x00000020

def _game_rect(gui, config: AegisConfig):
    hwnd = gui.FindWindow(config.game.window_class, None) or gui.FindWindow(None, config.game.window_title)
    if hwnd and not gui.IsIconic(hwnd):
        left, top, right, bottom = gui.GetWindowRect(hwnd)
        if right - left > 300 and bottom - top > 200:
            return left, top, right - left, bottom - top
    return None

def run_overlay(config: AegisConfig, state_rb_name: str, shutdown_event: Event) -> None:
    import glfw
    import imgui
    from imgui.integrations.glfw import GlfwRenderer
    from OpenGL import GL
    try:
        import win32con, win32gui
    except ImportError as exc:
        raise RuntimeError("The overlay requires pywin32 on Windows.") from exc
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")
    window = None
    renderer = None
    try:
        for hint, value in ((glfw.VISIBLE, glfw.FALSE), (glfw.DECORATED, glfw.FALSE), (glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE), (glfw.FLOATING, glfw.TRUE), (glfw.RESIZABLE, glfw.FALSE), (glfw.FOCUS_ON_SHOW, glfw.FALSE)):
            glfw.window_hint(hint, value)
        if hasattr(glfw, "MOUSE_PASSTHROUGH"):
            glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)
        window = glfw.create_window(config.ipc.frame_width, config.ipc.frame_height, config.overlay.title, None, None)
        if not window: raise RuntimeError("Failed to create transparent GLFW window")
        glfw.set_window_pos(window, 0, 0); glfw.make_context_current(window); glfw.swap_interval(1 if config.overlay.vsync else 0)
        hwnd = glfw.get_win32_window(window)
        styles = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, styles)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED)
        imgui.create_context(); renderer = GlfwRenderer(window); glfw.show_window(window)
        state_ring = StateRingBuffer(state_rb_name, config.ipc.ring_buffer_slots, config.ipc.metadata_size, create=False)
        state, last_frame_id, last_rect = {"health_pct": 0.0}, -1, None
        while not shutdown_event.is_set() and not glfw.window_should_close(window):
            glfw.poll_events(); GL.glClearColor(0, 0, 0, 0); GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            rect = _game_rect(win32gui, config)
            if rect != last_rect and rect is not None:
                glfw.set_window_pos(window, rect[0], rect[1]); glfw.set_window_size(window, rect[2], rect[3]); last_rect = rect
            if rect is None: glfw.hide_window(window)
            else: glfw.show_window(window)
            latest = state_ring.read_latest(last_frame_id)
            if latest is not None:
                state, last_frame_id = latest, int(latest["frame_id"])
            renderer.process_inputs(); imgui.new_frame()
            if config.overlay.telemetry_hud:
                imgui.set_next_window_position(18, 18); imgui.begin("AEGIS", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_BACKGROUND)
                health_pct = float(state.get("health_pct", 0.0))
                imgui.text_colored(f"HEALTH: {health_pct * 100:.0f}%", 0.2, 1.0, 0.35)
                imgui.progress_bar(health_pct, 180, 12)
                imgui.end()
            imgui.render(); renderer.render(imgui.get_draw_data()); glfw.swap_buffers(window)
            time.sleep(0.001)
    finally:
        if 'state_ring' in locals(): state_ring.close()
        if renderer: renderer.shutdown()
        if window: glfw.destroy_window(window)
        glfw.terminate()
