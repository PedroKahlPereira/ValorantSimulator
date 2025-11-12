import copy
import random
import math
from flask import Flask, request, jsonify, render_template
import os

# Certifique-se de que seus arquivos data.py e weapons.py estão corretos
from data import TEAMS
from weapons import WEAPONS

app = Flask(__name__)

# --- CONSTANTES GLOBAIS ---
AVAILABLE_MAPS = ["Ascent", "Bind", "Haven", "Icebox", "Lotus"]
WIN_REWARD, STARTING_CREDITS, MAX_CREDITS = 3000, 800, 9000
LIGHT_ARMOR_COST, HEAVY_ARMOR_COST = 400, 1000
KILL_REWARD = 200

ASSIST_PROBABILITY_BY_ROLE = {
    "Controller": 0.80, "Initiator": 0.75, "Sentinel": 0.65,
    "Flex": 0.60, "Duelist": 0.35,
}

MAP_LOCATIONS = {
    "Bind": {
        "A_Site": {"center": {"x": 0.28, "y": 0.25}, "attack_spawn": {"x": 0.25, "y": 0.08}},
        "B_Site": {"center": {"x": 0.75, "y": 0.70}, "attack_spawn": {"x": 0.90, "y": 0.75}},
        "Mid":    {"center": {"x": 0.5, "y": 0.5},   "attack_spawn": {"x": 0.5, "y": 0.25}}
    },
    "Ascent": {
        "A_Site": {"center": {"x": 0.25, "y": 0.35}, "attack_spawn": {"x": 0.15, "y": 0.45}},
        "B_Site": {"center": {"x": 0.75, "y": 0.65}, "attack_spawn": {"x": 0.90, "y": 0.55}},
        "Mid":    {"center": {"x": 0.5, "y": 0.5},   "attack_spawn": {"x": 0.40, "y": 0.80}}
    },
    "Haven": {
        "A_Site": {"center": {"x": 0.20, "y": 0.75}, "attack_spawn": {"x": 0.08, "y": 0.75}},
        "B_Site": {"center": {"x": 0.5, "y": 0.5},   "attack_spawn": {"x": 0.45, "y": 0.25}},
        "C_Site": {"center": {"x": 0.8, "y": 0.3},   "attack_spawn": {"x": 0.92, "y": 0.35}}
    },
    "Icebox": {
        "A_Site": {"center": {"x": 0.3, "y": 0.3}, "attack_spawn": {"x": 0.15, "y": 0.3}},
        "B_Site": {"center": {"x": 0.7, "y": 0.7}, "attack_spawn": {"x": 0.85, "y": 0.7}},
        "Mid":    {"center": {"x": 0.5, "y": 0.5}, "attack_spawn": {"x": 0.5, "y": 0.75}}
    },
    "Lotus": {
        "A_Site": {"center": {"x": 0.25, "y": 0.25}, "attack_spawn": {"x": 0.1, "y": 0.2}},
        "B_Site": {"center": {"x": 0.75, "y": 0.70}, "attack_spawn": {"x": 0.9, "y": 0.65}},
        "C_Site": {"center": {"x": 0.5, "y": 0.5},   "attack_spawn": {"x": 0.5, "y": 0.8}}
    },
}

def find_weapon_by_id(weapon_id):
    return next((w for w in WEAPONS if w['id'] == weapon_id), None)

def apply_damage(victim, damage):
    damage_to_armor = min(victim.get('armor', 0), damage)
    victim['armor'] -= damage_to_armor
    victim['health'] -= (damage - damage_to_armor)
    victim['health'] = max(0, round(victim['health']))

def set_map_specific_agents(team, map_name):
    pass

def calculate_duel_score(player, opponent):
    attrs = player['stats']
    base_score = attrs.get('Aim', 75) * 1.5
    weapon_type_advantage = 1.0
    if player['weapon']['type'] == 'Rifle' and opponent['weapon']['type'] == 'SMG': weapon_type_advantage = 1.1
    elif player['weapon']['type'] == 'SMG' and opponent['weapon']['type'] == 'Rifle': weapon_type_advantage = 0.9
    health_modifier = (player.get('health', 100) + player.get('armor', 0)) / 150.0
    final_score = base_score * weapon_type_advantage * health_modifier
    return final_score * (1 + (random.random() - 0.5) * 0.5)

