# -*- coding: utf-8 -*-
import io
import copy
import random
import requests
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, send_file

# --- CONFIGURAÇÃO INICIAL DO FLASK ---
app = Flask(__name__)

# --- MODELO DE DADOS (ARMAS E TIMES) ---

WEAPONS = [
    {'id': 'classic', 'name': 'Classic', 'cost': 0, 'type': 'Sidearm', 'damage': {'short': 78, 'medium': 66, 'long': 66}},
    {'id': 'shorty', 'name': 'Shorty', 'cost': 150, 'type': 'Sidearm', 'damage': {'short': 36, 'medium': 12, 'long': 9}},
    {'id': 'ghost', 'name': 'Ghost', 'cost': 500, 'type': 'Sidearm', 'damage': {'short': 105, 'medium': 88, 'long': 88}},
    {'id': 'spectre', 'name': 'Spectre', 'cost': 1600, 'type': 'SMG', 'damage': {'short': 78, 'medium': 66, 'long': 66}},
    {'id': 'bulldog', 'name': 'Bulldog', 'cost': 2050, 'type': 'Rifle', 'damage': {'short': 115, 'medium': 115, 'long': 115}},
    {'id': 'guardian', 'name': 'Guardian', 'cost': 2250, 'type': 'Rifle', 'damage': {'short': 195, 'medium': 195, 'long': 195}},
    {'id': 'phantom', 'name': 'Phantom', 'cost': 2900, 'type': 'Rifle', 'damage': {'short': 156, 'medium': 140, 'long': 124}},
    {'id': 'vandal', 'name': 'Vandal', 'cost': 2900, 'type': 'Rifle', 'damage': {'short': 160, 'medium': 160, 'long': 160}},
    {'id': 'operator', 'name': 'Operator', 'cost': 4700, 'type': 'Sniper', 'damage': {'short': 255, 'medium': 255, 'long': 255}},
]

TEAMS_DATA = {
    '1': {
        'id': 'acend2021', 'name': 'Acend 2021',
        'players': [
            {'id': 'p1', 'name': 'cNed', 'role': 'Duelist', 'img_url': 'https://owcdn.net/img/65dbc5cfc3b28.png', 'attributes': {'aim': 95, 'hs': 40, 'cl': 85, 'movement': 80, 'aggression': 95, 'support': 70}},
            {'id': 'p2', 'name': 'Starxo', 'role': 'Initiator', 'img_url': 'https://www.prosettings.gg/wp-content/uploads/2021/09/starxo-valorant-player-profile-picture-new.webp', 'attributes': {'aim': 80, 'hs': 25, 'cl': 75, 'movement': 85, 'aggression': 80, 'support': 85}},
            {'id': 'p3', 'name': 'zeek', 'role': 'Flex', 'img_url': 'https://owcdn.net/img/68644db3bfd7d.png', 'attributes': {'aim': 82, 'hs': 28, 'cl': 70, 'movement': 82, 'aggression': 85, 'support': 80}},
            {'id': 'p4', 'name': 'Kiles', 'role': 'Sentinel', 'img_url': 'https://owcdn.net/img/61c21625d9701.png', 'attributes': {'aim': 75, 'hs': 20, 'cl': 70, 'movement': 78, 'aggression': 70, 'support': 90}},
            {'id': 'p5', 'name': 'BONECOLD', 'role': 'Controller', 'img_url': 'https://liquipedia.net/commons/images/thumb/c/c6/Acend_BONECOLD.png/237px-Acend_BONECOLD.png', 'attributes': {'aim': 78, 'hs': 22, 'cl': 75, 'movement': 75, 'aggression': 75, 'support': 95}},
        ]
    },
    '2': {
        'id': 'loud2022', 'name': 'LOUD 2022',
        'players': [
            {'id': 'p6', 'name': 'Less', 'role': 'Sentinel', 'img_url': 'https://owcdn.net/img/677d651a8a520.png', 'attributes': {'aim': 88, 'hs': 30, 'cl': 85, 'movement': 85, 'aggression': 80, 'support': 90}},
            {'id': 'p7', 'name': 'Aspas', 'role': 'Duelist', 'img_url': 'https://i.imgur.com/CvT4ISK.webp', 'attributes': {'aim': 98, 'hs': 45, 'cl': 80, 'movement': 88, 'aggression': 98, 'support': 75}},
            {'id': 'p8', 'name': 'Sadhak', 'role': 'Flex', 'img_url': 'https://owcdn.net/img/66306e037e53b.png', 'attributes': {'aim': 85, 'hs': 28, 'cl': 95, 'movement': 80, 'aggression': 85, 'support': 100}},
            {'id': 'p9', 'name': 'Sacy', 'role': 'Initiator', 'img_url': 'https://static.valorantzone.gg/news/2022/09/18195828/52367462016_f823cda6d8_k.jpg', 'attributes': {'aim': 87, 'hs': 25, 'cl': 90, 'movement': 82, 'aggression': 80, 'support': 95}},
            {'id': 'p10', 'name': 'Pancada', 'role': 'Controller', 'img_url': 'https://i.imgur.com/kY3yAGy.png', 'attributes': {'aim': 90, 'hs': 35, 'cl': 100, 'movement': 78, 'aggression': 70, 'support': 90}},
        ]
    }
}

