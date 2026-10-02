import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spoon Egg Farm")

GREEN = (60, 140, 60)
DARK_BG = (30, 30, 45)
RED_CHICK = (200, 30, 30)
EGG_COLOR = (245, 240, 220)
BROWN_BTN = (110, 70, 40)
SHOVEL_COLOR = (139, 90, 43)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TROUGH_FOOD_COLOR = (160, 100, 40)
TROUGH_WATER_COLOR = (60, 140, 200)

FARM_W = 650
SHOP_X1, SHOP_X2 = FARM_W, WIDTH
MARKET_Y1, MARKET_Y2 = HEIGHT - 120, HEIGHT

# ========== 【关键：滚动容器范围】 ==========
# 上方状态文字结束位置（滚动区域的顶部）
SCROLL_CONTAINER_TOP = 330
# Egg Market开始位置（滚动区域的底部，不能超过这里）
SCROLL_CONTAINER_BOTTOM = MARKET_Y1
SCROLL_CONTAINER_HEIGHT = SCROLL_CONTAINER_BOTTOM - SCROLL_CONTAINER_TOP
scroll_offset = 0
MAX_SCROLL = 0

# 食槽（左）、水槽（右）位置
FEED_TROUGH_X = 80
FEED_TROUGH_Y = 320
WATER_TROUGH_X = FARM_W - 80
WATER_TROUGH_Y = 320
TROUGH_SIZE = 40

# 全局资源
dirt = 0.0
gold = 0.0
chicken_count = 0
shovel_count = 0
has_shovel_equipped = True
next_shovel_cost = 30.0
next_chicken_cost = 40.0
shovel_power_level = 1
base_dirt_per_click = 1.0
multi_drag_level = 1  # 多蛋拖拽等级，初始一次拖1个
multi_drag_cost_base = 25

# 食槽&水槽存量
feed_trough = {"stock": 100, "max": 100, "refill_cost": 15}
water_trough = {"stock": 100, "max": 100, "refill_cost": 12}


class Shovel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.handle_len = 30
        self.hit_radius = 22

    def contains_point(self, mx, my):
        return (mx - self.x) ** 2 + (my - self.y) ** 2 < self.hit_radius ** 2

    def move_random(self):
        self.x = random.randint(60, FARM_W - 60)
        self.y = random.randint(160, MARKET_Y1 - 60)

    def draw(self, scr):
        pygame.draw.line(scr, SHOVEL_COLOR, (self.x, self.y), (self.x, self.y - self.handle_len), 5)
        pygame.draw.polygon(scr, SHOVEL_COLOR, [
            (self.x - 12, self.y),
            (self.x + 12, self.y),
            (self.x + 6, self.y + 14),
            (self.x - 6, self.y + 14)
        ])


