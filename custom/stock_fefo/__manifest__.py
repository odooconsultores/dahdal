# -*- coding: utf-8 -*-
{
    'name': 'Stock FEFO',
    'version': '14.0',
    'author': 'Clara Savelli <clara.15is.cs@gmail.com',
    'license': 'AGPL-3',
    'depends': ['stock', 'point_of_sale', 'product_expiry'],
    'data': [
        'views/pos_config.xml',
        'views/product_views.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
