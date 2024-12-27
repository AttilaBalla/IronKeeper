from enum import Enum

class Territories(Enum):
    Neutral = 0
    BCU = 2
    ANI = 4
    Both = 6

admins = ['xattus']

bosses = [
    {
        "name": 'Hornian Queen',
        "key": 'hq',
        "time": 120,
        "map": Territories.Neutral
    },
    {
        "name": 'Hornian King',
        "key": 'hk',
        "time": 120,
        "map": Territories.Neutral
    },
    {
        "name": 'Pathos',
        "key": 'pathos',
        "time": 120,
        "map": Territories.BCU
    },
    {
        "name": 'Prog. Military Base',
        "key": 'mbase',
        "time": 120,
        "map": Territories.BCU
    },
    {
        "name": 'Nipar Bridge',
        "key": 'nipar',
        "time": 120,
        "map": Territories.BCU
    },
    {
        "name": 'Quetzalcoatl',
        "key": 'quetz',
        "time": 120,
        "map": Territories.Both
    },
    {
        "name": 'Gryphon',
        "key": 'gryph',
        "time": 120,
        "map": Territories.Both
    },
    {
        "name": 'Rock Emperor',
        "key": 're',
        "time": 180,
        "map": Territories.Neutral
    },
    {
        "name": 'Shrine',
        "key": 'shrine',
        "time": 120,
        "map": Territories.ANI
    },
    {
        "name": 'Energy Core',
        "key": 'core',
        "time": 120,
        "map": Territories.ANI
    },
    {
        "name": 'Skadi',
        "key": 'skadi',
        "time": 180,
        "map": Territories.Neutral
    },
    {
        "name": 'Bishop Blue',
        "key": 'bishopl',
        "time": 360,
        "map": Territories.Neutral
    },
    {
        "name": 'Bishop Black',
        "key": 'bishopb',
        "time": 360,
        "map": Territories.Neutral
    },
    {
        "name": 'Bishop Red',
        "key": 'bishopr',
        "time": 360,
        "map": Territories.Neutral
    },
    {
        "name": 'Mountain Sage',
        "key": 'sage',
        "time": 720,
        "map": Territories.BCU
    },
    {
        "name": 'Skarish',
        "key": 'skar',
        "time": 720,
        "map": Territories.BCU
    },
    {
        "name": 'Fx-01',
        "key": 'fx',
        "time": 720,
        "map": Territories.Neutral
    },
    {
        "name": 'Messenger',
        "key": 'messenger',
        "time": 720,
        "map": Territories.ANI
    },
    {
        "name": 'Egma Schill',
        "key": 'es',
        "time": 720,
        "map": Territories.Neutral
    },
    {
        "name": 'Ordin',
        "key": 'ordin',
        "time": 720,
        "map": Territories.Neutral
    },
    {
        "name": 'Gigantic God',
        "key": 'gg',
        "time": 480,
        "map": Territories.Neutral
    },
    {
        "name": 'Sekhmete',
        "key": 'sekh',
        "time": 1440,
        "map": Territories.Neutral
    },
    {
        "name": 'Guardian of Vatallus',
        "key": 'gov',
        "time": 1080,
        "map": Territories.Neutral
    },
    {
        "name": 'Black Widow',
        "key": 'bw',
        "time": 1080,
        "map": Territories.Both
    },
    {
        "name": 'Echelon',
        "key": 'eche',
        "time": 1080,
        "map": Territories.Both
    },
    {
        "name": 'Murena',
        "key": 'mur',
        "time": 720,
        "map": Territories.ANI
    },
    {
        "name": 'Invasion Lead Spider',
        "key": 'ils',
        "time": 1440,
        "map": Territories.Neutral
    },
{
        "name": 'test',
        "key": 'test',
        "time": 1,
        "map": Territories.Both
    },
]

