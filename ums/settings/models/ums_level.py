from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta

class Level(models.Model):
    _name = "ums.level"
    _description = "Level"

    name = fields.Char('Name', required=True, help='Name of level')
    english_name = fields.Char('English Name', required=False, help='Name of level')
    sequence = fields.Integer(string='Sequence')
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
