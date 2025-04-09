
from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta


class Program(models.Model):
    _name = "ums.program"
    _description = "College Programs"

    name = fields.Char('Name', required=True, help='Name')
    degree_name = fields.Char('Degree Name', required=True, help='College name in Degree Certificate')
    english_name = fields.Char('English Name', required=False, help='Name')
    code = fields.Char('Code', help='Code')
    college = fields.Many2one("ums.college", string="College")
    department = fields.Many2one("ums.department", string="Department", domain="[('college_id','=',college)]")
    program_type = fields.Selection([('deploma', 'Deploma'), ('bsc', 'Bsc'), ('master', 'Master')],
                                    string="Program type")
    level_line = fields.One2many("ums.program.level.line", "program_id", string="Level of program",
                                 ondelete="cascade")
    specialist_id = fields.Many2one('ums.specialist', string="Specialist")
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)
    
    @api.onchange('college')
    def onchange_is_department(self):
        for rec in self:
            if rec.college.department == True:
                rec.is_department = True
            else:
                rec.is_department = False

    @api.onchange('college')
    def onchange_is_specialist(self):
        for rec in self:
            if rec.college.specialist == True:
                rec.is_specialist = True
            else:
                rec.is_specialist = False

    @api.onchange('college')
    def onchange_department(self):
        for rec in self:
            return {'domain': {'department': [('college_id', '=', rec.college.id)]}}
    
    def name_get(self):
        return [(pro.id, '[%s] %s' % (pro.specialist_id.name, pro.name)) for pro in self]

    @api.onchange('department','college')
    def onchange_specialist_id(self):
        for rec in self:
            if rec.department:
                return {'domain': {'specialist_id': [('department_id', '=', rec.department.id)]}}
            else :
                return {'domain': {'specialist_id': [('college_id', '=', rec.college.id)]}}

    @api.onchange('college')
    def onchange_collage_id(self):
        if self.env.user.collage_ids and self.college.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college': [('id', 'in', domain)]}}


class ProgramLevel(models.Model):
    _name = "ums.program.level.line"
    _description = "Level of program"

    program_id = fields.Many2one("ums.program", string="program #")
    level = fields.Many2one("ums.level", string="Level")
    is_final = fields.Boolean("Is final")
    semester_line = fields.One2many("program.level.semester.line", "level_id",
                                    string="Semesters in levels with subject",
                                    ondelete="cascade")
    level_seq = fields.Integer('Level ID', required=False, copy=False, readonly=True, index=True)
    college = fields.Many2one(related='program_id.college', string="College", store=True)

    @api.onchange('college')
    def onchange_level(self):
        for rec in self:
            return {'domain': {'level': [('college_id', '=', rec.college.id)]}}

    @api.model
    def create(self, vals):
        vals['level_seq'] = self.env['ir.sequence'].next_by_code('ums.program.level.line')
        return super(ProgramLevel, self).create(vals)

    def write(self, vals):
        if not self.level_seq:
            vals['level_seq'] = self.env['ir.sequence'].next_by_code('ums.program.level.line')
        return super(ProgramLevel, self).write(vals)


class SemesterLine(models.Model):
    _name = "program.level.semester.line"
    _description = "Semester in program level with subjects in semester"

    level_id = fields.Many2one("ums.program.level.line", string="program level #")

    semester_id = fields.Many2one("ums.semester", string="Semester")

    subject_line = fields.One2many("program.semester.subject.line", "semester_id", string="Subjects of semester",
                                   ondelete="cascade")
    college = fields.Many2one(related='level_id.program_id.college', string="College", store=True)
    sem_seq = fields.Integer('Semester ID', required=False, copy=False, readonly=True, index=True)

    @api.onchange('college')
    def onchange_semester_id(self):
        for rec in self:
            return {'domain': {'semester_id': [('college_id', '=', rec.college.id)]}}

    @api.model
    def create(self, vals):
        vals['sem_seq'] = self.env['ir.sequence'].next_by_code('program.level.semester.line')
        return super(SemesterLine, self).create(vals)

    def write(self, vals):
        if not self.sem_seq:
            vals['sem_seq'] = self.env['ir.sequence'].next_by_code('program.level.semester.line')
        return super(SemesterLine, self).write(vals)


class SubjectLine(models.Model):
    _name = "program.semester.subject.line"
    _description = "Subjects in semester of level in program record"

    semester_id = fields.Many2one("program.level.semester.line", string="semester #")
    college = fields.Many2one(related='semester_id.level_id.program_id.college', string="College", store=True)
    subject = fields.Many2one("ums.subject", string="Subject")

    @api.onchange('college')
    def onchange_subject(self):
        for rec in self:
            return {'domain': {'subject': [('college_id', '=', rec.college.id)]}}
