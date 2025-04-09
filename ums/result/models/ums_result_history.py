from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from dateutil import relativedelta


class StudentResultHistory(models.Model):
    _name = 'ums.result.history'
    _description = "Students Result History"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('ums.student', string="Student Name")
    result_id = fields.Many2one('ums.result', 'Result')
    collage_id = fields.Many2one('ums.college', 'Collage')
    department_id = fields.Many2one('ums.department', 'Department')
    program_id = fields.Many2one('ums.program', 'Program')
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", tracking=True)
    class_id = fields.Many2one('ums.class', 'Class')
    level_id = fields.Many2one('ums.level', 'Level')
    academic_year_id = fields.Many2one('ums.academic.year', 'Academic Year')
    date = fields.Date(string="Date")
    firest_semstar = fields.Many2one('ums.semester', 'First Semstar')
    second_semstar = fields.Many2one('ums.semester', 'Second Semstar')
    line_first_ids = fields.One2many(string='First line', comodel_name='first.result.history.line',
                                     inverse_name='history_id')
    line_second_ids = fields.One2many(string='Second line', comodel_name='second.result.history.line',
                                      inverse_name='history_id')
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)

    @api.onchange('collage_id')
    def onchange_is_department(self):
        for rec in self:
            if rec.collage_id.department == True:
                rec.is_department = True
            else:
                rec.is_department = False

    @api.onchange('collage_id')
    def onchange_is_specialist(self):
        for rec in self:
            if rec.collage_id.specialist == True:
                rec.is_specialist = True
            else:
                rec.is_specialist = False


class FirstResultHistoryLine(models.Model):
    _name = 'first.result.history.line'
    _description = 'First Histroy Line'

    history_id = fields.Many2one('ums.result.history', 'History')
    student = fields.Many2one("ums.student", string="Student")
    degree = fields.Char("Degree")
    note = fields.Text("Note")
    subject_id = fields.Many2one('ums.subject', 'Subject')
    hours = fields.Char("Hours")
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")


class SecondResultHistoryLine(models.Model):
    _name = 'second.result.history.line'
    _description = 'Second Histroy Line'

    history_id = fields.Many2one('ums.result.history', 'History')
    student = fields.Many2one("ums.student", string="Student")
    degree = fields.Char("Degree")
    hours = fields.Char("Hours")
    note = fields.Text("Note")
    subject_id = fields.Many2one('ums.subject', 'Subject')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")