class Chicken:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 22
        self.base_timer = random.randint(6000, 10000)
        self.timer = self.base_timer
        self.last_spawn = pygame.time.get_ticks()
        self.egg_ready = False
        self.speed_level = 1
        self.amount_level = 1
        self.move_speed = 0.8

        # 饥渴属性
        self.hunger = 100.0    # 饥饿 0~100
        self.thirst = 100.0    # 口渴 0~100
        self.hunger_decay = 0.012
        self.thirst_decay = 0.015
        self.target = "shovel" # 目标：shovel / feed / water

    def update(self, now):
        interval = max(1200, int(self.timer - (self.speed_level - 1) * 700))
        if not self.egg_ready and now - self.last_spawn > interval:
            self.egg_ready = True
            return True
        return False

    def get_color(self):
        return RED_CHICK

    def upgrade_speed(self):
        self.speed_level += 1

    def upgrade_amount(self):
        self.amount_level += 1

    # 饥渴持续下降
    def decay_hunger_thirst(self):
        self.hunger -= self.hunger_decay
        self.thirst -= self.thirst_decay
        self.hunger = max(0, self.hunger)
        self.thirst = max(0, self.thirst)

        # 自动切换目标
        if self.hunger < 25 and feed_trough["stock"] > 0:
            self.target = "feed"
        elif self.thirst < 25 and water_trough["stock"] > 0:
            self.target = "water"
        else:
            self.target = "shovel"

    # 寻找离鸡最近的铲子
    def get_nearest_shovel(self, shovel_list):
        if len(shovel_list) == 0:
            return None
        nearest = None
        min_dist = float("inf")
        for s in shovel_list:
            dist = math.hypot(s.x - self.x, s.y - self.y)
            if dist < min_dist:
                min_dist = dist
                nearest = s
        return nearest

    # 移动到目标点
    def move_to_target(self, shovel_list):
        tx, ty = 0,0
        target_shovel = self.get_nearest_shovel(shovel_list)

        if self.target == "feed":
            tx, ty = FEED_TROUGH_X, FEED_TROUGH_Y
        elif self.target == "water":
            tx, ty = WATER_TROUGH_X, WATER_TROUGH_Y
        elif self.target == "shovel" and target_shovel is not None:
            tx, ty = target_shovel.x, target_shovel.y
        else:
            return target_shovel

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 3:
            self.x += (dx / dist) * self.move_speed
            self.y += (dy / dist) * self.move_speed

        # 边界限制草地内
        self.x = max(self.radius, min(FARM_W - self.radius, self.x))
        self.y = max(120 + self.radius, min(MARKET_Y1 - self.radius, self.y))

        # 到达食槽，吃东西
        if self.target == "feed" and dist < TROUGH_SIZE:
            if feed_trough["stock"] > 0:
                eat_amt = 0.3
                feed_trough["stock"] -= eat_amt
                self.hunger = min(100, self.hunger + 0.8)
        # 到达水槽，喝水
        if self.target == "water" and dist < TROUGH_SIZE:
            if water_trough["stock"] > 0:
                drink_amt = 0.3
                water_trough["stock"] -= drink_amt
                self.thirst = min(100, self.thirst + 0.9)
        return target_shovel

    def check_collision_with_shovel(self, shovel):
        if shovel is None:
            return False
        dist = math.hypot(self.x - shovel.x, self.y - shovel.y)
        return dist < self.radius + shovel.hit_radius


class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 14
        self.vy = 3.2
        self.dragging = False
        self.is_sold = False

    def update(self):
        if self.y < MARKET_Y1 - self.radius:
            self.y += self.vy


chickens = []
eggs = []
shovels = []
dragging_eggs = []  # 存储当前拖拽的多个鸡蛋

try:
    font = pygame.font.SysFont("arial", 24)
    font_small = pygame.font.SysFont("arial", 20)
except:
    font = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 20)

clock = pygame.time.Clock()
running = True

