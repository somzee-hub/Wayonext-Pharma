{
    'name': 'WayoNext Pharmaceuticals Demo Database',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Loads a WayoNext Pharmaceuticals demo: brands, third-party manufacturers, stockists, batches with expiry, purchase-to-sale cycle',
    'description': """
Demo data loader prepared by Ochre Digital for the WayoNext Pharmaceuticals Odoo 19 demo.

WayoNext owns the brands (Wayoprime and Wayomax divisions), buys finished goods from
third-party manufacturers and sells to stockists across India.

Install on a FRESH Odoo 19 database (no demo data, company country India).
All partner names, GSTINs, drug licence numbers and prices are fictitious demo values,
except the WayoNext company profile and product catalogue, which come from wayonext.com.
""",
    'author': 'Ochre Digital',
    'website': 'https://ochre.digital',
    'depends': [
        'contacts',
        'crm',
        'sale_management',
        'sale_stock',
        'purchase_stock',
        'stock_account',
        'product_expiry',
        'l10n_in',
        'hr',
    ],
    'data': [
        'views/product_views.xml',
        'views/res_partner_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
