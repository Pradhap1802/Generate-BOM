{
    'name': 'Dynamic BoM',
    'version': '1.0',
    'summary': 'Create dynamic bill of materials',
    'description': 'This module allows you to create dynamic bill of materials from sale orders.',
    'author': 'Pradhap',
    'license': 'LGPL-3',
    'website': 'https://www.processdrive.com',
    'category': 'Sales',
    'depends': ['sale_management', 'mrp'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/mrp_bom_views.xml',
        # 'views/sale_order_status_views.xml',
    ],
    'installable': True,
    'application': True,
}