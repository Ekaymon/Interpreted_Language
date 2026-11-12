#boba's graphics library

import threading
import win32gui
import win32con
import win32api

#fields[4] when spawnwindow is used is the window id
_windows = {}        # name -> _Window
_by_hwnd = {}        # hwnd -> _Window 
gui_variables = {}


class _Window:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.lock = threading.Lock()   # theres 2 threads that access this

        _, _, self.w, self.h = win32gui.GetClientRect(hwnd)

        screen_dc = win32gui.GetDC(hwnd)
        self.mem_dc = win32gui.CreateCompatibleDC(screen_dc)
        self.bitmap = win32gui.CreateCompatibleBitmap(screen_dc, self.w, self.h)
        self.old_bitmap = win32gui.SelectObject(self.mem_dc, self.bitmap)
        win32gui.ReleaseDC(hwnd, screen_dc)

        # white background to match COLOR_WINDOW
        win32gui.PatBlt(self.mem_dc, 0, 0, self.w, self.h, win32con.WHITENESS)

    def destroy(self):
        win32gui.SelectObject(self.mem_dc, self.old_bitmap)
        win32gui.DeleteObject(self.bitmap)
        win32gui.DeleteDC(self.mem_dc)


def gui_library(fields: list, variables: dict):
    """takes the fields token

    Args:
        fields list[str]: The parsed line
    """
    global gui_variables
    gui_variables = variables
    if fields[1] == "spawnwindow":
        spawn_window(fields)
    elif fields[1] == "changepixle":
        change_pixel(fields)


# window process handling function
def __wnd_proc(hwnd, msg, wparam, lparam) -> int:
    if msg == win32con.WM_PAINT: # if the window msg is to paint this sets the window to allow painting
        hdc, ps = win32gui.BeginPaint(hwnd) # it says this takes no args but crashes without a hwnd 
        win = _by_hwnd.get(hwnd) 
        if win: # makes sure the window is real
            with win.lock: # makes sure that the thread being used is the only thread modifying the window
                win32gui.BitBlt(hdc, 0, 0, win.w, win.h, win.mem_dc, 0, 0, win32con.SRCCOPY)  # window flag slop,   copied from the docs, no clue how this works
        win32gui.EndPaint(hwnd, ps) # exits paint mode
        return 0

    if msg == win32con.WM_DESTROY: # if the window msg is to destroy the window will close
        win = _by_hwnd.pop(hwnd, None) # remove the window from the windows list
        if win:
            win.destroy()
            _windows.pop(win.name, None)
        win32gui.PostQuitMessage(0)
        return 0

    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def _window_thread(fields, ready: threading.Event) -> None:
    #Creates the window and runs its message loop. cannot be done on sepreate threads according to the pywin32 docs
    try:
        hInstance = win32api.GetModuleHandle(None)
        className = fields[4]
        # type: ingnore is beacuse it would fill up the error count beacuse of type it being type unshure
        wndclass = win32gui.WNDCLASS()
        wndclass.hInstance = hInstance   # type: ignore
        wndclass.lpszClassName = className  # type: ignore
        wndclass.lpfnWndProc = __wnd_proc  # type: ignore
        wndclass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)   # type: ignore
        wndclass.hbrBackground = win32con.COLOR_WINDOW + 1   # type: ignore
        wndclass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW   # type: ignore

        atom = win32gui.RegisterClass(wndclass)

        # this stops the window from tweaking tf out. it does remove being able to resize the window after its creation
        style = win32con.WS_OVERLAPPED | win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.WS_MINIMIZEBOX

        hwnd = win32gui.CreateWindow(
            atom, className, style,
            0, 0, int(fields[2]), int(fields[3]),  #fields[2] is the width,   fields[3] is the height
            0, 0, hInstance, None
        )

        win = _Window(hwnd)  #window object init
        win.name = className # sets the window name to the name provided by fields[4]
        _windows[className] = win # adds the window name to the window dict
        _by_hwnd[hwnd] = win # adds the hwnd to the wnd dict

        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL) # renders the window
        win32gui.UpdateWindow(hwnd) # updates the window
    finally:
        ready.set()   # always release the caller, even if creation failed

    # Message loop
    while True:
        ret, msg = win32gui.GetMessage(None, 0, 0)
        if ret == 0:    # window manager quit
            break
        if ret == -1:
            raise RuntimeError("win32gui.GetMessage returned -1") # there was a fuck up
        win32gui.TranslateMessage(msg)
        win32gui.DispatchMessage(msg)


def spawn_window(fields) -> None:
    #[g:spawnwindow:width:height:name]
    print("[spawning window...]")
    ready = threading.Event()
    threading.Thread(target=_window_thread, args=(fields, ready)).start()
    ready.wait()   # don't return until the window exists, so change_pixel can find it
    print("[window spawned...]")


def change_pixel(fields) -> None:
    #[g:changepixle:name:x:y:r:g:b]
    win = _windows.get(fields[2])
    if win is None:
        raise RuntimeError(f"no window named {fields[2]!r}") # failed to find a window with the correct name
    
    x, y = int(gui_variables[fields[3]]), int(gui_variables[fields[4]]) # the pixel to change
    r, g, b = int(fields[5]), int(fields[6]), int(fields[7]) # the colour to change said pixel to
    
    if not (0 <= x < win.w and 0 <= y < win.h):
        return   # out of bounds, ignore

    with win.lock: # makes sure that another thread is not touching the window
        win32gui.SetPixel(win.mem_dc, x, y, win32api.RGB(r, g, b)) # sets the pixel color

    # nicely ask Windows to repaint just that pixel 
    win32gui.InvalidateRect(win.hwnd, (x, y, x + 1, y + 1), False)



if __name__ == "__main__":
    #g:spawnwindow:300:300:test
    gui_library(["g", "spawnwindow", 300, 300, "test"])
    #g:changepixle:test:50:50:255:0:0
    #                    x y  r   g b
    gui_library(["g", "changepixle", "test", 50, 50, 255, 0, 0])