import cv2
import win32gui
import win32con
import win32ui
import numpy
from common import Point
from ultralytics import YOLO

# 称号到角色腿部的偏移量
OFFSET_ON_VERTICAL = 180


class CaptureImg:

    def __init__(self, hwnd):
        self.hwnd = hwnd

    @property
    def img(self):
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
        img = numpy.frombuffer(singed_ints_array, dtype='uint8')
        img.shape = (h, w, 4)
        frame = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwnd_dc)

        return frame


class TargetWindowHWND:

    def __init__(self, window_name):
        self.hwnds = dict()
        self.window_name = window_name

    def _get_active_hwnds(self, hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            self.hwnds.update({hwnd: win32gui.GetWindowText(hwnd)})

    @property
    def hwnd(self) -> int:
        win32gui.EnumWindows(self._get_active_hwnds, None)
        for h, t in self.hwnds.items():
            if t == self.window_name:
                return h


class YOLOPredict:

    def __init__(self, best_model):
        self.best_model = best_model
        self.model = YOLO(self.best_model)
        print("Model loaded...")

    def predict(self, img, conf=0.7, half=False, show=False, verbose=False):
        results = self.model.predict(img, conf=conf, half=half, show=show, verbose=verbose)
        boxes = results[0].boxes
        cls = [int(c) for c in boxes.cls]
        xywh = [tuple(map(int, [*xywh])) for xywh in boxes.xywh]
        boxes = list(zip(cls, xywh))
        return boxes


def extract_object_from_box(boxes, cls: int) -> (Point | list[Point]):
    enemies = []
    drops = []
    for t_cls, point in boxes:
        if cls == t_cls == 0:
            # 角色坐标：称号偏移到腿部
            return Point(point[0], point[1] + OFFSET_ON_VERTICAL)
        elif cls == t_cls == 1:
            # 怪物坐标：底部中间
            enemies.append(Point(point[0], point[1] + point[3] * 0.5))
        elif cls == t_cls == 2:
            # boss坐标：底部中间
            return Point(point[0], point[1] + point[3] * 0.5)
        elif cls == t_cls == 8:
            drops.append(Point(point[0], point[1]))
        else:
            # 其他坐标：中间， 含上下左右箭头，boss房间门
            for i in (3, 4, 5, 6, 7):
                if cls == t_cls == i:
                    return Point(point[0], point[1])
    return enemies or drops


if __name__ == '__main__':
    pass