# --- LÓGICA DE SIMULAÇÃO ---
# (Seu código de simulação, bem estruturado)

WIN_REWARD = 3000
LOSS_REWARD = 1900
STARTING_CREDITS = 800
MAX_CREDITS = 9000

def find_weapon_by_id(weapon_id):
    """Encontra uma arma na lista WEAPONS pelo seu ID."""
    return next((w for w in WEAPONS if w['id'] == weapon_id), None)

def determine_economy_type(average_credits):
    if average_credits < 2000: return 'Full Eco'
    if average_credits < 3900: return 'Semi Buy'
    return 'Full Buy'

def buy_weapons_for_team(team):
    # (Sua lógica de compra de armas aqui)
    pass

def calculate_combat_score(player, opponent, is_clutch, alive_teammates):
    # (Sua lógica de cálculo de combate aqui)
    return random.randint(50, 150) # Placeholder

def apply_round_results(team_a, team_b, winner):
    # (Sua lógica para aplicar resultados do round aqui)
    pass

def simulate_full_round(team_a, team_b):
    # (Sua lógica completa de simulação de round aqui)
    kill_feed = ["Simulação de kill feed"]
    winner = random.choice(['teamA', 'teamB'])
    team_a_weapons = [p.get('weapon', {}).get('name', 'Classic') for p in team_a['players']]
    team_b_weapons = [p.get('weapon', {}).get('name', 'Classic') for p in team_b['players']]

    # Atualiza scores e créditos (simulação simplificada)
    if winner == 'teamA':
        team_a['score'] += 1
    else:
        team_b['score'] += 1
        
    return winner, kill_feed, team_a_weapons, team_b_weapons

# --- ROTAS DA APLICAÇÃO (ENDPOINTS) ---

@app.route('/proxy-image')
def proxy_image():
    """
    Busca uma imagem de uma URL externa, agindo como um proxy para evitar
    problemas de CORS ou hotlinking (Erro 403).
    """
    url = request.args.get('url')
    if not url:
        return 'URL da imagem não foi fornecida', 400

    try:
        parsed_url = urlparse(url)
        referer = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': referer
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        return send_file(
            io.BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.exceptions.RequestException as e:
        print(f"PROXY ERROR: Falha ao buscar a imagem {url}. Erro: {e}")
        return 'Imagem não pôde ser carregada pelo servidor', 500

@app.route('/api/teams')
def get_teams_data():
    """Fornece os dados dos times em formato JSON para o frontend."""
    return jsonify(TEAMS_DATA)

@app.route('/')
def main_page():
    """Renderiza a página HTML principal."""
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    """Recebe a seleção de times e retorna o resultado da simulação."""
    data = request.get_json()
    team1_key = str(data.get('team_1'))
    team2_key = str(data.get('team_2'))

    if not all([team1_key, team2_key]) or team1_key not in TEAMS_DATA or team2_key not in TEAMS_DATA or team1_key == team2_key:
        return jsonify({'error': 'Seleção de times inválida.'}), 400

    team_a = copy.deepcopy(TEAMS_DATA[team1_key])
    team_b = copy.deepcopy(TEAMS_DATA[team2_key])

    # Inicializa o estado do jogo
    team_a['score'] = 0
    team_b['score'] = 0
    for p in team_a['players'] + team_b['players']:
        p.update({'credits': STARTING_CREDITS, 'weapon': find_weapon_by_id('classic'), 'is_alive': True, 'kills': 0, 'deaths': 0})

    round_history = []
    
    while team_a['score'] < 13 and team_b['score'] < 13:
        # A lógica de simulação completa iria aqui. Usando uma versão simplificada por enquanto.
        winner, kill_feed, team_a_weapons, team_b_weapons = simulate_full_round(team_a, team_b)
        
        round_history.append({
            'round_number': len(round_history) + 1,
            'winner': 'teamA' if winner == 'teamA' else 'teamB',
            'kill_feed': kill_feed,
            'score': f"{team_a['score']} - {team_b['score']}"
        })

    final_winner = team_a['name'] if team_a['score'] > team_b['score'] else team_b['name']
    
    return jsonify({
        'team_1_name': team_a['name'],
        'team_2_name': team_b['name'],
        'final_score': [team_a['score'], team_b['score']],
        'winner_name': final_winner,
        'round_history': round_history,
        'team_1_stats': [{'name': p['name'], 'kills': p['kills'], 'deaths': p['deaths']} for p in team_a['players']],
        'team_2_stats': [{'name': p['name'], 'kills': p['kills'], 'deaths': p['deaths']} for p in team_b['players']],
    })

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)