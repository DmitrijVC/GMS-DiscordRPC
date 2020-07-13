import subprocess
import threading
import os
from pypresence import Presence
import time
import psutil
import win32process
import win32gui

wd = os.getcwd()


def is_running(pid):
    if psutil.pid_exists(pid):
        return True
    return False


class GMS2:
    def __init__(self, path=None):
        self.original_path = path
        if self.original_path is None:
            self.original_path = os.path.join(wd, "GameMakerStudio_original.exe")
        self._check()
        self.thread = None
        self.subthread = None
        self.process = None

    def _check(self):
        if not os.path.exists(self.original_path):
            return None  # Raise Exception

    def _run_background(self):
        self.process = subprocess.Popen(self.original_path)

    def kill(self):
        self.thread.exit()

    def run(self):
        self.thread = threading.Thread(target=self._run_background())
        self.thread.daemon = True
        self.thread.run()


class RPC:
    def __init__(self, client_id, pid):
        self.pid = pid
        self.id = client_id
        self.RPC = Presence(self.id, pipe=0)
        self.timeout = 5
        self.thread = None

    @staticmethod
    def _get_name(gms_proc):
        if gms_proc.hwnd is None:
            name = "Loading..."
            gms_proc.get_gms_hwnd()
        else:
            name = str(win32gui.GetWindowText(gms_proc.hwnd)).replace(" - GameMaker Studio 2*", "")
            name = name.replace(" - GameMaker Studio 2", "")
        if len(name) <= 2:
            name = "InvalidName"
        return name

    def _run_background(self):
        gms_proc = Process(self.pid)
        self.RPC.connect()
        epoch_time = int(time.time())
        while is_running(self.pid):

            name = self._get_name(gms_proc)

            self.RPC.update(
                pid=self.pid,
                large_image="logo",
                details=name,
                start=epoch_time
            )
            time.sleep(self.timeout)
        self.RPC.close()

    def run(self):
        self.thread = threading.Thread(target=self._run_background())
        self.thread.run()


class Process:
    def __init__(self, pid, hwnd=None):
        self.pid = pid
        self.hwnd = hwnd
        self.name = None
        self.name_place = None
        self.handle = None
        self._set_window_data()

    def _set_window_data(self):
        if self.hwnd is not None:
            self.name = win32gui.GetWindowText(self.hwnd)
            self.handle = win32gui.FindWindow(None, self.name)
        else:
            self.get_gms_hwnd()

    def get_gms_hwnd(self):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == self.pid:
                    hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        for hwnd in hwnds:
            if "- GameMaker Studio 2" in win32gui.GetWindowText(hwnd):
                self.hwnd = hwnd
                self.name = win32gui.GetWindowText(hwnd)
                break


gms = GMS2()
gms.run()

rpc = RPC('732173865500934174', gms.process.pid)
rpc.run()


print(f"Ending {gms.process.pid}")
