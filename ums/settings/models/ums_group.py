# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields


class Group(models.Model):
    _name = "ums.group"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _description = "Groups"

    name = fields.Char(string="Name", required=True)
    english_name = fields.Char(string="English Name", required=True)
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
