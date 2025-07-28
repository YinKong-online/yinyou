import pygame
import json
import requests
import sys
import random
import math
import os
import webbrowser

pygame.init()
pygame.mixer.init()

# 设置屏幕
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# 初始化得分变量
perfect_count = 0
success_count = 0
miss_count = 0

# 加载音效和图片资源
#hit_sound = pygame.mixer.Sound("hit_sound.wav")
star_image = pygame.image.load(r"game\star.png")
star_image = pygame.transform.scale(star_image, (50, 50))

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

# 设置加载动画参数
loading_radius = 50
loading_color = (0, 0, 255)
loading_center = (screen_width // 2, screen_height // 2)
loading_angle = 0
loading_speed = 5

# 获取查询字符串中的歌曲名称
target_name = sys.argv[1] if len(sys.argv) > 1 else None
if not target_name:
    print("歌曲名称未提供。")
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
            loading_center[1] + loading_radius * math.sin(math.radians(end_rad))
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
        yinpin = None
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

# 音符参数
note_width = 50
note_height = 50
note_speed = 100  # 音符移动速度，单位为像素/秒
spawn_rate = 1000  # 音符生成频率，单位为毫秒
spawn_time = pygame.time.get_ticks() + spawn_rate

# 音符列表
notes = []

# 玩家输入检测
def check_input(event, note):
    if note['direction'] == 'up' and event.key == pygame.K_w:
        return True
    elif note['direction'] == 'down' and event.key == pygame.K_s:
        return True
    elif note['direction'] == 'left' and event.key == pygame.K_a:
        return True
    elif note['direction'] == 'right' and event.key == pygame.K_d:
        return True
    return False

# 主循环
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # 生成新的音符
    if current_time > spawn_time:
        spawn_time += spawn_rate
        note_direction = random.choice(['up', 'down', 'left', 'right'])
        note = {
            'direction': note_direction,
            'time': current_time / 1000.0,
            'rect': pygame.Rect(screen_width // 2, screen_height, note_width, note_height)
        }
        notes.append(note)
    
    # 更新音符位置
    for note in notes:
        note['rect'].y -= note_speed * (current_time / 1000.0 - note['time'])
    
    # 移除超出屏幕的音符
    notes = [note for note in notes if note['rect'].y > -note_height]
    
    # 检查玩家输入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                webbrowser.open('jiandan.html')
            # 检测按键并处理音符
            for note in notes:
                if check_input(event, note):
                    if abs(note['rect'].y - (screen_height // 2 - note_height // 2)) < 10:
                        perfect_count += 1
                    elif abs(note['rect'].y - (screen_height // 2 - note_height // 2)) < 30:
                        success_count += 1
                    else:
                        miss_count += 1
                    notes.remove(note)
                    break
    
    # 绘制音符
    screen.fill(white)
    for note in notes:
        pygame.draw.rect(screen, blue, note['rect'])
    
    # 显示得分和评星
    total_notes = perfect_count + success_count + miss_count
    score = (perfect_count + success_count) / total_notes * 100 if total_notes > 0 else 0
    font = pygame.font.Font(None, 72)
    score_text = font.render(f"得分: {score:.2f}%", True, black)
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 3))
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
    screen.blit(exit_text, exit_text_rect)
    
    # 点击退出按钮的检测
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if exit_text_rect.collidepoint(mouse_pos):
                running = False
                webbrowser.open('jiandan.html')

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()