from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from dateutil import relativedelta


class StudentLetter(models.Model):
    _name = 'ums.letter.degree'
    _description = "Letter Degree"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', tracking=True)    
    english_name = fields.Char(string='English Name', tracking=True)
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    maximum_marks = fields.Integer("Maximum marks", required=True, help='Maximum marks of the subject can get')
    minimum_marks = fields.Integer("Minimum marks", required=True, help='''Required minimum
        marks of the subject''')
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}

    