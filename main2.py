import pygame
import sys
import math
import random

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
STEEL = (176, 196, 222)
DARK_STEEL = (130, 148, 165)  # 튕겨나갈 때 사용할 어두운 검 색상


class Player:
    def __init__(self, name, max_stamina):
        self.name = name
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.guard_state = 'none'
        self.is_defenseless = False
        self.defenseless_timer = 0
        self.x = 400
        self.y = 500

    def update_stamina(self, amount, tf):
        if tf == 0:
            self.stamina -= math.floor(amount*1.2)
        elif tf == 1:
            print(self.stamina)
            self.stamina -= amount
            print(self.stamina)
        # if self.stamina <= 0 :
        #     pygame.quit()
    def check_guard_failure(self, player_guard_direction, enemy_direction, damage, enemy, current_time,degree):
        if enemy_direction != -1 and enemy_direction != player_guard_direction:
            self.update_stamina(damage, 0)
        elif enemy_direction != -1 and enemy_direction == player_guard_direction:
            self.update_stamina(damage, 1)
            enemy.stamina -= math.ceil(damage * (1+degree))
            # 가드 성공 시 적에게 튕김 연출 트리거 전달
            enemy.trigger_recoil(current_time)

    def check_stamina_zero(self):
        if self.stamina <= 0 :
            return True
        else :
            return False

    def execute_enemy(self, enemy):
        pass

    def take_damage(self, damage):
        pass

    def guard_off(self):
        self.guard_state = 'none'

    def draw(self, screen):
        shield_color = GRAY

        if self.guard_state == 'w':
            shield_points = [(180, 400), (620, 400), (580, 530), (220, 530)]
        elif self.guard_state == 'a':
            shield_points = [(180, 430), (380, 370), (380, 540), (230, 580)]
            shield_color = DARK_GRAY
        elif self.guard_state == 'd':
            shield_points = [(420, 370), (620, 430), (570, 580), (420, 540)]
            shield_color = DARK_GRAY
        else:
            shield_points = [(260, 470), (540, 470), (520, 600), (280, 600)]

        pygame.draw.polygon(screen, shield_color, shield_points)
        pygame.draw.polygon(screen, BLACK, shield_points, 3)


