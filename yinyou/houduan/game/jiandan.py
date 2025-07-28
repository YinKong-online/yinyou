import os
import pygame
import json
import requests
import sys
import random
import math
import webbrowser
import importlib.util

pygame.init()
pygame.mixer.init()

# 设置屏幕
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
sub_screen = pygame.Surface((1340, 870))

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 255)

screen_width, screen_height = screen.get_size()
role_image_width = 90
role_image_height = int(role_image_width * 8 / 6)
image_gap = role_image_width // 5 +  100
image_gap1 = role_image_width // 5
# 加载动画参数
loading_radius = 50
loading_color = (0, 0, 255)
loading_center = (screen_width // 2, screen_height // 2)
loading_angle = 0
loading_speed = 5

# 设置音符参数
num_lanes = 8
lane_width = sub_screen.get_width() // num_lanes
width = 100
height = 20
fall_speed = 10  # 调整速度以适应游戏体验

# 检测线参数
detector_y = sub_screen.get_height() - 200  # 检测线提高
detector_height = 100
detector_line_width = 5
perfect_region_height = detector_height // 3
success_region_height = detector_height // 3

# 定义颜色范围
yellow = (255, 255, 0)
light_yellow = (255, 255, 153)
light_blue = (153, 204, 255)
light_red = (255, 153, 153)

# 获取查询字符串中的歌曲名称和角色名称（拼音）
target_name = sys.argv[1] if len(sys.argv) > 1 else None
role_names = sys.argv[2:6] if len(sys.argv) > 2 else None  # 假设前端发送最多4个角色名称
print(f"role_names: {role_names}")
if not target_name:
    print("歌曲名称未提供。")
    pygame.quit()
    sys.exit()

if not role_names or len(role_names) != 4:
    print("角色名称未提供或不足4个。")
    pygame.quit()
    sys.exit()

# 获取JSON数据
url = "https://yinkong-online.github.io/yinyou/chuli.json"
response = requests.get(url)

# 显示等待动画
loading_font = pygame.font.Font(None, 36)
loading_text = loading_font.render("正在加载...", True, (0, 0, 0))
loading_text_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))

loading = True
start_loading_time = pygame.time.get_ticks()  # 记录开始加载的时间
while loading:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill((255, 255, 255))
    screen.blit(loading_text, loading_text_rect)

    # 绘制旋转的圆圈
    for i in range(0, 360, 45):
        end_rad = loading_angle + i
        end_pos = (
            loading_center[0] + loading_radius * math.cos(math.radians(end_rad)),
            loading_center[1] + loading_radius * math.sin(math.radians(end_rad))  # 修正了此处的错误
        )
        pygame.draw.line(screen, loading_color, loading_center, end_pos, 5)
    loading_angle += loading_speed
    if loading_angle >= 360:
        loading_angle = 0

    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # 检查JSON数据是否加载完成
    if response.status_code == 200:
        data = json.loads(response.text)
        onset_times = None
        for item in data:
            if isinstance(item, dict) and 'name' in item and item['name'] == target_name:
                onset_times = item['onset_times']
                yinpin = item['filename']
                break
        if onset_times is None:
            print(f"onset_times not found for name '{target_name}' in the JSON data.")
            pygame.quit()
            sys.exit()
        loading = False
    else:
        # 检查是否已经过了5秒
        if (pygame.time.get_ticks() - start_loading_time) / 1000.0 >= 5:
            print("Failed to retrieve the JSON file within 5 seconds.")
            pygame.quit()
            sys.exit()

# 加载角色图片和逻辑
roles = []

