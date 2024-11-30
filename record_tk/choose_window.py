import threading
import tkinter as tk
import cv2
import os
import win32gui
import win32con
import win32ui
import numpy
import time

lock = threading.Lock()
flag = False
TEMP_VIDEO_NAME = 'temp.avi'


class MYTKWindow:

    def __init__(self, **kwargs):
        self.hwnds = dict()
        self.window = tk.Tk()
        self.geo = kwargs['geo']
        self.title = kwargs['title']
        self.var1 = tk.StringVar()
        self.var2 = tk.StringVar()
        self.var3 = tk.StringVar()
        self.var2.set("Start Record")
        self.var3.set("Stop Record")
        self.frame_windows = tk.LabelFrame(self.window)
        self.scrollbar = tk.Scrollbar(self.frame_windows)
        self.listbox = tk.Listbox(self.frame_windows, selectmode=tk.SINGLE)
        self.start_button = tk.Button(self.window, textvariable=self.var2, font=('bold', 16))
        self.stop_button = tk.Button(self.window, textvariable=self.var3, font=('bold', 16))
        self.hwnd = None

    def _on_resize(self, event):
        lb_width = self.window.winfo_width()
        lb_height = self.window.winfo_height()
        self.frame_windows.config(width=int(lb_width * 0.99), height=int(lb_height * 0.7))

    def _get_active_hwnds(self, hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            self.hwnds.update({hwnd: win32gui.GetWindowText(hwnd)})

    def _get_listbox(self):
        win32gui.EnumWindows(self._get_active_hwnds, None)
        self.listbox.delete(0, tk.END)
        for win_title in self.hwnds.values():
            if win_title:
                self.listbox.insert(tk.END, f" {win_title}")

    def _listbox_events(self, event):
        curselection = self.listbox.curselection()[0]
        self.listbox.activate(curselection)
        value = self.listbox.get(curselection).strip()
        for h, t in self.hwnds.items():
            if t == value:
                self.hwnd = h
                self.var1.set(t)
                print(f'{h} --> {t}')

    def _start_button_event(self, save_path, event):
        global flag
        lock.acquire()
        flag = True
        rec_inst = RecordWindow(self.hwnd, 30, *"XVID")
        t1 = threading.Thread(target=rec_inst.video_record, args=(save_path,))
        t1.start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='active')
        lock.release()
        print(flag)

    def _stop_button_event(self, event):
        global flag
        lock.acquire()
        flag = False
        self.stop_button.config(state='disabled')
        lock.release()
        print(flag)
        self.window.quit()

    def _close_window(self):
        self.window.quit()
        self.window.destroy()

    def app(self):
        self.window.title(self.title)
        self.window.geometry(self.geo)
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        self.window.bind('<Configure>', self._on_resize)
        self.listbox.after(200, self._get_listbox)

        self.frame_windows.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind('<Double-Button-1>', self._listbox_events)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        label_notice = tk.Label(self.window, text="你选择了窗口: ", font=('bold', 16))
        label_notice.grid(row=1, column=0, padx=5, sticky='w')
        self.var1.set("双击选择窗口")
        label = tk.Label(self.window, textvariable=self.var1, background='yellow', font=('bold', 16))
        label.grid(row=2, column=0, columnspan=2, sticky='nswe')

        self.start_button.grid(row=3, column=0, sticky='ewns', padx=5, pady=5)
        self.start_button.bind('<Button-1>', lambda event: self._start_button_event(f"video_{int(time.time())}.avi", event))
        self.stop_button.grid(row=3, column=1, sticky='ewns', padx=5, pady=5)
        self.stop_button.bind('<Button-1>', self._stop_button_event)

        self.window.mainloop()


class RecordWindow:

    def __init__(self, hwnd, fps, *args):
        self.hwnd = hwnd
        self.fps = fps
        self.fcc = cv2.VideoWriter.fourcc(*args)

    @property
    def shot_frame(self):
        [l, t, r, b] = win32gui.GetWindowRect(self.hwnd)
        w = r - l
        h = b - t
        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)
        save_dc.BitBlt((0, 0), (w, h), mfc_dc, (0, 0), win32con.SRCCOPY)
        singed_ints_array = bitmap.GetBitmapBits(True)
        frame = numpy.frombuffer(singed_ints_array, dtype='uint8')
        frame.shape = (h, w, 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwnd_dc)

        return frame

    def video_record(self, save_path):
        size = (int(self.shot_frame.shape[1]), int(self.shot_frame.shape[0]))
        temp_video_writer = cv2.VideoWriter(TEMP_VIDEO_NAME, self.fcc, self.fps, size)
        count = 0
        start_time = int(time.time())
        global flag
        while flag:
            temp_video_writer.write(self.shot_frame)
            count += 1
        end_time = int(time.time())
        temp_video_writer.release()

        # 重新计算正确的帧率
        print(start_time, end_time, count)
        real_fps = count / (end_time - start_time)
        real_video_writer = cv2.VideoWriter(save_path, self.fcc, real_fps, size)
        real_video = cv2.VideoCapture(TEMP_VIDEO_NAME)
        success, frame = real_video.read()
        while success:
            success, frame = real_video.read()
            real_video_writer.write(frame)
        real_video.release()
        real_video_writer.release()
        cv2.destroyAllWindows()
        os.remove(TEMP_VIDEO_NAME)


if __name__ == '__main__':
    geo = "600x400+200+300"
    mtk = MYTKWindow(geo=geo, title="Please Select A Window")
    mtk.app()
