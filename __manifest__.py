{
    'name': 'Generate BOM Variants',
    'version': '1.0',
    'summary': 'Generate BOM for Product Variants',
    'description': """
        This module is designed to provide functionality for generating Bill of Materials
        for product variants based on specified attributes and values.
    """,
    'author': 'Pradhap',
    'license': 'LGPL-3',
    'website': 'https://www.processdrive.com',
    'category': 'Manufacturing/MRP',
    'depends': ['product', 'mrp', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_generate_variants_button.xml',
        # XML and CSV files will be added here later
    ],
    'installable': True,
    'application': True,
}