class Enemy:
    def __init__(self, max_stamina, damage, is_boss=False):
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.damage = damage
        self.is_boss = is_boss
        self.is_defenseless = False
        self.attack_direction = -1
        self.x = 400
        self.y = 250

        self.state = 'idle'  # 'idle', 'windup', 'attacking', 'recoil'
        self.state_start_time = 0
        self.windup_duration = 800
        self.attack_duration = 300
        self.recoil_impact_duration = 80  # 공격 타격 위치에 순간 멈추는 시간
        self.recoil_duration = 300  # 튕겨 나가는 시간

    def start_attack(self, current_time):
        self.state = 'windup'
        self.state_start_time = current_time
        self.attack_direction = random.randint(0, 2)

    def trigger_recoil(self, current_time):
        """가드 당했을 때 공격 임팩트 후 튕겨 나가는 상태로 전환"""
        self.state = 'recoil'
        self.state_start_time = current_time

    def update(self, current_time):
        hit_direction = -1

        if self.state == 'windup':
            if current_time - self.state_start_time >= self.windup_duration:
                self.state = 'attacking'
                self.state_start_time = current_time
                hit_direction = self.attack_direction

        elif self.state == 'attacking':
            if current_time - self.state_start_time >= self.attack_duration:
                self.reset_stance()

        elif self.state == 'recoil':
            total_recoil_time = self.recoil_impact_duration + self.recoil_duration
            if current_time - self.state_start_time >= total_recoil_time:
                self.reset_stance()

        return hit_direction

    def reset_stance(self):
        self.state = 'idle'
        self.attack_direction = -1

    def take_recoil(self, amount):
        pass

    def check_stamina_zero(self):
        if self.stamina <= 0 :
            return True
        else :
            return False


    def die(self):
        pass

    def draw(self, screen, current_time):
        # 1. 공격 및 위치 오프셋 설정
        offset_y = 0
        width_add = 0
        height_add = 0

        if self.state == 'attacking':
            offset_y = 30
            width_add = 30
            height_add = 40
        elif self.state == 'recoil':
            elapsed = current_time - self.state_start_time
            if elapsed < self.recoil_impact_duration:
                offset_y = 30
                width_add = 30
                height_add = 40
            else:
                offset_y = -10

        enemy_x = 320 - (width_add // 2)
        enemy_y = 190 + offset_y
        enemy_w = 160 + width_add
        enemy_h = 210 + height_add

        body_rect = (enemy_x, enemy_y, enemy_w, enemy_h)
        pygame.draw.rect(screen, RED, body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 2)

        if self.is_boss:
            crown_y = enemy_y - 40
            pygame.draw.polygon(screen, YELLOW, [(360, crown_y), (380, crown_y - 30), (400, crown_y)])
            pygame.draw.polygon(screen, YELLOW, [(400, crown_y), (420, crown_y - 30), (440, crown_y)])

        # 기본 손(칼 자루) 위치
        sword_start = (400, enemy_y + 130)

        # 2. 상태별 손 위치와 칼 끝 위치 및 색상 계산
        if self.state == 'windup':
            # 준비 동작: 어두운 색상(DARK_STEEL) 적용 -> 밝은 색상(STEEL)로 변경함
            if self.attack_direction == 0:  # 좌측 공격 준비 -> 오른쪽으로 손과 칼을 당김
                sword_start = (470, enemy_y + 80)
                sword_end = (550, 100)
            elif self.attack_direction == 2:  # 우측 공격 준비 -> 왼쪽으로 손과 칼을 당김
                sword_start = (330, enemy_y + 80)
                sword_end = (250, 100)
            else:  # 정면 공격 준비 -> 가슴 중앙으로 높이 올림
                sword_start = (400, enemy_y + 60)
                sword_end = (400, 70)

            pygame.draw.line(screen, STEEL, sword_start, sword_end, 10)

        elif self.state == 'attacking':
            # 내려찍기 모션: 일반 밝은 칼 색상(STEEL) 적용
            if self.attack_direction == 0:
                sword_end = (160, 420)
            elif self.attack_direction == 1:
                sword_end = (400, 520)
            elif self.attack_direction == 2:
                sword_end = (640, 420)
            else:
                sword_end = (400, 80)

            pygame.draw.line(screen, STEEL, sword_start, sword_end, 12)

        elif self.state == 'recoil':
            elapsed = current_time - self.state_start_time

            # Phase 1: 공격 충돌 순간 모션 (잠깐 멈춤)
            if elapsed < self.recoil_impact_duration:
                if self.attack_direction == 0:
                    sword_end = (160, 420)
                elif self.attack_direction == 1:
                    sword_end = (400, 520)
                elif self.attack_direction == 2:
                    sword_end = (640, 420)
                else:
                    sword_end = (400, 80)
                pygame.draw.line(screen, STEEL, sword_start, sword_end, 12)

            # Phase 2: 방패에 맞고 크게 튕겨 나가는 모션 - 어두운 색상(DARK_STEEL) 적용
            else:
                sword_start = (400, enemy_y + 90)
                if self.attack_direction == 0:
                    sword_end = (100, 180)
                elif self.attack_direction == 1:
                    sword_end = (400, 120)
                elif self.attack_direction == 2:
                    sword_end = (700, 180)
                else:
                    sword_end = (400, 120)
                pygame.draw.line(screen, DARK_STEEL, sword_start, sword_end, 10)

        else:
            # 기본 대기 상태
            sword_end = (400, 100)
            pygame.draw.line(screen, STEEL, sword_start, sword_end, 10)

        # 손(검은색 원) 그리기
        pygame.draw.circle(screen, BLACK, sword_start, 8)


class Game:
    def __init__(self):
        self.kill_count = 0
        self.round = 1

    def show_upgrade_menu(self):
        pass

    def apply_upgrade(self, choice):
        pass


def draw_ui(screen, player):
    font = pygame.font.SysFont("malgun gothic", 20)

    bar_width = 300
    bar_height = 25
    pygame.draw.rect(screen, BLACK, (20, 20, bar_width, bar_height))

    current_width = int(bar_width * (player.stamina / player.max_stamina))
    pygame.draw.rect(screen, YELLOW, (20, 20, current_width, bar_height))
    pygame.draw.rect(screen, WHITE, (20, 20, bar_width, bar_height), 2)

    text = font.render(f"STAMINA : {math.floor(player.stamina)} / {player.max_stamina}", True, BLACK)
    screen.blit(text, (25, 50))


def main():
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Guard Fighter")

    stamina_increase = True
    no_stamina_increase_time = 0
    player_stun = False
    player_stun_time = 0
    clock = pygame.time.Clock()
    FPS = 60

    player = Player('LL', 100)
    enemy = Enemy(max_stamina=100, damage=50, is_boss=False)
    game = Game()

    running = True

    guard_start_time = 0
    guard_duration = 300
    is_guarding = False

    enemy_last_attack_time = pygame.time.get_ticks()
    enemy_attack_interval = 3000

    player_guard_direction = -1

    while running:
        current_time = pygame.time.get_ticks()

        if player_stun == False :
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if is_guarding:
                        continue
                    if event.key in (pygame.K_w, pygame.K_a, pygame.K_d):
                        guard_start_time = current_time
                        is_guarding = True
                        stamina_increase = False

                        if event.key == pygame.K_w:
                            player.guard_state = 'w'
                            player_guard_direction = 1
                            #print('전면 가드')
                        elif event.key == pygame.K_a:
                            player.guard_state = 'a'
                            player_guard_direction = 0
                            #print('좌측 가드')
                        elif event.key == pygame.K_d:
                            player.guard_state = 'd'
                            player_guard_direction = 2
                            #print('우측 가드')

                    elif event.key == pygame.K_f:
                        if enemy.check_stamina_zero() == True :
                            print('처치')
                            player.execute_enemy(enemy)
                            player.stamina -= 50
                            enemy.die()

        # 1. 가드 시간 처리
        if is_guarding and (current_time - guard_start_time >= guard_duration):
            player.guard_off()
            is_guarding = False
            stamina_increase = True
            player_guard_direction = -1
            no_stamina_increase_time = current_time


        # 2. 적 공격 타이밍 제어 (idle 상태일 때만 새로운 공격 시작)
        if enemy.check_stamina_zero() == False :
            if enemy.state == 'idle' and (current_time - enemy_last_attack_time >= enemy_attack_interval):
                enemy.start_attack(current_time)
                enemy_last_attack_time = current_time

        # 3. 적 상태 업데이트 및 피격 검사
        hit_direction = enemy.update(current_time)
        degree = 0
        if hit_direction != -1:
            update_damage = enemy.damage
            if is_guarding == True :
                if -300 <= guard_start_time - current_time < -200 :
                    degree = 0.2
                    if math.floor(enemy.damage*0.8) == enemy.damage :
                        update_damage = enemy.damage -1
                    else :
                        update_damage = math.floor(enemy.damage*0.8)
                    print("fast")
                elif -200 <= guard_start_time - current_time < 0 :
                    degree = 0.5
                    update_damage = math.floor(enemy.damage*0.5)
                    print("perfect!!")
                elif 0 <= guard_start_time - current_time < 100 :
                    degree = -0.2
                    if math.floor(enemy.damage*1.2) == enemy.damage :
                        update_damage = enemy.damage +1
                    else :
                        update_damage = math.floor(enemy.damage*1.2)
                    print("slow")
            player.check_guard_failure(player_guard_direction, hit_direction, update_damage, enemy, current_time,degree)

        # 4. 화면 그리기
        screen.fill(WHITE)
        pygame.draw.rect(screen, (220, 220, 220), (0, 300, 800, 300))
        pygame.draw.line(screen, BLACK, (0, 300), (800, 300), 2)

        enemy.draw(screen, current_time)
        player.draw(screen)

        draw_ui(screen, player)

        pygame.display.flip()
        clock.tick(FPS)

        if player.check_stamina_zero() == True :
            no_stamina_increase_time = current_time
            player.stamina = 0.1
            player_stun_time = current_time
            player_stun = True

        if current_time - player_stun_time > 5000 :
            player_stun = False

        if player.stamina < 0 :
            player.stamina = 0

        if player.stamina >= 70 :
            if current_time - no_stamina_increase_time > 1000 :
                if stamina_increase == True and player.stamina < 100 :
                    player.stamina += 0.1
        else :
            if player.stamina == 0:
                if current_time - no_stamina_increase_time > 1300 :
                    if stamina_increase == True and player.stamina < 100 :
                        player.stamina += 0.05
            else :
                if current_time - no_stamina_increase_time > 1300:
                    if stamina_increase == True and player.stamina < 100 :
                        player.stamina += 0.05
        if player.stamina >= 100 :
            player.stamina = 100

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()