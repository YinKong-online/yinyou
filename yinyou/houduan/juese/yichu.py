import os
import pygame

def get_role_image_path():
    return os.path.join("houduan", "juese", "images", "yichu.png")

def some_role_logic():
    print("苡初的特殊逻辑")

def use_skill(roles, current_role_index, next_role_index):
    print("苡初使用了技能")
    # 计算技能分数
    current_time = pygame.time.get_ticks() / 1000.0
    last_skill_time = roles[current_role_index]['last_skill_time']
    time_since_last_skill = current_time - last_skill_time
    
    if time_since_last_skill >= 50:  # 技能冷却时间
        skill_score = time_since_last_skill * 80
        previous_score = roles[current_role_index]['score']
        new_score = previous_score * 0.60 + skill_score * 0.40
        roles[current_role_index]['score'] = new_score
        some_role_logic()
        print(f"使用技能，当前分数变为 {new_score}")
        
        # 更新当前角色的技能冷却时间和上次使用技能的时间
        roles[current_role_index]['skill_cooldown'] = 50
        roles[current_role_index]['last_skill_time'] = current_time
        
        return 50  # 技能冷却时间为50秒
    else:
        return roles[current_role_index]['skill_cooldown']

def apply_beidong_effect(roles, current_role_index):
    print("苡初被触动了")
    # 应用初始旋律被动效果
    if 'passive_effect_timer' not in roles[current_role_index]:
        roles[current_role_index]['passive_effect_timer'] = pygame.time.get_ticks() / 1000.0
        roles[current_role_index]['passive_effect_level'] = 1
    
    current_time = pygame.time.get_ticks() / 1000.0
    time_since_beidong = current_time - roles[current_role_index]['passive_effect_timer']
    
    if time_since_beidong <= 20 * roles[current_role_index]['passive_effect_level']:
        roles[current_role_index]['score'] *= 1.25
        print(f"被动效果生效，当前分数变为 {roles[current_role_index]['score']}")
    else:
        roles[current_role_index]['passive_effect_level'] = min(roles[current_role_index]['passive_effect_level'] + 1, 6)  # 被动效果最多升到6级
        roles[current_role_index]['passive_effect_timer'] = current_time  # 重置被动效果计时器
        print(f"被动效果升级到第 {roles[current_role_index]['passive_effect_level']} 级")

def check_skill_effect(roles, current_role_index):
    role = roles[current_role_index]
    if 'skill_active' in role and role['skill_active']:
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - role['last_skill_time'] >= role['skill_timer']:
            role['skill_active'] = False
            print("技能效果解除")
