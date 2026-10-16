from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        today = fields.Date.context_today(self)
        for order in self:
            partner = order.partner_id.commercial_partner_id
            if partner.wn_partner_type in ('stockist', 'institution'):
                if not partner.wn_drug_licence:
                    raise UserError(self.env._(
                        "%(partner)s has no drug licence on record. "
                        "Add the licence number before confirming this order.",
                        partner=partner.display_name,
                    ))
                valid_till = partner.wn_drug_licence_valid_till
                if valid_till and valid_till < today:
                    raise UserError(self.env._(
                        "Drug licence %(dl)s of %(partner)s expired on %(date)s. "
                        "Sales to this party are blocked until a renewed licence is recorded.",
                        dl=partner.wn_drug_licence,
                        partner=partner.display_name,
                        date=valid_till,
                    ))
        return super().action_confirm()
