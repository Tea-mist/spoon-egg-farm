import pygame
import random
import time

# 初始化pygame
pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Spoon Egg Farm")
clock = pygame.time.Clock()

# 字体（新版pygame兼容写法）
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

# 颜色定义
BG = (30, 30, 40)
GREEN = (60, 180, 80)
BROWN = (130, 90, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 60)
RED = (220, 60, 60)

# 游戏全局数据
dirt = 0  # 泥土
gold = 0  # 金币
chicken_list = []  # 小鸡列表
egg_list = []  # 鸡蛋列表
chicken_cost = 50  # 购买小鸡的泥土价格


# 小鸡类：同时挖土+产蛋
class Chicken:
    def __init__(self):
        self.x = random.randint(50, 400)
        self.y = random.randint(100, 480)
        self.dirt_per_sec = 0.8  # 每秒产出泥土
        self.egg_cd = random.uniform(3, 6)  # 产蛋冷却时间
        self.last_egg_time = time.time()

    def update(self, dt):
        global dirt
        # 自动挖土
        dirt += self.dirt_per_sec * dt
        # 产蛋判断
        now = time.time()
        if now - self.last_egg_time > self.egg_cd:
            egg_list.append(Egg(self.x, self.y))
            self.last_egg_time = now


# 鸡蛋类，点击卖出换金币
class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = 10  # 一枚鸡蛋卖10金币
        self.radius = 12

    def is_click(self, mx, my):
        dx = mx - self.x
        dy = my - self.y
        return dx * dx + dy * dy < self.radius * self.radius


# 主循环
running = True
while running:
    dt = clock.tick(60) / 1000.0
    now = time.time()
    screen.fill(BG)

    # 事件
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            # 点击画面空白：手动挖土
            dirt += 5
            # 点击鸡蛋卖蛋
            for egg in egg_list[:]:
                if egg.is_click(mx, my):
                    gold += egg.value
                    egg_list.remove(egg)
            # 右侧购买小鸡按钮
            if 520 < mx < 860 and 180 < my < 240:
                if dirt >= chicken_cost:
                    dirt -= chicken_cost
                    chicken_list.append(Chicken())
                    chicken_cost *= 1.15  # 涨价

    # 更新所有小鸡
    for ck in chicken_list:
        ck.update(dt)

    # ========== 绘制 ==========
    # 农场绿地
    pygame.draw.rect(screen, GREEN, (40, 80, 460, 480))
    # 绘制小鸡
    for ck in chicken_list:
        pygame.draw.circle(screen, RED, (int(ck.x), int(ck.y)), 14)
    # 绘制鸡蛋
    for egg in egg_list:
        pygame.draw.circle(screen, YELLOW, (int(egg.x), int(egg.y)), egg.radius)

    # 右侧UI面板
    pygame.draw.rect(screen, (50, 50, 70), (500, 80, 380, 480))
    # 资源文字
    t1 = font.render(f"Dirt: {dirt:.1f}", True, WHITE)
    t2 = font.render(f"Gold: {gold:.1f}", True, WHITE)
    t3 = font.render(f"Chickens: {len(chicken_list)}", True, WHITE)
    screen.blit(t1, (520, 90))
    screen.blit(t2, (520, 120))
    screen.blit(t3, (520, 150))

    # 购买小鸡按钮
    pygame.draw.rect(screen, BROWN, (520, 180, 320, 60))
    btn_text = font.render(f"Buy Chicken ({chicken_cost:.1f} Dirt)", True, WHITE)
    screen.blit(btn_text, (540, 195))

    tip = small_font.render("Click green area to get dirt | Click eggs to sell", True, WHITE)
    screen.blit(tip, (50, 20))

    pygame.display.flip()

pygame.quit()
