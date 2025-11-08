# weapons.py

WEAPONS = [
    # Sidearms
    {
        'id': 'classic', 'name': 'Classic', 'type': 'Sidearm', 'cost': 0,
        'damage_body': 26, 'headshot_multiplier': 3
    },
    {
        'id': 'shorty', 'name': 'Shorty', 'type': 'Sidearm', 'cost': 150,
        'damage_body': 12, 'headshot_multiplier': 2 # Por bala
    },
    {
        'id': 'frenzy', 'name': 'Frenzy', 'type': 'Sidearm', 'cost': 450,
        'damage_body': 26, 'headshot_multiplier': 3.1
    },
    {
        'id': 'ghost', 'name': 'Ghost', 'type': 'Sidearm', 'cost': 500,
        'damage_body': 30, 'headshot_multiplier': 3.1
    },
    {
        'id': 'sheriff', 'name': 'Sheriff', 'type': 'Sidearm', 'cost': 800,
        'damage_body': 55, 'headshot_multiplier': 2.5
    },
    # SMGs
    {
        'id': 'stinger', 'name': 'Stinger', 'type': 'SMG', 'cost': 1100,
        'damage_body': 27, 'headshot_multiplier': 2.5
    },
    {
        'id': 'spectre', 'name': 'Spectre', 'type': 'SMG', 'cost': 1600,
        'damage_body': 26, 'headshot_multiplier': 3
    },
    # Shotguns
    {
        'id': 'bucky', 'name': 'Bucky', 'type': 'Shotgun', 'cost': 850,
        'damage_body': 20, 'headshot_multiplier': 2 # Por bala
    },
    {
        'id': 'judge', 'name': 'Judge', 'type': 'Shotgun', 'cost': 1850,
        'damage_body': 17, 'headshot_multiplier': 2 # Por bala
    },
    # Rifles
    {
        'id': 'bulldog', 'name': 'Bulldog', 'type': 'Rifle', 'cost': 2050,
        'damage_body': 35, 'headshot_multiplier': 3.1
    },
    {
        'id': 'guardian', 'name': 'Guardian', 'type': 'Rifle', 'cost': 2250,
        'damage_body': 65, 'headshot_multiplier': 2.5
    },
    {
        'id': 'phantom', 'name': 'Phantom', 'type': 'Rifle', 'cost': 2900,
        'damage_body': 39, 'headshot_multiplier': 3.1
    },
    {
        'id': 'vandal', 'name': 'Vandal', 'type': 'Rifle', 'cost': 2900,
        'damage_body': 40, 'headshot_multiplier': 4
    },
    # Snipers
    {
        'id': 'marshal', 'name': 'Marshal', 'type': 'Sniper', 'cost': 950,
        'damage_body': 101, 'headshot_multiplier': 2
    },
    {
        'id': 'operator', 'name': 'Operator', 'type': 'Sniper', 'cost': 4700,
        'damage_body': 150, 'headshot_multiplier': 2.5
    },
    # Heavies
    {
        'id': 'ares', 'name': 'Ares', 'type': 'Heavy', 'cost': 1600,
        'damage_body': 30, 'headshot_multiplier': 2.5
    },
    {
        'id': 'odin', 'name': 'Odin', 'type': 'Heavy', 'cost': 3200,
        'damage_body': 38, 'headshot_multiplier': 2.5
    }
]