def buy_weapons_for_team(team, round_number):
    for player in team['players']:
        if not player.get('is_alive', True): continue
        if round_number == 1 or round_number == 13:
            player.update({'weapon': find_weapon_by_id('classic'), 'armor': 0})
            if player['credits'] >= 800 and random.random() < 0.7:
                weapon_choice = find_weapon_by_id(random.choice(['ghost', 'sheriff']))
                if weapon_choice: player.update({'weapon': weapon_choice, 'credits': player['credits'] - weapon_choice['cost']})
            elif player['credits'] >= LIGHT_ARMOR_COST:
                player.update({'armor': 25, 'credits': player['credits'] - LIGHT_ARMOR_COST})
            continue
        if player['credits'] >= 2900 + HEAVY_ARMOR_COST:
            weapon_choice = find_weapon_by_id(random.choice(['vandal', 'phantom']))
            if weapon_choice: player.update({'weapon': weapon_choice, 'armor': 50, 'credits': player['credits'] - (weapon_choice['cost'] + HEAVY_ARMOR_COST)})
        elif player['credits'] >= 1600 + LIGHT_ARMOR_COST:
            weapon_choice = find_weapon_by_id('spectre')
            if weapon_choice: player.update({'weapon': weapon_choice, 'armor': 25, 'credits': player['credits'] - (weapon_choice['cost'] + LIGHT_ARMOR_COST)})
        else:
            player.update({'weapon': find_weapon_by_id('classic'), 'armor': 0})

def process_kill(killer, victim, damage_log, all_a, all_b, killer_pos, victim_pos):
    victim.update({'is_alive': False, 'deaths': victim['deaths'] + 1})
    killer['kills'] += 1
    killer['credits'] = min(MAX_CREDITS, killer['credits'] + KILL_REWARD)
    
    assister_name = None
    if victim['name'] in damage_log:
        potential_assisters = [name for name in damage_log[victim['name']] if name != killer['name']]
        if potential_assisters:
            chosen_assister_name = random.choice(potential_assisters)
            killer_team_players = all_a['players'] if any(p['name'] == killer['name'] for p in all_a['players']) else all_b['players']
            for p in killer_team_players:
                if p['name'] == chosen_assister_name:
                    if random.random() < ASSIST_PROBABILITY_BY_ROLE.get(p['role'], 0.60):
                        p['assists'] += 1
                        assister_name = p['name']
                    break
    
    return {
        "type": "kill", "killerName": killer['name'], "victimName": victim['name'], 
        "assisterName": assister_name, "weaponId": killer['weapon']['id'],
        "killerPosition": killer_pos, "victimPosition": victim_pos,
        "final_states": { p['name']: { 
            "health": p['health'], "armor": p['armor'], 
            "k": p['kills'], "d": p['deaths'], "a": p['assists'], 
            "credits": p['credits'], "weaponId": p['weapon']['id'] 
        } for p in all_a['players'] + all_b['players'] }
    }

def _simulate_confrontation(attackers, defenders, timeline, all_players_a, all_players_b, skirmish_positions):
    skirmish_damage_log = {}
    
    while attackers and defenders:
        p_a, p_b = random.choice(attackers), random.choice(defenders)
        score_a, score_b = calculate_duel_score(p_a, p_b), calculate_duel_score(p_b, p_a)
        shooter, target = (p_a, p_b) if random.random() < (score_a / (score_a + score_b)) else (p_b, p_a)
        
        damage = shooter['weapon']['damage_body']
        apply_damage(target, damage)
        skirmish_damage_log.setdefault(target['name'], set()).add(shooter['name'])
        
        shooter_pos = skirmish_positions.get(shooter['name'])
        target_pos = skirmish_positions.get(target['name'])

        if target['health'] <= 0:
            kill_event = process_kill(shooter, target, skirmish_damage_log, all_players_a, all_players_b, shooter_pos, target_pos)
            kill_event['victimState'] = {"health": 0, "armor": target['armor']}
            timeline.append(kill_event)
            
            attackers = [p for p in attackers if p['is_alive']]
            defenders = [p for p in defenders if p['is_alive']]
        else:
            timeline.append({
                "type": "damage", "attackerName": shooter['name'], "victimName": target['name'],
                "damageDealt": damage, "weaponId": shooter['weapon']['id'],
                "attackerPosition": shooter_pos, "victimPosition": target_pos,
                "victimState": {"health": target['health'], "armor": target['armor']}
            })
    return attackers, defenders

