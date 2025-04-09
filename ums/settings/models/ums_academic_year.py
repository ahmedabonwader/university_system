from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class AcademicYear(models.Model):
    _name = "ums.academic.year"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Academic Year"

    name = fields.Char('Name', required=True, help='Name of academic year', tracking=True)
    english_name = fields.Char('English Name', required=False, help='Name of academic year', tracking=True)
    code = fields.Char('Code', help='Code of academic year', tracking=True)
    start_date = fields.Date('Start Date', required=False, tracking=True,
                             help='Starting date of academic year')
    end_date = fields.Date('End Date', required=False, tracking=True)
    description = fields.Text('Description', help='Description', tracking=True)
    academic_active = fields.Boolean(string="Active", default=True, tracking=True)
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
