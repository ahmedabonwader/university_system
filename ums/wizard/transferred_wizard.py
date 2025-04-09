import datetime
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date

class TransferreddWizard(models.TransientModel):
    _name = "transferred.wizard"
    _description = "Transferred Wizard"
    
    def default_get(self, fields):
        res = super(TransferreddWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['student'] = self.env.context.get('active_id')
        return res
    
    student = fields.Many2one('ums.student', string="Student Name")
    college_id = fields.Many2one(related="student.college_id", string="College")
    department = fields.Many2one(related="student.department", string="Department")
    program = fields.Many2one(related='student.program', string='Program')
    specialist_id = fields.Many2one(related='student.specialist_id', string="Specialist")
    transferred_lins_ids = fields.One2many('transferred.line', 'transferred_id', string="Transferred Line") 
    
    def action_transferred(self):
        for rec in self:
            vals = {
                'student':rec.student.id,
                'college_id':rec.college_id.id,
                'department':rec.department.id,
                'program':rec.program.id,
                'specialist_id':rec.specialist_id.id,
            }
            res = self.env['ums.transferred'].create(vals)
            line_vals = {
                'transfer_id':res.id,
                'semester_id':rec.transferred_lins_ids.semester_id.id,
                'subject':rec.transferred_lins_ids.subject.ids,
                'level':rec.transferred_lins_ids.level.id,
            }
            line = self.env['ums.transfer.line'].create(line_vals)
            rec.student.state = 'study'
    
    
class TransferredLine(models.TransientModel):
    _name = "transferred.line"
    _description = "Transferred Line"
    
    transferred_id = fields.Many2one('transferred.wizard')
    semester_id = fields.Many2one('ums.semester', string="Semester")
    subject = fields.Many2many('ums.subject', string="Subject")
    level = fields.Many2one("ums.level", string="Level")
    program = fields.Many2one(related='transferred_id.program', string='Program')
    
    @api.onchange('program')
    def onchange_level(self):
        if self.program:
            domain = []
            program = self.program.level_line
            for items in program:
                domain.append(items.level.id)
            return {'domain': {'level': [('id', 'in', domain)]}}
        
    @api.onchange('level')
    def onchange_semester_id(self):
        if self.level:
            vals = []
            domain = []
            program = self.program.level_line
            for items in program:
                vals.append(items.level.id)
                if self.level.id == items.level.id:
                    for rec in items.semester_line:
                        for t in rec.semester_id:
                            domain.append(t.id)
            return {'domain': {'semester_id': [('id', 'in', domain)]}}

    @api.onchange('semester_id')
    def onchange_subject(self):
        if self.semester_id:
            vals = []
            domain = []
            program = self.program.level_line
            for item in program:
                for rec in item.semester_line:
                    if self.semester_id == rec.semester_id:
                        for t in rec.subject_line:
                            domain.append(t.subject.id)
            return {'domain': {'subject': [('id', 'in', domain)]}}

                    