def generate_positions_for_group(players, base_coords, radius, positions_dict):
    num_players = len(players)
    if num_players == 0: return
        
    for i, p in enumerate(players):
        if num_players == 1:
            offset_x, offset_y = (random.random() - 0.5) * 0.02, (random.random() - 0.5) * 0.02
        else:
            angle = (2 * math.pi / num_players) * i
            offset_x = radius * math.cos(angle)
            offset_y = radius * math.sin(angle)
        
        positions_dict[p['name']] = {
            'x': base_coords['x'] + offset_x,
            'y': base_coords['y'] + offset_y
        }

def simulate_full_round(team_a, team_b, round_number, map_name, skip_buy_phase=False):
    temp_a, temp_b = copy.deepcopy(team_a), copy.deepcopy(team_b)
    for p in temp_a['players'] + temp_b['players']: p.update({'is_alive': True, 'health': 100, 'armor': p.get('armor', 0)})
    
    if not skip_buy_phase:
        buy_weapons_for_team(temp_a, round_number)
        buy_weapons_for_team(temp_b, round_number)
    
    timeline = []
    
    round_attacker_id = 'team_a' if temp_a['side'] == 'attacker' else 'team_b'
    attacker_team = temp_a if round_attacker_id == 'team_a' else temp_b
    defender_team = temp_b if round_attacker_id == 'team_a' else temp_a
    
    map_sites_list = list(MAP_LOCATIONS.get(map_name, {}).keys())
    if not map_sites_list: map_sites_list = ["A_Site", "B_Site"]

    attack_target_site = random.choice(map_sites_list)
    lurk_site = None
    
    player_locations = {}
    
    attacker_players = [p for p in attacker_team['players'] if p['is_alive']]
    lurker = next((p for p in attacker_players if p['role'] == 'Sentinel'), None)
    
    if lurker and len(map_sites_list) > 1:
        lurk_site = random.choice([s for s in map_sites_list if s != attack_target_site])
        player_locations[lurker['name']] = lurk_site
        attacker_players.remove(lurker)
    
    for p in attacker_players:
        player_locations[p['name']] = attack_target_site

    defender_players = [p for p in defender_team['players'] if p['is_alive']]
    random.shuffle(defender_players)
    for i, p in enumerate(defender_players):
        site_index = i % len(map_sites_list)
        player_locations[p['name']] = map_sites_list[site_index]

    # Dicionário que guarda as coordenadas de cada jogador durante o round
    round_positions = {}
    
    # 1. POSICIONAMENTO INICIAL ESTRATÉGICO
    grouped_player_locations = {}
    all_players_with_loc = attacker_team['players'] + defender_team['players']
    for p in all_players_with_loc:
        if p['name'] in player_locations:
            site = player_locations[p['name']]
            if site not in grouped_player_locations:
                grouped_player_locations[site] = []
            grouped_player_locations[site].append(p)
            
    for site, players_on_site in grouped_player_locations.items():
        attackers_in_group = [p for p in players_on_site if any(att['name'] == p['name'] for att in attacker_team['players'])]
        defenders_in_group = [p for p in players_on_site if any(defe['name'] == p['name'] for defe in defender_team['players'])]

        site_data = MAP_LOCATIONS[map_name][site]
        generate_positions_for_group(attackers_in_group, site_data['attack_spawn'], 0.04, round_positions)
        generate_positions_for_group(defenders_in_group, site_data['center'], 0.04, round_positions)

    # 2. SIMULA O CONFRONTO NO BOMB PRINCIPAL (O PUSH)
    attackers_on_main_site = [p for p in attacker_team['players'] if p['is_alive'] and player_locations.get(p['name']) == attack_target_site]
    defenders_on_main_site = [p for p in defender_team['players'] if p['is_alive'] and player_locations.get(p['name']) == attack_target_site]
    
    # CRÍTICO: Move os atacantes para o "center" PARA O DUELO, garantindo que as mortes ocorram DENTRO do bomb
    for p in attackers_on_main_site:
        site_data = MAP_LOCATIONS[map_name][attack_target_site]
        round_positions[p['name']] = {
            'x': site_data['center']['x'] + (random.random() - 0.5) * 0.05,
            'y': site_data['center']['y'] + (random.random() - 0.5) * 0.05
        }
    
    surviving_attackers_main, surviving_defenders_main = _simulate_confrontation(attackers_on_main_site, defenders_on_main_site, timeline, temp_a, temp_b, round_positions)

    # 3. SIMULA O CONFRONTO DO LURKER (SE HOUVER)
    if lurk_site:
        lurkers = [p for p in attacker_team['players'] if p['is_alive'] and player_locations.get(p['name']) == lurk_site]
        defenders_on_lurk_site = [p for p in defender_team['players'] if p['is_alive'] and player_locations.get(p['name']) == lurk_site]
        if lurkers and defenders_on_lurk_site:
             _simulate_confrontation(lurkers, defenders_on_lurk_site, timeline, temp_a, temp_b, round_positions)
    
    # 4. FASE DE ADAPTAÇÃO (RETAKE OU ROTAÇÃO)
    entry_successful = len(surviving_attackers_main) > len(surviving_defenders_main)

    if entry_successful:
        surviving_attackers_total = [p for p in attacker_team['players'] if p['is_alive']]
        defenders_rotating = [p for p in defender_team['players'] if p['is_alive'] and player_locations.get(p['name']) != attack_target_site]
        
        if surviving_attackers_total and defenders_rotating:
            retake_coords = MAP_LOCATIONS[map_name][attack_target_site]['attack_spawn'] # Defensores vem de fora para o retake
            for p in defenders_rotating:
                round_positions[p['name']] = {'x': retake_coords['x'] + (random.random() - 0.5) * 0.05, 'y': retake_coords['y'] + (random.random() - 0.5) * 0.05}
            _simulate_confrontation(defenders_rotating, surviving_attackers_total, timeline, temp_a, temp_b, round_positions)
    else:
        alive_attackers_total = [p for p in attacker_team['players'] if p['is_alive']]
        if len(alive_attackers_total) >= 3 and len(map_sites_list) > 1:
            new_target_site = next(s for s in map_sites_list if s != attack_target_site)
            defenders_on_new_site = [p for p in defender_team['players'] if p['is_alive'] and player_locations.get(p['name']) == new_target_site]

            if alive_attackers_total and defenders_on_new_site:
                rotation_coords = MAP_LOCATIONS[map_name][new_target_site]['center'] # Na rotação, o confronto também é no centro
                for p in alive_attackers_total:
                    round_positions[p['name']] = {'x': rotation_coords['x'] + (random.random() - 0.5) * 0.05, 'y': rotation_coords['y'] + (random.random() - 0.5) * 0.05}
                _simulate_confrontation(alive_attackers_total, defenders_on_new_site, timeline, temp_a, temp_b, round_positions)

    winner = 'team_a' if sum(p['is_alive'] for p in temp_a['players']) > 0 else 'team_b'
    winner_team_orig, loser_team_orig = (team_a, team_b) if winner == 'team_a' else (team_b, team_a)
    
    winner_team_orig['score'] += 1
    winner_team_orig['loss_streak'] = 0
    loser_team_orig['loss_streak'] += 1
    loss_bonus = [1900, 2400, 2900]
    loss_reward = loss_bonus[min(loser_team_orig['loss_streak'] - 1, 2)]

    for p_orig, p_temp in zip(winner_team_orig['players'], temp_a['players'] if winner_team_orig['name'] == team_a['name'] else temp_b['players']): p_orig.update({'credits': min(MAX_CREDITS, p_temp['credits'] + WIN_REWARD), 'kills': p_temp['kills'], 'deaths': p_temp['deaths'], 'assists': p_temp['assists']})
    for p_orig, p_temp in zip(loser_team_orig['players'], temp_a['players'] if loser_team_orig['name'] == team_a['name'] else temp_b['players']): p_orig.update({'credits': min(MAX_CREDITS, p_temp['credits'] + loss_reward), 'kills': p_temp['kills'], 'deaths': p_temp['deaths'], 'assists': p_temp['assists']})
    
    return winner, timeline, copy.deepcopy(temp_a['players']), copy.deepcopy(temp_b['players'])


