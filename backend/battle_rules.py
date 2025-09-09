def get_battle_rules():
    return {
        'type_effectiveness': {
            'Normal': {'Rock': 0.5, 'Ghost': 0, 'Steel': 0.5},
            'Fire': {
                'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 2,
                'Bug': 2, 'Rock': 0.5, 'Dragon': 0.5, 'Steel': 2
            },
            'Water': {
                'Fire': 2, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2,
                'Rock': 2, 'Dragon': 0.5
            },
            'Electric': {
                'Water': 2, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0,
                'Flying': 2, 'Dragon': 0.5
            },
            'Grass': {
                'Fire': 0.5, 'Water': 2, 'Grass': 0.5, 'Poison': 0.5,
                'Ground': 2, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2,
                'Dragon': 0.5, 'Steel': 0.5
            }
        },
        'battle_mechanics': {
            'critical_hit_chance': 0.0625,
            'critical_multiplier': 2,
            'stab_bonus': 1.5,
            'max_turns': 20
        }
    }