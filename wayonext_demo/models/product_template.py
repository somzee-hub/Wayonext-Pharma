from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wn_composition = fields.Text(string='Composition')
    wn_indication = fields.Text(string='Indication')
    wn_dosage_form = fields.Selection(
        [
            ('tablet', 'Tablet'),
            ('capsule', 'Capsule'),
            ('softgel', 'Soft Gelatin Capsule'),
            ('sachet', 'Sachet'),
            ('powder', 'Powder'),
            ('infusion', 'Infusion'),
        ],
        string='Dosage Form',
    )
    wn_pack_size = fields.Char(string='Pack Size', help="e.g. 10 tablets per strip")
    wn_schedule = fields.Selection(
        [
            ('h', 'Schedule H (Rx)'),
            ('h1', 'Schedule H1 (Rx, register)'),
            ('nutra', 'Nutraceutical (FSSAI)'),
        ],
        string='Drug Schedule',
    )
    wn_mrp = fields.Float(string='MRP (per pack, incl. GST)', digits='Product Price')
    wn_ptr = fields.Float(string='PTR (Price to Retailer)', digits='Product Price')
