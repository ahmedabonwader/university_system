from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from dateutil import relativedelta


class Student(models.Model):
    _name = 'ums.nationality'
    _description = "Student Nationality"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', tracking=True)    
    english_name = fields.Char(string='English Name', tracking=True)
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}

    