while running:
    now = pygame.time.get_ticks()
    screen.fill(DARK_BG)

    # 草地和区域
    pygame.draw.rect(screen, GREEN, (0, 120, FARM_W, HEIGHT - 120))
    pygame.draw.rect(screen, (50, 50, 70), (0, MARKET_Y1, FARM_W, HEIGHT - MARKET_Y1))
    pygame.draw.rect(screen, (70, 100, 140), (SHOP_X1, MARKET_Y1, SHOP_X2 - SHOP_X1, HEIGHT - MARKET_Y1))
    market_text = font.render("Egg Market (Drag egg here to sell)", True, WHITE)
    screen.blit(market_text, (SHOP_X1 + 10, MARKET_Y1 + 10))

    # ====== 只有买了小鸡之后，才绘制食槽水槽 ======
    if chicken_count > 0:
        # 食槽
        pygame.draw.rect(screen, TROUGH_FOOD_COLOR, (FEED_TROUGH_X-TROUGH_SIZE//2, FEED_TROUGH_Y-TROUGH_SIZE//2, TROUGH_SIZE, TROUGH_SIZE))
        feed_text = font_small.render(f"Feed:{feed_trough['stock']:.0f}", True, WHITE)
        screen.blit(feed_text, (FEED_TROUGH_X - 30, FEED_TROUGH_Y + 30))
        # 水槽
        pygame.draw.rect(screen, TROUGH_WATER_COLOR, (WATER_TROUGH_X-TROUGH_SIZE//2, WATER_TROUGH_Y-TROUGH_SIZE//2, TROUGH_SIZE, TROUGH_SIZE))
        water_text = font_small.render(f"Water:{water_trough['stock']:.0f}", True, WHITE)
        screen.blit(water_text, (WATER_TROUGH_X - 30, WATER_TROUGH_Y + 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鼠标滚轮：只在【按钮滚动容器】内生效
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if SHOP_X1 < mx < WIDTH and SCROLL_CONTAINER_TOP < my < SCROLL_CONTAINER_BOTTOM:
                scroll_offset += event.y * 30
                scroll_offset = max(-MAX_SCROLL, min(0, scroll_offset))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            dragging_eggs.clear()
            # 多蛋拾取：最多拾取 multi_drag_level 个鸡蛋
            for e in eggs:
                if not e.is_sold and len(dragging_eggs) < multi_drag_level:
                    if (mx - e.x) ** 2 + (my - e.y) ** 2 < e.radius ** 2:
                        e.dragging = True
                        dragging_eggs.append(e)

            if len(dragging_eggs) == 0:
                # 点击铲子挖土
                for s in shovels:
                    if s.contains_point(mx, my) and has_shovel_equipped:
                        dirt += base_dirt_per_click * shovel_power_level
                        s.move_random()
                        break

            # ========== 按钮点击检测：坐标要加上滚动偏移 ==========
            btn_y = SCROLL_CONTAINER_TOP + scroll_offset
            # 【购买铲子】开局永远显示
            btn_shovel_x1, btn_shovel_y1 = SHOP_X1 + 20, btn_y
            btn_shovel_x2, btn_shovel_y2 = SHOP_X2 - 20, btn_y + 40
            if btn_shovel_x1 < mx < btn_shovel_x2 and btn_shovel_y1 < my < btn_shovel_y2:
                if shovel_count == 0:
                    shovel_count += 1
                    has_shovel_equipped = True
                    new_shovel = Shovel(random.randint(60, FARM_W - 60), random.randint(160, MARKET_Y1 - 60))
                    shovels.append(new_shovel)
                else:
                    if dirt >= next_shovel_cost:
                        dirt -= next_shovel_cost
                        shovel_count += 1
                        has_shovel_equipped = True
                        next_shovel_cost *= 1.4
                        new_shovel = Shovel(random.randint(60, FARM_W - 60), random.randint(160, MARKET_Y1 - 60))
                        shovels.append(new_shovel)

            # 买到铲子之后，解锁下面按钮
            if shovel_count > 0:
                btn_y += 50
                # 升级铲子
                btn_upgrade_shovel_x1, btn_upgrade_shovel_y1 = SHOP_X1 + 20, btn_y
                btn_upgrade_shovel_x2, btn_upgrade_shovel_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_upgrade_shovel_x1 < mx < btn_upgrade_shovel_x2 and btn_upgrade_shovel_y1 < my < btn_upgrade_shovel_y2:
                    cost = 30 * shovel_power_level
                    if dirt >= cost:
                        dirt -= cost
                        shovel_power_level += 1

                btn_y += 50
                # 购买小鸡
                btn_chicken_x1, btn_chicken_y1 = SHOP_X1 + 20, btn_y
                btn_chicken_x2, btn_chicken_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_chicken_x1 < mx < btn_chicken_x2 and btn_chicken_y1 < my < btn_chicken_y2:
                    if dirt >= next_chicken_cost:
                        dirt -= next_chicken_cost
                        chicken_count += 1
                        cx = random.randint(40, FARM_W - 40)
                        cy = random.randint(140, MARKET_Y1 - 40)
                        chickens.append(Chicken(cx, cy))
                        next_chicken_cost *= 1.5

            # 买到小鸡之后，解锁小鸡相关和补给按钮 + 多蛋拖拽升级
            if chicken_count > 0:
                btn_y += 50
                # 鸡-产蛋数量升级
                btn_upgrade_amount_x1, btn_upgrade_amount_y1 = SHOP_X1 + 20, btn_y
                btn_upgrade_amount_x2, btn_upgrade_amount_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_upgrade_amount_x1 < mx < btn_upgrade_amount_x2 and btn_upgrade_amount_y1 < my < btn_upgrade_amount_y2:
                    cost = 20 * chickens[0].amount_level
                    if gold >= cost:
                        gold -= cost
                        for ck in chickens:
                            ck.upgrade_amount()

                btn_y += 50
                # 鸡-产蛋速度升级
                btn_upgrade_speed_x1, btn_upgrade_speed_y1 = SHOP_X1 + 20, btn_y
                btn_upgrade_speed_x2, btn_upgrade_speed_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_upgrade_speed_x1 < mx < btn_upgrade_speed_x2 and btn_upgrade_speed_y1 < my < btn_upgrade_speed_y2:
                    cost = 25 * chickens[0].speed_level
                    if gold >= cost:
                        gold -= cost
                        for ck in chickens:
                            ck.upgrade_speed()

                btn_y += 50
                # 【新增】一次多拖鸡蛋升级按钮
                btn_multi_x1, btn_multi_y1 = SHOP_X1 + 20, btn_y
                btn_multi_x2, btn_multi_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_multi_x1 < mx < btn_multi_x2 and btn_multi_y1 < my < btn_multi_y2:
                    cost = multi_drag_cost_base * multi_drag_level
                    if gold >= cost:
                        gold -= cost
                        multi_drag_level += 1

                btn_y += 50
                # 补给食槽
                btn_refill_feed_x1, btn_refill_feed_y1 = SHOP_X1 + 20, btn_y
                btn_refill_feed_x2, btn_refill_feed_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_refill_feed_x1 < mx < btn_refill_feed_x2 and btn_refill_feed_y1 < my < btn_refill_feed_y2:
                    if gold >= feed_trough["refill_cost"]:
                        gold -= feed_trough["refill_cost"]
                        feed_trough["stock"] = feed_trough["max"]

                btn_y += 50
                # 补给水槽
                btn_refill_water_x1, btn_refill_water_y1 = SHOP_X1 + 20, btn_y
                btn_refill_water_x2, btn_refill_water_y2 = SHOP_X2 - 20, btn_y + 40
                if btn_refill_water_x1 < mx < btn_refill_water_x2 and btn_refill_water_y1 < my < btn_refill_water_y2:
                    if gold >= water_trough["refill_cost"]:
                        gold -= water_trough["refill_cost"]
                        water_trough["stock"] = water_trough["max"]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if len(dragging_eggs) > 0:
                mx, my = pygame.mouse.get_pos()
                # 全部鸡蛋卖到市场
                if SHOP_X1 < mx < SHOP_X2 and MARKET_Y1 < my < HEIGHT:
                    for e in dragging_eggs:
                        e.is_sold = True
                        gold += 3.0
                for e in dragging_eggs:
                    e.dragging = False
                dragging_eggs.clear()

        if event.type == pygame.MOUSEMOTION:
            if len(dragging_eggs) > 0:
                mx, my = pygame.mouse.get_pos()
                for e in dragging_eggs:
                    e.x, e.y = mx, my

    # 鸡逻辑更新
    for ck in chickens:
        ck.decay_hunger_thirst()
        nearest_shovel = ck.move_to_target(shovels)

        # 鸡碰到铲子挖土
        if nearest_shovel is not None and ck.check_collision_with_shovel(nearest_shovel):
            dirt += base_dirt_per_click * shovel_power_level
            nearest_shovel.move_random()

        # 鸡产蛋
        if ck.update(now):
            for _ in range(ck.amount_level):
                new_egg = Egg(ck.x + random.randint(-6, 6), ck.y + 10)
                eggs.append(new_egg)
            ck.egg_ready = False
            ck.last_spawn = now

    # 更新鸡蛋
    for e in eggs:
        if not e.dragging:
            e.update()
    eggs = [e for e in eggs if not e.is_sold]

    # 绘制铲子
    for s in shovels:
        s.draw(screen)
    # 绘制鸡
    for ck in chickens:
        pygame.draw.circle(screen, ck.get_color(), (ck.x, ck.y), ck.radius)
    # 绘制鸡蛋
    for e in eggs:
        pygame.draw.circle(screen, EGG_COLOR, (e.x, e.y), e.radius)
        pygame.draw.circle(screen, (180, 150, 100), (e.x, e.y), e.radius, 2)

    # ==========【上方固定文字，永远不动！】==========
    t1 = font.render(f"Dirt: {dirt:.1f}", True, WHITE)
    t2 = font.render(f"Gold: {gold:.1f}", True, WHITE)
    t3 = font.render(f"Chickens: {chicken_count}", True, WHITE)
    t_shovel = font.render(f"Shovels: {shovel_count} | Shovel Lv.{shovel_power_level}", True, WHITE)
    t_multi = font.render(f"Multi-Drag: {multi_drag_level}", True, WHITE)
    screen.blit(t1, (FARM_W + 20, 140))
    screen.blit(t2, (FARM_W + 20, 180))
    screen.blit(t3, (FARM_W + 20, 220))
    screen.blit(t_shovel, (FARM_W + 20, 260))
    screen.blit(t_multi, (FARM_W + 20, 300))

    # 计算按钮总高度，更新最大滚动值
    total_btn_count = 1
    if shovel_count>0: total_btn_count +=2
    if chicken_count>0: total_btn_count +=5
    total_btn_height = total_btn_count * 50
    MAX_SCROLL = max(0, total_btn_height - SCROLL_CONTAINER_HEIGHT)

    # ====================== 绘制滚动按钮区域 + 裁剪 ======================
    # 设置裁剪区域，只有在这个矩形内的内容才会画出来，超出直接隐藏
    clip_rect = (SHOP_X1, SCROLL_CONTAINER_TOP, SHOP_X2 - SHOP_X1, SCROLL_CONTAINER_HEIGHT)
    screen.set_clip(clip_rect)

    btn_y = SCROLL_CONTAINER_TOP + scroll_offset
    # 购买铲子按钮
    pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
    if shovel_count == 0:
        btn_shovel_text = font.render("Get Shovel (FREE)", True, WHITE)
    else:
        btn_shovel_text = font.render(f"Buy Shovel ({next_shovel_cost:.1f} Dirt)", True, WHITE)
    screen.blit(btn_shovel_text, (SHOP_X1 + 30, btn_y + 8))

    # 铲子存在，绘制升级铲子 + 买鸡按钮
    if shovel_count > 0:
        btn_y += 50
        #升级铲子
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        shovel_upgrade_cost = 30 * shovel_power_level
        btn_upgrade_shovel_text = font.render(f"Upgrade Shovel ({shovel_upgrade_cost:.1f} Dirt)", True, WHITE)
        screen.blit(btn_upgrade_shovel_text, (SHOP_X1 + 30, btn_y + 8))

        btn_y += 50
        #买小鸡
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        btn_chicken_text = font.render(f"Buy Chicken ({next_chicken_cost:.1f} Dirt)", True, WHITE)
        screen.blit(btn_chicken_text, (SHOP_X1 + 30, btn_y + 8))

    # 有小鸡，绘制小鸡升级、多蛋拖拽、补给按钮
    if chicken_count > 0:
        btn_y += 50
        #升级产蛋数量
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        cost = 20 * chickens[0].amount_level
        btn_amount_text = font.render(f"Upgrade Amount ({cost} Gold)", True, WHITE)
        screen.blit(btn_amount_text, (SHOP_X1 + 30, btn_y + 8))

        btn_y += 50
        #升级产蛋速度
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        cost = 25 * chickens[0].speed_level
        btn_speed_text = font.render(f"Upgrade Speed ({cost} Gold)", True, WHITE)
        screen.blit(btn_speed_text, (SHOP_X1 + 30, btn_y + 8))

        btn_y += 50
        #新增：多蛋拖拽升级
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        multi_cost = multi_drag_cost_base * multi_drag_level
        btn_multi_text = font.render(f"Upgrade Multi-Drag ({multi_cost} Gold)", True, WHITE)
        screen.blit(btn_multi_text, (SHOP_X1 + 30, btn_y + 8))

        btn_y += 50
        #补给食槽
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        btn_refill_feed_text = font.render(f"Refill Feed ({feed_trough['refill_cost']} Gold)", True, WHITE)
        screen.blit(btn_refill_feed_text, (SHOP_X1 + 30, btn_y + 8))

        btn_y += 50
        #补给水槽
        pygame.draw.rect(screen, BROWN_BTN, (SHOP_X1+20, btn_y, SHOP_X2 - SHOP_X1 -40, 40))
        btn_refill_water_text = font.render(f"Refill Water ({water_trough['refill_cost']} Gold)", True, WHITE)
        screen.blit(btn_refill_water_text, (SHOP_X1 + 30, btn_y + 8))

    # 清除裁剪！非常重要，不然别的画面会被裁剪掉
    screen.set_clip(None)

    tip = font_small.render(
        "Scroll mouse wheel on panel. Multi-Drag: pick up multiple eggs at once.",
        True, WHITE
    )
    screen.blit(tip, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
