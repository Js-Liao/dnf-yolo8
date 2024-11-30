from yolo_predict import *
from actions import *
from minimap_navigator import *
from multiprocessing import Process, Queue

classes = CLS()
best_model = r'runs\detect\train2\weights\best.pt'
title = '地下城与勇士：创新世纪'
hwnd = TargetWindowHWND(title).hwnd
capture_instance = CaptureImg(hwnd)
win32gui.SetForegroundWindow(hwnd)
X_ATT_RANGE = 150
Y_ATT_RANGE = 35
X_DROP_RANGE = 30
Y_DROP_RANGE = 30
SKILL_KEYS = [Keys.A, Keys.S, Keys.D, Keys.F, Keys.G, Keys.H, Keys.X]
action_cache_a = []
action_cache_n = []


def play(yolo: YOLOPredict, queue: Queue, action_cache: list):
    frame_counter = 0
    while True:
        frame = capture_instance.img
        frame_counter += 1
        if frame_counter % 5 == 0:  # predict every 5 frames
            boxes = yolo.predict(frame, show=False)

            if classes.hero not in [x for x, _ in boxes]:
                if match_object(frame, MiniMaps.CLEAR_PATH, MiniMaps.CLEAR):
                    press_and_release_key(Keys.RSHIFT)
                    if action_cache:
                        for action in action_cache:
                            release_key(action)
                        action_cache = []
                    time.sleep(2)
                continue
            if match_object(frame, MiniMaps.SWITCH_PATH, MiniMaps.SWITCH):
                press_and_release_key(Keys.ESC)
                time.sleep(0.2)
                press_and_release_key(Keys.W)

            hero = extract_object_from_box(boxes, classes.hero)
            boss = extract_object_from_box(boxes, classes.boss)
            enemies = extract_object_from_box(boxes, classes.enemy)
            drops = extract_object_from_box(boxes, classes.drop)

            if boss:
                skill_index = get_available_skills(frame)
                action_cache = attack_enemy(SKILL_KEYS[skill_index], hero, boss, X_ATT_RANGE, Y_ATT_RANGE, action_cache)
            elif enemies:
                enemy = get_nearest_target(hero, enemies)
                skill_index = get_available_skills(frame)
                # print(f"skill_index: {skill_index}")
                action_cache = attack_enemy(SKILL_KEYS[skill_index], hero, enemy, X_ATT_RANGE, Y_ATT_RANGE,
                                            action_cache)
            elif not boss and not enemies and drops:
                drop = get_nearest_target(hero, drops)
                is_to_drop_range = is_moved_to_range(hero, drop, X_DROP_RANGE, Y_DROP_RANGE, action_cache)
                if is_to_drop_range:
                    for action in action_cache:
                        release_key(action)
                    action_cache = []
            elif not boss and not enemies and not drops:
                minimap = get_minimap(frame, MiniMaps.MAPS_DIR)
                direction = navigate(frame, minimap, boxes)
                if direction:
                    action_cache = move(direction, action_cache)

            frame_counter = 0
            queue.put((frame, boxes))


def navigator(queue: Queue):
    while True:
        if not queue.empty():
            _wrap = queue.get()
            # to do...
            pass


def main():
    print("*" * 50)
    yolo_p = YOLOPredict(best_model)
    que = Queue()
    t1 = Process(target=play, args=(yolo_p, que, action_cache_a))
    t1.start()

    navigator(que)

    t1.terminate()
    t1.join()


if __name__ == '__main__':
    main()
