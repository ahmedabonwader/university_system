# -*- coding: utf-8 -*-

from odoo import api, models, fields


class UniversityClass(models.Model):
    _name = "ums.class"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Class"
    _order = 'id desc'

    name = fields.Char(string="Class Name", required=True)
    english_name = fields.Char(string="Class English Name", required=False)
    code = fields.Char(string="Code")

    program_id = fields.Many2one('ums.program', string="Program", domain="[('college','=',college_id)]")
    college_id = fields.Many2one('ums.college', string="College")
    department_id = fields.Many2one('ums.department', string="Department", domain="[('college_id','=',college_id)]")
    level = fields.Many2one('ums.level', string="Level", domain="[('college_id','=',college_id)]")
    academic_year = fields.Many2one('ums.academic.year', string="Academic Year", domain="[('college_id','=',college_id)]")
    semester_id = fields.Many2one('ums.semester', string="Semester", domain="[('college_id','=',college_id)]")
    specialist_id = fields.Many2one('ums.specialist', string="Specialist")
    class_strength = fields.Integer(string="Class Strength")
    group_id = fields.Many2one('ums.group', string="Group")
    std_line_ids = fields.One2many('ums.student', 'class_id', "Student Line", ondelete="cascade")
    student_count = fields.Integer(string="Student Count", compute='_compute_student_count', tracking=True)
    faculity_id = fields.Many2one('ums.faculty', 'Faculity')
    is_department = fields.Boolean(string="Is Department ?", store=True,)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True,)
    
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
    def onchange_college_id_department_id(self):
        for rec in self:
            if rec.college_id.department == True:
                return {'domain': {'department_id': [('college_id', '=', rec.college_id.id)]}}
        
    @api.onchange('college_id')
    def onchange_college_id_program(self):
        for rec in self:
            return {'domain': {'program_id': [('college', '=', rec.college_id.id)]}}
        
    @api.onchange('college_id')
    def onchange_college_id_academic_year(self):
        for rec in self:
            return {'domain': {'academic_year': [('college_id', '=', rec.college_id.id)]}}
        
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
        
    @api.onchange('department_id','college_id')
    def onchange_specialist_id(self):
        for rec in self:
            if rec.department_id:
                return {'domain': {'specialist_id': [('department_id', '=', rec.department_id.id)]}}
            else :
                return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}

    def _compute_student_count(self):
        for rec in self:
            studeent_count = self.env['ums.student'].search_count([('class_id', '=', rec.id)])
            rec.student_count = studeent_count

    # This Function of Smart Button Student Count
    def action_student(self):
        for rec in self:
            domain = [('class_id', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Student',
                'res_model': 'ums.student',
                'domain': domain,
                'view_mode': 'tree,form',
                'target': 'current',

            }

    @api.onchange('program_id')
    def onchange_level(self):
        if self.program_id:
            domain = []
            program = self.program_id.level_line
            for items in program:
                domain.append(items.level.id)
            return {'domain': {'level': [('id', 'in', domain)]}}

    @api.onchange('level')
    def onchange_semester_id(self):
        if self.level:
            vals = []
            domain = []
            program = self.program_id.level_line
            for items in program:
                vals.append(items.level.id)
                if self.level.id == items.level.id:
                    for rec in items.semester_line:
                        for t in rec.semester_id:
                            domain.append(t.id)
            return {'domain': {'semester_id': [('id', 'in', domain)]}}
        
