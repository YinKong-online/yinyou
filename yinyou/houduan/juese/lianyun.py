import os
import pygame

def get_role_image_path():
    return os.path.join("houduan", "juese", "images", "lianyun.png")

def some_role_logic():
    print("连韵的特殊逻辑")

def use_skill(roles, current_role_index, next_role_index):
    print("连韵使用了技能")
    current_time = pygame.time.get_ticks() / 1000.0
    last_skill_time = roles[current_role_index]['last_skill_time']
    time_since_last_skill = current_time - last_skill_time
    
    if time_since_last_skill >= roles[current_role_index]['skill_cooldown']:
        # 计算连击效果
        n = 100  # 连击冷却时间100秒
        roles[current_role_index]['skill_timer'] = n * roles[current_role_index]['passive_effect_level']
        roles[current_role_index]['skill_active'] = True
        roles[current_role_index]['skill_cooldown'] = 100
        roles[current_role_index]['last_skill_time'] = current_time
        print(f"技能冷却时间 {roles[current_role_index]['skill_timer']} 秒")
        
        return 100  # 技能冷却时间为100秒
    else:
        return roles[current_role_index]['skill_cooldown']

def apply_beidong_effect(roles, current_role_index):
    print("连韵被触动了")
    if 'passive_effect_timer' not in roles[current_role_index]:
        roles[current_role_index]['passive_effect_timer'] = pygame.time.get_ticks() / 1000.0
        roles[current_role_index]['passive_effect_level'] = 1
    
    current_time = pygame.time.get_ticks() / 1000.0
    time_since_beidong = current_time - roles[current_role_index]['passive_effect_timer']
    
    if time_since_beidong <= 5 * roles[current_role_index]['passive_effect_level']:
        roles[current_role_index]['score'] *= 1.25
        print(f"被动效果生效，当前分数变为 {roles[current_role_index]['score']}")
    else:
        roles[current_role_index]['passive_effect_level'] = min(roles[current_role_index]['passive_effect_level'] + 1, 6)
        roles[current_role_index]['passive_effect_timer'] = current_time
        print(f"被动效果升级到第 {roles[current_role_index]['passive_effect_level']} 级")

def check_skill_effect(roles, current_role_index):
    if 'skill_active' in roles[current_role_index] and roles[current_role_index]['skill_active']:
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - roles[current_role_index]['last_skill_time'] >= roles[current_role_index]['skill_timer']:
            roles[current_role_index]['skill_active'] = False
            print("技能效果解除")
