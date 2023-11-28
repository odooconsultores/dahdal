# -*- coding: utf-8 -*-

{
	'name': 'Proandsys - Dahdal',
	'version': '1',
	'author': '[Proandsys]',
	'website': 'http://www.odooconsultores.cl',
	'license': 'AGPL-3',
	'category': 'Localization',
	'summary': 'Ajustes Dahdal',
	'description': 
"""

""",
	'depends': ['base', 'proandsys_report_14', 'product', 'website_sale', 'web', 'stock_fefo'],
	'data': [
		'views/product_views.xml',
		'views/website_templates.xml',
		'views/res_country_views.xml',
		'views/webclient_templates.xml',
		'views/pos_invoice_report.xml',
	],
	'installable': True,	
}
