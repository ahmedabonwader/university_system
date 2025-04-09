from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class Department(models.Model):
    _name = 'ums.department'
    _description = 'College Department'

    name = fields.Char('Name', required=True, help='Subject name')
    english_name = fields.Char('English Name', required=False, help='Subject name')

    college_id = fields.Many2one('ums.college', required=True,string="College Name")

    
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}