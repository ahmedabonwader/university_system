from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


# need work
class Semester(models.Model):
    _name = "ums.semester"
    _description = "Semester"

    name = fields.Char('Name', required=True, help='Name')
    english_name = fields.Char('English Name', help='English Name')
    description = fields.Text('Description', help='Description')
    sequence = fields.Integer(string='Sequence')
    # specialize_id = fields.Many2one('college.specialize', string="Specialize Name")
    # subject_id = fields.One2many('subject.subject.line', 'semester_id',string="Subject")
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
