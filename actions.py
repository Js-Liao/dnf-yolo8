from common import Point
from device_input import *


def get_nearest_target(hero: Point, targets: list[Point]) -> Point:
    if not any(targets) or not hero:
        return Point()
    # 计算出离hero最近目标坐标的位置, 直线距离
    target = targets[0]
    for pos in targets:
        distance = pos.distance_to(hero)
        if distance < target.distance_to(hero):
            target = pos
    return target


def is_moved_to_range(current: Point, target: Point, x_range: int, y_range: int, action_cache=None):
    distance = target - current
    # x轴范围内
    is_in_x_range = abs(distance.x) <= x_range
    # y轴范围内
    is_in_y_range = abs(distance.y) <= y_range

    print(f"distance.x: {distance.x}, distance.y: {distance.y}")

    # 已经在范围内，不再移动，释放移动按键
    if is_in_x_range and is_in_y_range:
        if action_cache:
            for key in action_cache:
                release_key(key)
            action_cache.clear()
        return True

    # 判断目标在右上，右下，左上，左下
    # 右上
    if distance.x > x_range and distance.y < -y_range:
        action_cache = move(Keys.RIGHT_UP, action_cache)
    # 右下
    elif distance.x > x_range and distance.y > y_range:
        action_cache = move(Keys.RIGHT_DOWN, action_cache)
    # 左上
    elif distance.x < -x_range and distance.y < -y_range:
        action_cache = move(Keys.LEFT_UP, action_cache)
    # 左下
    elif distance.x < -x_range and distance.y > y_range:
        action_cache = move(Keys.LEFT_DOWN, action_cache)

    # 目标在x轴范围内，不在y轴范围内
    if is_in_x_range and not is_in_y_range:
        if distance.y < 0:
            action_cache = move(Keys.UP, action_cache)
        else:
            action_cache = move(Keys.DOWN, action_cache)
    # 目标在y轴范围内，不在x轴范围内
    elif not is_in_x_range and is_in_y_range:
        if distance.x < 0:
            action_cache = move(Keys.LEFT, action_cache)
        else:
            action_cache = move(Keys.RIGHT, action_cache)

    return False


def attack_enemy(key: int, hero: Point, enemy: Point, x_range: int, y_range: int, action_cache=None):
    no_need_to_move = is_moved_to_range(hero, enemy, x_range, y_range, action_cache)
    if no_need_to_move:
        if enemy.x < hero.x:
            press_and_release_key(Keys.LEFT)
            press_and_release_key(key)
        elif enemy.x > hero.x:
            press_and_release_key(Keys.RIGHT)
            press_and_release_key(key)
    return action_cache


def _to_left_or_right(direction: int, action_cache=None, interval=0.05):
    if action_cache:  # cache中有动作
        # 缓存动作中有只有左或右移时，不做任何操作
        if len(action_cache) == 1 and action_cache[0] == direction:
            pass
        else:
            # 缓存动作中不是只有左或只有右移时，清空缓存动作，然后右移
            # if all([False if key == direction else True for key in action_cache]):
            for key in action_cache:
                release_key(key)
            action_cache.clear()
            press_and_release_key(direction, interval=interval)
            time.sleep(interval)
            press_key(direction)
            action_cache.append(direction)
    else:  # cache中没有动作, 表示第一次右移
        press_and_release_key(direction, interval=interval)
        time.sleep(interval)
        press_key(direction)
        action_cache.append(direction)
    return action_cache


def _to_up_or_down(direction: int, action_cache=None, interval=0.05):
    if action_cache:  # cache中有动作
        # 缓存动作中有只有上或下移时，不做任何操作
        if len(action_cache) == 1 and action_cache[0] == direction:
            pass
        else:
            # 缓存动作中不是只有上移时，清空缓存动作，然后上移
            # if all([False if key == Keys.UP else True for key in action_cache]):
            for key in action_cache:
                release_key(key)
            action_cache.clear()
            press_key(direction)
            action_cache.append(direction)
    else:  # cache中没有动作, 表示第一次上移
        press_key(direction)
        action_cache.append(direction)
    return action_cache


def _to_left_or_right_up_or_down(directions: list[int], action_cache=None, interval=0.05):
    direction1, direction2 = directions
    if action_cache:  # cache中有动作
        # 缓存动作中不是左/右上/下时，清空缓存动作，然后右上移
        if action_cache != directions:
            for key in action_cache:
                release_key(key)
            action_cache.clear()
            press_and_release_key(direction1, interval=interval)
            time.sleep(interval)
            press_key(direction1)
            time.sleep(0.1)
            press_key(direction2)
            action_cache.append(direction1)
            action_cache.append(direction2)
    else:  # cache中没有动作, 表示第一次移动
        press_and_release_key(direction1, interval=interval)
        time.sleep(interval)
        press_key(direction1)
        time.sleep(0.1)
        press_key(direction2)
        action_cache.append(direction1)
        action_cache.append(direction2)
    return action_cache


def move(direction: Keys, action_cache=None, interval=0.05):
    if action_cache is None:
        action_cache = []
    if direction == Keys.RIGHT:  # 右移
        print("move right...")
        action_cache = _to_left_or_right(Keys.RIGHT, action_cache, interval)
        return action_cache

    elif direction == Keys.LEFT:  # 左移
        print("move left...")
        action_cache = _to_left_or_right(Keys.LEFT, action_cache, interval)
        return action_cache

    elif direction == Keys.UP:  # 上移
        print("move up...")
        action_cache = _to_up_or_down(Keys.UP, action_cache, interval)
        return action_cache

    elif direction == Keys.DOWN:  # 下移
        print("move down...")
        action_cache = _to_up_or_down(Keys.DOWN, action_cache, interval)
        return action_cache

    elif direction == Keys.RIGHT_UP:  # 右上移
        print("move right up...")
        action_cache = _to_left_or_right_up_or_down(Keys.RIGHT_UP, action_cache, interval)
        return action_cache

    elif direction == Keys.RIGHT_DOWN:  # 右下移
        print("move right down...")
        action_cache = _to_left_or_right_up_or_down(Keys.RIGHT_DOWN, action_cache, interval)
        return action_cache

    elif direction == Keys.LEFT_UP:  # 左上移
        print("move left up...")
        action_cache = _to_left_or_right_up_or_down(Keys.LEFT_UP, action_cache, interval)
        return action_cache

    elif direction == Keys.LEFT_DOWN:  # 左下移
        print("move left down...")
        action_cache = _to_left_or_right_up_or_down(Keys.LEFT_DOWN, action_cache, interval)
        return action_cache


if __name__ == "__main__":
    _action_cache = []
    while True:
        st1 = time.time()
        while time.time() - st1 < 1:
            _action_cache = move(Keys.LEFT, _action_cache, interval=0.05)
        st2 = time.time()
        while time.time() - st2 < 1:
            _action_cache = move(Keys.RIGHT, _action_cache, interval=0.05)

        for _key in _action_cache:
            release_key(_key)
