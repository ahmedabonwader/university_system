# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime


class Supplement(models.Model):
    _name = "ums.supplement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Supplement"

    name = fields.Many2one('ums.student', 'Student Name')
    exam_name = fields.Char(string="Exam Name")
    class_id = fields.Many2one('ums.class', 'Class', required=True, tracking=True)
    program_id = fields.Many2one(related='result_id.program', string='Program')
    level_id = fields.Many2one(related='result_id.level', string='Level')
    academic_year = fields.Many2one(related='result_id.academic_year', string='Academic Year', required=True,
                                    tracking=True)
    college_id = fields.Many2one('ums.college', string="College", required=True, tracking=True)
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", tracking=True)
    supplement_ids = fields.One2many('first.supplement.line', 'supplement_id', 'Line')
    supplement_second_ids = fields.One2many('second.supplement.line', 'supplement_id', 'Line')
    date = fields.Date(string='Date')
    department = fields.Many2one("ums.department", string="Department")
    firest_semstar = fields.Many2one('ums.semester', 'First Semstar')
    second_semstar = fields.Many2one('ums.semester', 'Second Semstar')
    result_id = fields.Many2one('ums.result', 'Result')
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)

    @api.onchange('college_id')
    def onchange_is_department(self):
        for rec in self:
            if rec.college_id.department == True:
                rec.is_department = True
            else:
                rec.is_department = False

    @api.onchange('college_id')
    def onchange_is_specialist(self):
        for rec in self:
            if rec.college_id.specialist == True:
                rec.is_specialist = True
            else:
                rec.is_specialist = False

    @api.onchange('college_id')
    def onchange_college_id(self):
        for rec in self:
            return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}

    @api.onchange('specialist_id')
    def onchange_specialist_id(self):
        for rec in self:
            return {'domain': {'class_id': [('specialist_id', '=', rec.specialist_id.id)]}}


class FirstSupplementLine(models.Model):
    _name = 'first.supplement.line'
    _description = 'First Supplement Line'

    supplement_id = fields.Many2one('ums.supplement', 'Supplement')
    student_id = fields.Many2one('ums.student', 'Student')
    subject_id = fields.Many2one('ums.subject', 'Subject')
    pass_or_fail = fields.Boolean(string='Pass?', readonly=True)
    mark_scored = fields.Float(string='Mark')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")
    sub_first_id = fields.Many2one('result.subject.line', string="ID")


class SecondSupplementLine(models.Model):
    _name = 'second.supplement.line'
    _description = 'Second Supplement Line'

    supplement_id = fields.Many2one('ums.supplement', 'Supplement')
    student_id = fields.Many2one('ums.student', 'Student')
    subject_id = fields.Many2one('ums.subject', 'Subject')
    pass_or_fail = fields.Boolean(string='Pass?', readonly=True)
    mark_scored = fields.Float(string='Mark')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")
    sub_second_id = fields.Many2one('result.subject.line', string="ID")
