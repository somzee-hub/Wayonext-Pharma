from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wn_partner_type = fields.Selection(
        [
            ('stockist', 'Stockist / Distributor'),
            ('manufacturer', 'Third-Party Manufacturer'),
            ('institution', 'Hospital / Institution'),
            ('retail', 'Retail (B2C)'),
        ],
        string='Trade Type',
    )
    wn_drug_licence = fields.Char(string='Drug Licence No. (20B / 21B)')
    wn_drug_licence_valid_till = fields.Date(string='Drug Licence Valid Till')
    wn_fssai = fields.Char(string='FSSAI Licence No.')
