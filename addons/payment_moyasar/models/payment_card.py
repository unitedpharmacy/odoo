import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class PaymentCard(models.Model):
    _name = 'payment.card'
    _description = 'Payment Card'
    
    name = fields.Char(string="Name", required=True)
    number = fields.Char(string="Number", required=True)
    year = fields.Char(string="Year")
    month = fields.Char(string="Month")
    partner_id = fields.Many2one(string="Partner", comodel_name='res.partner', required=True)
    