def simulate_single_game(team_a_data, team_b_data, map_name, is_replay=False):
    team_a, team_b = copy.deepcopy(team_a_data), copy.deepcopy(team_b_data)
    set_map_specific_agents(team_a, map_name)
    set_map_specific_agents(team_b, map_name)
    
    team_a['score'], team_b['score'] = 0, 0
    team_a['loss_streak'], team_b['loss_streak'] = 0, 0

    for p in team_a['players'] + team_b['players']: p.update({'credits': STARTING_CREDITS, 'weapon': find_weapon_by_id('classic'), 'kills': 0, 'deaths': 0, 'assists': 0, 'armor': 0})
    
    rounds_history = []
    sides = {'team_a': 'attacker', 'team_b': 'defender'}

    while team_a['score'] < 13 and team_b['score'] < 13:
        round_num = team_a['score'] + team_b['score'] + 1
        
        team_a['side'] = sides['team_a']
        team_b['side'] = sides['team_b']

        if round_num == 13:
            sides = {'team_a': 'defender', 'team_b': 'attacker'}
            for p in team_a['players'] + team_b['players']: p['credits'] = STARTING_CREDITS
            team_a['loss_streak'], team_b['loss_streak'] = 0, 0
        
        buy_weapons_for_team(team_a, round_num)
        buy_weapons_for_team(team_b, round_num)

        if is_replay:
            initial_players_a = copy.deepcopy(team_a['players'])
            initial_players_b = copy.deepcopy(team_b['players'])
            winner, timeline, _, _ = simulate_full_round(team_a, team_b, round_num, map_name, skip_buy_phase=True)
            
            rounds_history.append({
                'round_number': round_num, 'round_winner': winner, 'timeline': timeline,
                'initial_team_a': initial_players_a, 'initial_team_b': initial_players_b,
                'round_attacker': 'team_a' if sides['team_a'] == 'attacker' else 'team_b'
            })
        else:
            simulate_full_round(team_a, team_b, round_num, map_name, skip_buy_phase=True)

    final_score_str = f"{team_a['score']} - {team_b['score']}"
    winner_name = team_a['name'] if team_a['score'] > team_b['score'] else team_b['name']
    final_stats = {"team_a": [{"name": p['name'], "kills": p['kills'], "deaths": p['deaths'], "assists": p['assists']} for p in team_a['players']], "team_b": [{"name": p['name'], "kills": p['kills'], "deaths": p['deaths'], "assists": p['assists']} for p in team_b['players']]}
    
    return {
        "type": "replay" if is_replay else "single_match",
        "team_a": {"name": team_a['name'], "logo_url": team_a['logo_url'], "players": team_a_data['players']}, 
        "team_b": {"name": team_b['name'], "logo_url": team_b['logo_url'], "players": team_b_data['players']}, 
        "map": map_name, "final_score": final_score_str, "winner_name": winner_name, 
        "stats": final_stats, "rounds": rounds_history
    }

