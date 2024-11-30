import cv2
import os
from yolo_predict import extract_object_from_box
from device_input import Keys
from common import *

classes = CLS()


def _match(base_img: cv2.Mat, template_img: cv2.Mat):
    """
    匹配两个图片，返回最大可信度和匹配的最大坐标
    :param base_img: 待匹配的图像
    :param template_img: 用去匹配的图像
    :return: 最大可信度 和 匹配的最大坐标（左上角）
    """
    res = cv2.matchTemplate(base_img, template_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val, max_loc


def get_minimap(frame, maps_dir: str):
    minimap = ""
    # 地图名称匹配永远截取以下范围
    title = IMGArea(Point(865, 1), 170, 20)
    base_img = partial_img(frame, title)
    for file in os.listdir(maps_dir):
        template_img = cv2.imread(os.path.join(maps_dir, file))
        val, _ = _match(base_img, template_img)
        if val > 0.8:
            minimap = file.split('.')[0]
            # print(f"Found minimap: {minimap}")
    if minimap == "CYGQ":
        return MiniMaps.CYGQ
    elif minimap == "CCZL":
        return MiniMaps.CCZL
    elif minimap == "HJQD":
        return MiniMaps.HJQD
    elif minimap == "WYZJ":
        return MiniMaps.WYZJ
    else:
        print(f"unknown minimap. you are not in WEIYANG maps.")


def match_object(frame, template_path: str, base_area: IMGArea):
    template = cv2.imread(template_path)
    base = partial_img(frame, base_area)
    val, _ = _match(base, template)
    if val > 0.8:
        return True
    return False


def get_matrix(width: int, height: int, cell_length: int = 18):
    """计算出小地图的坐标矩阵，每个方格大小为 18x18
    :param width: 小地图的宽度
    :param height: 小地图的高度
    :param cell_length: 小地图每个房间的像素宽度
    """
    rows = [i for i in range(1, height) if i % cell_length == 0]
    columns = [i for i in range(1, width) if i % cell_length == 0]

    matrix = []
    for i in range(len(rows)):
        for j in range(len(columns)):
            top_left_x = j * cell_length
            top_left_y = i * cell_length
            bottom_right_x = top_left_x + cell_length
            bottom_right_y = top_left_y + cell_length
            matrix.append((top_left_x, top_left_y, bottom_right_x, bottom_right_y))
    return matrix


def is_in_rect(current_pos, rect):
    in_x_range = current_pos[0] in range(rect[0], rect[2])
    in_y_range = current_pos[1] in range(rect[1], rect[3])
    return in_x_range and in_y_range


def get_room_index(frame, minimap: IMGArea):
    current = cv2.imread(MiniMaps.CURRENT_PATH)
    base = partial_img(frame, minimap)
    res = cv2.matchTemplate(base, current, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < 0.8:
        return
    matrix = get_matrix(minimap.width, minimap.height)
    room_index = None
    for i, pos in enumerate(matrix):
        if is_in_rect(max_loc, pos):
            room_index = i
            break
    return room_index


def _with_question_mark(frame, minimap: IMGArea):
    yet_visit = cv2.imread(MiniMaps.YET_VISIT_PATH)
    base = partial_img(frame, minimap)
    res = cv2.matchTemplate(base, yet_visit, cv2.TM_CCOEFF_NORMED)
    unexplored = len(np.where(res >= 0.8)[0])
    return unexplored


def navigate_cygq(frame, minimap: IMGArea, boxes):
    room_index = get_room_index(frame, minimap)
    hero = extract_object_from_box(boxes, classes.hero)
    down = extract_object_from_box(boxes, classes.down)
    right = extract_object_from_box(boxes, classes.right)
    up = extract_object_from_box(boxes, classes.up)
    left = extract_object_from_box(boxes, classes.left)
    boss_gate = extract_object_from_box(boxes, classes.boss_gate)
    x_range = 70
    y_range = 80
    if room_index == 1:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT
    elif room_index == 2:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT
    elif room_index == 3:
        if boss_gate:
            dist = boss_gate - hero
            if dist.x > x_range:
                return Keys.RIGHT_DOWN
            elif dist.x < -x_range:
                return Keys.LEFT_DOWN
            else:
                return Keys.DOWN
        else:
            return Keys.DOWN
    elif room_index == 4:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT
    elif room_index == 6:
        if left:
            dist = left - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.LEFT
        else:
            return Keys.LEFT
    elif room_index == 9:
        if up:
            dist = up - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.UP
        else:
            return Keys.UP
    elif room_index == 5:
        unexplored = _with_question_mark(frame, minimap)
        # 有3个房间未探索，就先向下走，没有时，有2个就向右走，有1、0个时，向上走
        if unexplored == 3:
            if down:
                dist = down - hero
                if dist.x > x_range:
                    return Keys.RIGHT_DOWN
                elif dist.x < -x_range:
                    return Keys.LEFT_DOWN
                else:
                    return Keys.DOWN
            else:
                return Keys.DOWN
        if unexplored == 2:
            if right:
                dist = right - hero
                if dist.y > y_range:
                    return Keys.DOWN
                elif dist.y < -y_range:
                    return Keys.UP
                else:
                    return Keys.RIGHT
            else:
                return Keys.RIGHT
        elif unexplored == 1 or unexplored == 0:
            if up:
                dist = up - hero
                if dist.x > x_range:
                    return Keys.RIGHT
                elif dist.x < -x_range:
                    return Keys.LEFT
                else:
                    return Keys.UP
            else:
                return Keys.UP


def navigate_hjqd(frame, minimap: IMGArea, boxes):
    room_index = get_room_index(frame, minimap)
    hero = extract_object_from_box(boxes, classes.hero)
    down = extract_object_from_box(boxes, classes.down)
    right = extract_object_from_box(boxes, classes.right)
    up = extract_object_from_box(boxes, classes.up)
    boss_gate = extract_object_from_box(boxes, classes.boss_gate)
    x_range = 70
    y_range = 80
    if room_index == 4:
        return Keys.RIGHT
    elif room_index == 5:
        unexplored = _with_question_mark(frame, minimap)
        # 有2个房间未探索，就先向下走，只有1个或没有时，向右走
        if unexplored == 2:
            if down:
                dist = down - hero
                if dist.x > x_range:
                    return Keys.RIGHT
                elif dist.x < -x_range:
                    return Keys.LEFT
                else:
                    return Keys.DOWN
            else:
                return Keys.DOWN
        elif unexplored == 1 or unexplored == 0:
            if right:
                dist = right - hero
                if dist.y > y_range:
                    return Keys.DOWN
                elif dist.y < -y_range:
                    return Keys.UP
                else:
                    return Keys.RIGHT
            else:
                return Keys.RIGHT
    elif room_index == 9:
        if up:
            dist = up - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.UP
        else:
            return Keys.RIGHT
    elif room_index == 6:
        unexplored = _with_question_mark(frame, minimap)
        # 有1个房间未探索，就先向上走，没有时，向右走
        if unexplored == 1:
            if up:
                dist = up - hero
                if dist.x > x_range:
                    return Keys.RIGHT
                elif dist.x < -x_range:
                    return Keys.LEFT
                else:
                    return Keys.UP
            else:
                return Keys.RIGHT
        elif unexplored == 0:
            if boss_gate:
                boss_gate.y += 180
                dist = boss_gate - hero
                if dist.y > y_range:
                    return Keys.DOWN
                elif dist.y < -y_range:
                    return Keys.UP
                else:
                    return Keys.RIGHT
            else:
                return Keys.RIGHT
    elif room_index == 2:
        if down:
            dist = down - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.DOWN
        else:
            return Keys.DOWN


def navigate_cczl(frame, minimap: IMGArea, boxes):
    room_index = get_room_index(frame, minimap)
    hero = extract_object_from_box(boxes, classes.hero)
    down = extract_object_from_box(boxes, classes.down)
    right = extract_object_from_box(boxes, classes.right)
    up = extract_object_from_box(boxes, classes.up)
    boss_gate = extract_object_from_box(boxes, classes.boss_gate)
    x_range = 70
    y_range = 80
    if room_index == 1:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT
    elif room_index == 2:
        if down:
            dist = down - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.DOWN
        else:
            return Keys.DOWN
    elif room_index == 4:
        return Keys.RIGHT
    elif room_index == 5:
        if up:
            dist = up - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.UP
        else:
            return Keys.RIGHT
    elif room_index == 10:
        if up:
            dist = up - hero
            if dist.x > x_range:
                return Keys.RIGHT
            elif dist.x < -x_range:
                return Keys.LEFT
            else:
                return Keys.UP
        else:
            return Keys.UP
    elif room_index == 6:
        unexplored = _with_question_mark(frame, minimap)
        # 有1个房间未探索，就先向下走，没有时，向右走
        if unexplored == 0:
            if boss_gate:
                boss_gate.y += 180
                dist = boss_gate - hero
                if dist.y > y_range:
                    return Keys.DOWN
                elif dist.y < -y_range:
                    return Keys.UP
                else:
                    return Keys.RIGHT
            else:
                return Keys.RIGHT
        elif unexplored == 1:
            if down:
                dist = down - hero
                if dist.x > x_range:
                    return Keys.RIGHT
                elif dist.x < -x_range:
                    return Keys.LEFT
                else:
                    return Keys.DOWN
            else:
                return Keys.DOWN


def navigate_wyzj(frame, minimap: IMGArea, boxes):
    room_index = get_room_index(frame, minimap)
    hero = extract_object_from_box(boxes, classes.hero)
    down = extract_object_from_box(boxes, classes.down)
    right = extract_object_from_box(boxes, classes.right)
    up = extract_object_from_box(boxes, classes.up)
    boss_gate = extract_object_from_box(boxes, classes.boss_gate)
    x_range = 70
    y_range = 70
    if room_index == 3:
        if down:
            dist = down - hero
            if dist.x > x_range:
                return Keys.RIGHT_DOWN
            elif dist.x < -x_range:
                return Keys.LEFT_DOWN
            else:
                return Keys.LEFT_DOWN
        else:
            return Keys.RIGHT_DOWN
    elif room_index == 5:
        return Keys.RIGHT
    elif room_index == 6:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT_UP
    elif room_index == 7:
        if right:
            dist = right - hero
            if dist.y > y_range:
                return Keys.DOWN
            elif dist.y < -y_range:
                return Keys.UP
            else:
                return Keys.RIGHT
        else:
            return Keys.RIGHT_UP
    elif room_index == 8:
        unexplored = _with_question_mark(frame, minimap)
        # 有1个房间未探索，就先向上走，没有时，向右走
        if unexplored == 0:
            if boss_gate:
                boss_gate.y += 150
                dist = boss_gate - hero
                if dist.y > y_range:
                    return Keys.DOWN
                elif dist.y < -y_range:
                    return Keys.UP
                else:
                    return Keys.RIGHT
            else:
                return Keys.RIGHT_DOWN
        elif unexplored == 1:
            if up:
                dist = up - hero
                if dist.x > x_range:
                    return Keys.RIGHT_DOWN
                elif dist.x < -x_range:
                    return Keys.LEFT_UP
                else:
                    return Keys.UP
            else:
                return Keys.RIGHT_UP


def navigate(frame, minimap: IMGArea, boxes):
    if minimap == MiniMaps.CYGQ:
        return navigate_cygq(frame, minimap, boxes)
    elif minimap == MiniMaps.HJQD:
        return navigate_hjqd(frame, minimap, boxes)
    elif minimap == MiniMaps.CCZL:
        return navigate_cczl(frame, minimap, boxes)
    elif minimap == MiniMaps.WYZJ:
        return navigate_wyzj(frame, minimap, boxes)


if __name__ == '__main__':
    pass
    # from yolo_predict import *
    # from device_input import *

    # _hwnd = TargetWindowHWND("地下城与勇士：创新世纪").hwnd
    # base_area = IMGArea(Point(525, 115), 305, 300)
    # win32gui.SetForegroundWindow(_hwnd)

    # img0 = CaptureImg(_hwnd).img
    # sinan = cv2.imread(r"imgs\sinan.png", cv2.IMREAD_GRAYSCALE)
    # base = partial_img(img0, base_area)
    # base = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)

    # res = cv2.matchTemplate(base, sinan, cv2.TM_CCOEFF_NORMED)
    # res = np.where(res >= 0.8)
    # print(len(res[0]))

    # cv2.imshow("img2", base)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
