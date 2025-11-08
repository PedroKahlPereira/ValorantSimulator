# Arquivo: map_data.py

MAPS_DATA = {
    'Ascent': {
        'positions': {
            'attacker_spawn': {'x': 50, 'y': 950},
            'a_main': {'x': 450, 'y': 700},
            'a_site': {'x': 400, 'y': 400},
            'a_heaven': {'x': 420, 'y': 200},
            'mid_market': {'x': 500, 'y': 500},
            'defender_spawn': {'x': 950, 'y': 50},
            'b_site': {'x': 800, 'y': 450},
            'b_main': {'x': 850, 'y': 750},
        },
        'paths': [
            ('attacker_spawn', 'a_main'),
            ('attacker_spawn', 'b_main'),
            ('a_main', 'a_site'),
            ('a_site', 'a_heaven'),
            ('a_site', 'mid_market'),
            ('mid_market', 'defender_spawn'),
            ('b_main', 'b_site'),
            ('b_site', 'defender_spawn'),
        ]
    }
    # (No futuro, adicionaremos outros mapas como Bind, Haven, etc. aqui)
}