# --- Rotas Flask ---
@app.route('/')
def index(): return render_template('index.html', teams=TEAMS, maps=AVAILABLE_MAPS)
@app.route('/replay')
def replay(): return render_template('replay.html')
@app.route('/options')
def options(): return render_template('options.html')
@app.route('/results/match')
def match_results(): return render_template('match_results.html')
@app.route('/results/series')
def series_results(): return render_template('series_results.html')
@app.route('/api/teams')
def get_teams(): return jsonify(TEAMS)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    team_1_id, team_2_id = data.get('team_1'), data.get('team_2')
    mode, map_name, tournament = data.get('simulation_mode'), data.get('map'), data.get('tournament')
    team_a_data, team_b_data = TEAMS.get(team_1_id), TEAMS.get(team_2_id)
    if not team_a_data or not team_b_data: return jsonify({"error": "Team not found"}), 404
    
    if mode == 'series':
        games_to_win = 3 if tournament in ['vct', 'masters'] else 2
        results = simulate_series(team_a_data, team_b_data, AVAILABLE_MAPS, games_to_win)
    else:
        results = simulate_single_game(team_a_data, team_b_data, map_name, is_replay=(mode == 'replay'))
    
    return jsonify(results)

def simulate_series(team_a_data, team_b_data, available_maps, games_to_win):
    team_a_series_wins, team_b_series_wins = 0, 0
    games_played = []
    
    num_maps_needed = games_to_win * 2 - 1
    maps_to_play = random.sample(available_maps, k=min(len(available_maps), num_maps_needed))

    for map_name in maps_to_play:
        if team_a_series_wins >= games_to_win or team_b_series_wins >= games_to_win:
            break

        game_result = simulate_single_game(copy.deepcopy(team_a_data), copy.deepcopy(team_b_data), map_name, is_replay=False)
        
        if game_result['winner_name'] == team_a_data['name']:
            team_a_series_wins += 1
        else:
            team_b_series_wins += 1
        
        games_played.append({ "map": map_name, "final_score": game_result['final_score'], "winner_name": game_result['winner_name'] })

    series_winner_name = team_a_data['name'] if team_a_series_wins > team_b_series_wins else team_b_data['name']
    
    return {
        "type": "series_results", "series_winner": series_winner_name,
        "series_score": f"{team_a_series_wins} - {team_b_series_wins}",
        "games": games_played,
        "team_a": {"name": team_a_data['name'], "logo_url": team_a_data['logo_url']},
        "team_b": {"name": team_b_data['name'], "logo_url": team_b_data['logo_url']}
    }




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)