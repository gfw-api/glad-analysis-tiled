"""-"""

import os

SETTINGS = {
    'logging': {
        'level': 'DEBUG'
    },
    'service': {
        'port': os.getenv('PORT'),
        'name': 'Glad Analysis Tiled'
    }
}