for role_name in role_names:
    role_logic_path = os.path.join("houduan", "juese", f"{role_name}.py")
    try:
        spec = importlib.util.spec_from_file_location(f"{role_name}_module", role_logic_path)
        role_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(role_module)
        
        # 获取角色图片路径
        role_image_path = os.path.join("houduan", "juese", "images", f"{role_name}.png")
        
        # 确保图片文件存在
        if os.path.exists(role_image_path):
            role_image = pygame.image.load(role_image_path)
        else:
            print(f"Failed to load image for {role_name}: {role_image_path}")
            continue 
        
        # 初始化角色数据
        roles.append({
            'name': role_name,
            'module': role_module,
            'image': role_image,
            'score': 0,
            'skill_cooldown': 0,
            'last_skill_time': 0,
            'skill_active': False,
            'skill_timer': 0,
            'passive_effect_timer': 0,
            'passive_effect_level': 1
        })
    except Exception as e:
        print(f"Failed to load role logic for {role_name}: {e}")
        role_module = None
        role_image = None

# 加载音符音乐
filename = f"{target_name}.mp3"

if not os.path.exists(filename):
    try:
        response = requests.get(yinpin)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the audio file: {e}")
        pygame.quit()
        sys.exit()

pygame.mixer.music.load(filename)
pygame.mixer.music.play()

index = 0
notes = []
perfect_count = 0
success_count = 0
combo_color = white
combo_text = None
combo_start_time = 0

# 技能冷却相关
last_skill_time = 0
current_role_index = 0

