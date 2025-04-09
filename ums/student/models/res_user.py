from odoo import models, fields, api, _


class ResUser(models.Model):
    _inherit = 'res.users'

    collage_ids = fields.Many2many('ums.college', string='Collage')
