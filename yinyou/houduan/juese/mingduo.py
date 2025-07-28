import pygame
import os

def get_role_image_path():
    return os.path.join("houduan", "juese", "images", "mingduo.png")

def some_role_logic():
    print("铭铎的特殊逻辑")

def use_skill(role_module, roles, current_role_index, next_role_index):
    print("铭铎使用了技能")
    # 刷新下一个上场角色的技能
    if next_role_index is not None:
        roles[next_role_index]['skill_cooldown'] = 0  # 刷新技能冷却时间
    return 50  # 技能冷却时间为50秒

def apply_beidong_effect(roles, current_role_index):
    print("铭铎被触动了")
    # 上场角色的CD本局永久减20秒
    roles[current_role_index]['skill_cooldown'] -= 20
    if roles[current_role_index]['skill_cooldown'] < 0:
        roles[current_role_index]['skill_cooldown'] = 0
    
    # 场下角色的CD本局永久减10秒
    for i in range(len(roles)):
        if i != current_role_index:
            roles[i]['skill_cooldown'] -= 10
            if roles[i]['skill_cooldown'] < 0:
                roles[i]['skill_cooldown'] = 0

def check_skill_effect(roles, current_role_index):
    role = roles[current_role_index]
    if 'skill_active' in role and role['skill_active']:
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - role['last_skill_time'] >= role['skill_timer']:
            role['skill_active'] = False
            print("技能效果解除")