# 游戏循环
running = True
start_time = pygame.time.get_ticks() / 1000.0
total_notes = len(onset_times)
while running:
    current_time = pygame.time.get_ticks() / 1000.0 - start_time + 2.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            for note in notes[:]:
                if note['rect'].y >= detector_y and note['rect'].y <= detector_y + detector_height:
                    lane = note['rect'].x // lane_width
                    key = None
                    if lane == 0:
                        key = pygame.K_a
                    elif lane == 1:
                        key = pygame.K_s
                    elif lane == 2:
                        key = pygame.K_d
                    elif lane == 3:
                        key = pygame.K_f
                    elif lane == 4:
                        key = pygame.K_j
                    elif lane == 5:
                        key = pygame.K_k
                    elif lane == 6:
                        key = pygame.K_l
                    elif lane == 7:
                        key = pygame.K_SEMICOLON

                    if event.key == key:
                        note_y = note['rect'].y - detector_y
                        if note_y >= 0 and note_y < perfect_region_height:
                            perfect_count += 1
                            success_count += 1
                            combo_color = yellow
                            roles[current_role_index]['module'].apply_beidong_effect(roles, current_role_index)  # 应用被触动效果
                        elif note_y >= perfect_region_height and note_y < perfect_region_height + success_region_height:
                            success_count += 1
                            combo_color = light_yellow
                        elif note_y >= perfect_region_height + success_region_height and note_y < detector_height:
                            success_count += 1
                            combo_color = light_blue

                        notes.remove(note)
                        combo_start_time = current_time
                        # hit_sound.play()
            
            # 使用技能
            if roles[current_role_index]['module'] and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and current_role_index == 0:
                    if current_time - last_skill_time >= roles[current_role_index]['skill_cooldown']:
                        roles[current_role_index]['skill_cooldown'] = roles[current_role_index]['module'].use_skill(
                            roles, current_role_index, (current_role_index + 1) % 4)
                        last_skill_time = current_time
                elif event.key == pygame.K_2 and current_role_index == 1:
                    if current_time - last_skill_time >= roles[current_role_index]['skill_cooldown']:
                        roles[current_role_index]['skill_cooldown'] = roles[current_role_index]['module'].use_skill(
                            roles, current_role_index, (current_role_index + 1) % 4)
                        last_skill_time = current_time
                elif event.key == pygame.K_3 and current_role_index == 2:
                    if current_time - last_skill_time >= roles[current_role_index]['skill_cooldown']:
                        roles[current_role_index]['skill_cooldown'] = roles[current_role_index]['module'].use_skill(
                            roles, current_role_index, (current_role_index + 1) % 4)
                        last_skill_time = current_time
                elif event.key == pygame.K_4 and current_role_index == 3:
                    if current_time - last_skill_time >= roles[current_role_index]['skill_cooldown']:
                        roles[current_role_index]['skill_cooldown'] = roles[current_role_index]['module'].use_skill(
                            roles, current_role_index, (current_role_index + 1) % 4)
                        last_skill_time = current_time

    if index < len(onset_times) and current_time >= onset_times[index]:
        lane = random.randint(0, num_lanes - 1)
        notes.append({
            'rect': pygame.Rect(lane * lane_width + (lane_width - width) // 2, -height, width, height),
            'time': onset_times[index]
        })
        index += 1

    notes_to_remove = []
    for note in notes:
        note['rect'].y += fall_speed * (current_time - note['time'])
        if note['rect'].y > sub_screen.get_height():
            notes_to_remove.append(note)

    for note in notes_to_remove:
        notes.remove(note)

    screen.fill(white)
    sub_screen.fill(black)

    for note in notes:
        pygame.draw.rect(sub_screen, white, note['rect'])

    pygame.draw.line(sub_screen, green, (0, detector_y), (sub_screen.get_width(), detector_y), detector_line_width)
    pygame.draw.line(sub_screen, blue, (0, detector_y + perfect_region_height), (sub_screen.get_width(), detector_y + perfect_region_height), 2)
    pygame.draw.line(sub_screen, blue, (0, detector_y + perfect_region_height + success_region_height), (sub_screen.get_width(), detector_y + perfect_region_height + success_region_height), 2)

    screen.blit(sub_screen, (100, 0))

    # 显示角色图片
    role_positions = [
        (image_gap, 745),  # 第一张图片的左边距为间隔
        (image_gap + image_gap1 + role_image_width, 745),  # 第二张图片
        (image_gap + 2 * image_gap1 + 2 * (role_image_width), 745),  # 第三张图片
        (image_gap + 3 * image_gap1 + 3 * (role_image_width), 745),  # 第四张图片
    ]

    for i, role in enumerate(roles):
        if i < 4:
            if i == current_role_index:
                # 场上角色，图片变大
                scaled_image = pygame.transform.scale(role['image'], (role_image_width + 1, role_image_height + 1))
                screen.blit(scaled_image, (role_positions[i][0] - 1, role_positions[i][1] - 1))
            else:
                # 场下角色，图片较小
                scaled_image = pygame.transform.scale(role['image'], (role_image_width, role_image_height))
                screen.blit(scaled_image, role_positions[i])

    if success_count >= 5 and current_time - combo_start_time < 2:  # 连击文本持续显示2秒
        font = pygame.font.Font(None, 36)
        combo_text = font.render(f"连击 x {success_count}", True, combo_color)
        screen.blit(combo_text, (screen_width // 2 - combo_text.get_width() // 2, screen_height // 2 - combo_text.get_height() // 2))

    # 检查技能效果
    for role in roles:
        role['module'].check_skill_effect(roles, roles.index(role))

    if index >= total_notes and not notes:
        running = False

    pygame.display.flip()
    pygame.time.Clock().tick(60)

# 计算得分
score = (perfect_count + success_count) / total_notes * 100

# 显示得分和评星
screen.fill(white)
font = pygame.font.Font(None, 72)
score_text = font.render(f"{score:.2f}%", True, black)
screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 3))

star_image = pygame.image.load(r"game\star.png")
star_image = pygame.transform.scale(star_image, (50, 50))
star_count = 0
if score >= 90:
    star_count = 3
elif score >= 70:
    star_count = 2
elif score >= 50:
    star_count = 1

for i in range(star_count):
    screen.blit(star_image, (screen_width // 2 - star_count * 50 // 2 + i * 50, screen_height // 2))

# 退出按钮
exit_font = pygame.font.Font(None, 36)
exit_text = exit_font.render("X", True, black)
exit_text_rect = exit_text.get_rect(topright=(screen_width - 10, 10))

# 游戏结束循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if exit_text_rect.collidepoint(mouse_pos):
                running = False
                webbrowser.open('jiandan.html')

    screen.blit(exit_text, exit_text_rect)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()