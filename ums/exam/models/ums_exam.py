# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime


class ExamType(models.Model):
    """
    Represents different types of university examinations.
    
    This model stores the basic configuration for exam types like mid-term and final exams.
    
    Attributes:
        name (Char): Name of the exam type
        exam_type (Selection): Type of exam (mid_term/final)
    """
    _name = "ums.exam.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Exam Type"
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string="Name", required=False, tracking=True)
    exam_type = fields.Selection(string='Exam Type', selection=[
        ('mid_term', 'Mid Term'),
        ('final', ' Final Exam (Exam that promotes students to the next Semester)')
    ])


class Exam(models.Model):
    """
    Manages university examinations and their scheduling.
    
    This model handles the creation and management of exams, including scheduling,
    subject allocation, and state management throughout the exam lifecycle.
    
    Attributes:
        name (Char): Auto-generated exam name
        type_name (Char): User-defined exam name
        type (Many2one): Reference to exam type
        start_date (Date): Exam start date
        end_date (Date): Exam end date
        class_id (Many2one): Reference to class
        program_id (Many2one): Related program
        level_id (Many2one): Academic level
        department_id (Many2one): Department reference
        academic_year (Many2one): Academic year
        college_id (Many2one): College reference
        specialist_id (Many2one): Specialist reference
        state (Selection): Exam state (draft/ongoing/close/cancel)
        subject_ids (One2many): Related exam subjects
        semester_id (Many2one): Semester reference
        exam_type (Selection): Type of exam (final/supplement/absent)
        is_department (Boolean): Department flag
        is_specialist (Boolean): Specialist flag
    """
    _name = "ums.exam"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Exam"
    _order = 'id desc'

    name = fields.Char(string="Name", readonly=True, tracking=True, default='New')
    type_name = fields.Char(string='Name', required=True, tracking=True)
    type = fields.Many2one('ums.exam.type', 'Type', required=False, tracking=True, invisible=True)
    start_date = fields.Date(string="Start Data", required=True, tracking=True)
    end_date = fields.Date(string="End Data", required=True, tracking=True)
    class_id = fields.Many2one('ums.class', 'Class', required=True, tracking=True)
    program_id = fields.Many2one(related="class_id.program_id", string='Program', tracking=True)
    level_id = fields.Many2one("ums.level", string='Level', store=True, tracking=True)
    department_id = fields.Many2one('ums.department', string='Department', domain="[('college_id','=',college_id)]", tracking=True)
    academic_year = fields.Many2one(related="class_id.academic_year", string='Academic Year', required=True,
                                    tracking=True, )
    college_id = fields.Many2one('ums.college', string="College", required=True, tracking=True)
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", domain="[('department_id','=',department_id)]", tracking=True)
    # evaluation_ids = fields.One2many('ums.exam.evaluation', 'exam_evaluation_id')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ongoing', 'On Going'),
         ('close', 'Closed'),
         ('cancel', 'Canceled')],
        default='draft', string="State", tracking=True)
    subject_ids = fields.One2many('ums.exam.subject.line', 'exam_id', string="Subject Line", tracking=True)
    semester_id = fields.Many2one('ums.semester', string="Semestar", store=True, tracking=True, domain="[('college_id','=',college_id)]")
    exam_type = fields.Selection(string='Exam Type', selection=[
        ('final', 'Final Exam (Exam that promotes students to the next Semester)'),
        ('supplement_exam', 'Supplement Exam'),('absent_exam', 'Absent Exam')], required=True, tracking=True)
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
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}

    @api.onchange('class_id','program_id')
    def onchange_level_id(self):
         for rec in self:
            if rec.exam_type == 'final':
                rec.level_id = rec.class_id.level
            elif rec.exam_type == 'supplement_exam':
                rec.level_id = rec.class_id.level
            elif rec.exam_type == 'absent_exam':
                if rec.program_id:
                    domain = []
                    program = rec.program_id.level_line
                    for items in program:
                        domain.append(items.level.id)
                    return {'domain': {'level_id': [('id', 'in', domain)]}}
                

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_("Start date must be Anterior to end date"))

    @api.onchange('college_id')
    def onchange_department_id(self):
        for rec in self:
            return {'domain': {'department_id': [('college_id', '=', rec.college_id.id)]}}
      
    @api.onchange('department_id','college_id')
    def onchange_specialist_id(self):
        for rec in self:
            if rec.department_id:
                return {'domain': {'specialist_id': [('department_id', '=', rec.department_id.id)]}}
            else :
                return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}  
        
    @api.onchange('college_id','department_id','specialist_id')
    def onchange_class_id(self):
        for rec in self:
            if rec.college_id:
                return {'domain': {'class_id': [('college_id', '=', rec.college_id.id)]}}
            elif rec.department_id:
                return {'domain': {'class_id': [('department_id', '=', rec.department_id.id)]}}
            elif rec.specialist_id:
                return {'domain': {'class_id': [('specialist_id', '=', rec.specialist_id.id)]}}
            
    # @api.onchange('specialist_id')
    # def onchange_class_id(self):
    #     for rec in self:
    #         return {'domain': {'class_id': [('specialist_id', '=', rec.specialist_id.id),('department_id', '=', rec.department_id.id)]}}
           

    def close_exam(self):
        """
        Closes the exam after verifying all evaluations are completed.
        
        Raises:
            ValidationError: If any evaluation is not in 'completed' state
        """
        for rec in self:
            comp = self.env['ums.exam.evaluation'].search([
                ('exam_id', '=', rec.name),
                ('college_id', '=', rec.college_id.name),
                ('specialist_id', '=', rec.specialist_id.name),
                ('class_id', '=', rec.class_id.name),
            ])
            for con in comp:
                if con.state != 'completed':
                    raise ValidationError(_("you can not close before completed valuation"))
            rec.state = 'close'

    def cancel_exam(self):
        self.state = 'cancel'
        
    def action_back(self):
        self.state = 'draft'

    def confirm_exam(self):
        """
        Confirms and starts the exam after validation.
        
        Creates evaluation records for each subject and changes exam state to 'ongoing'.
        
        Raises:
            UserError: If no subjects are added or required fields are missing
        """
        if len(self.subject_ids) < 1:
            raise UserError(_('Please Add Subjects'))
        for rec in self:
            for t in rec.subject_ids:
                if not t.date:
                    raise UserError(_('Please Add Date'))
                elif not t.time_from:
                    raise UserError(_('Please Add Time From'))
                elif not t.time_to:
                    raise UserError(_('Please Add Time to'))
                else:
                    pass
        name = str(self.type_name) + '-' + str(self.start_date)[0:10]
        self.name = name
        for line in self:
            for l in line.subject_ids:
                exam_evaluation_vals = {
                    'subject_id' : l.subject_id.id,
                    'exam_id' : line.id,
                    'class_id' : line.class_id.id,
                    'college_id' : line.college_id.id,
                    'specialist_id' : line.specialist_id.id,
                    'program_id' : line.program_id.id,
                    'state' : 'draft',
                    'academic_year' : line.academic_year.id,
                    'semester_id' : line.semester_id.id,
                    'exam_type' : line.exam_type,
                    'department_id' : line.department_id.id,
                }
                exam_evaluation = self.env['ums.exam.evaluation'].create(exam_evaluation_vals)
        self.state = 'ongoing'

    @api.onchange('level_id')
    def change_subject_line(self):
        for rec in self:
            if rec.exam_type == 'final':
                rec.subject_ids = False
                rec.semester_id = rec.class_id.semester_id
                for line in rec.program_id.level_line:
                    if rec.level_id and rec.level_id.id == line.level.id:
                        for t in line.semester_line:
                            if rec.semester_id and rec.semester_id.id == t.semester_id.id:
                                subject_vals = []
                                for l in t.subject_line:
                                    subject_vals.append((0, 0, {
                                        'subject_id': l.subject.id,
                                    }))
                                rec.subject_ids = subject_vals

            if rec.exam_type == 'supplement_exam':
                for line in rec.program_id.level_line:
                    if rec.level_id and rec.level_id.id == line.level.id:
                        semester_ids = [s.semester_id.id for s in line.semester_line]
                        return {'domain': {'semester_id': [('id', 'in', semester_ids)]}}
                    
    @api.onchange('level_id')
    def oncange_semestar_id(self):
        if self.exam_type == 'absent_exam':
            if self.level_id:
                vals = []
                domain = []
                program = self.program_id.level_line
                for items in program:
                    vals.append(items.level.id)
                    if self.level_id.id == items.level.id:
                        for rec in items.semester_line:
                            for t in rec.semester_id:
                                domain.append(t.id)
                return {'domain': {'semester_id': [('id', 'in', domain)]}}
                


    @api.onchange('semester_id')
    def change_semester_id(self):
        for rec in self:
            if rec.exam_type == 'supplement_exam':
                supplement = self.env['ums.supplement'].search([
                    ('class_id', '=', rec.class_id.id),
                    ('program_id', '=', rec.program_id.id),
                    ('level_id', '=', rec.level_id.id),
                ])
                if supplement:
                    rec.subject_ids = False
                    for sec in supplement:
                        
                        if sec.firest_semstar.id == rec.semester_id.id:
                            subject_vals = []
                            existing_subjects = rec.subject_ids.mapped('subject_id')
                            for l in sec.supplement_ids:
                                if l.subject_id not in existing_subjects:
                                    subject_vals.append((0, 0, {
                                        'subject_id': l.subject_id.id,
                                    }))
                                   
                            if subject_vals:
                                rec.subject_ids = subject_vals
                        else:
                            if sec.second_semstar.id == rec.semester_id.id:
                                subject_vals = []
                                existing_subjects = rec.subject_ids.mapped('subject_id')
                                for res in sec.supplement_second_ids:
                                    if res.subject_id not in existing_subjects:
                                        subject_vals.append((0, 0, {
                                            'subject_id': res.subject_id.id,
                                        }))
                                if subject_vals:
                                    rec.subject_ids = subject_vals
            elif rec.exam_type == 'absent_exam':
                absent = self.env['ums.absent'].search([
                    ('class_id', '=', rec.class_id.id),
                    ('program_id', '=', rec.program_id.id),
                    ('level_id', '=', rec.level_id.id),
                    # ('absent_check_first_sem', '=', False),
                    # ('absent_check_second_sem', '=', False),
                ])
                if absent:
                    if rec.semester_id:
                        rec.subject_ids = False
                        for sec in absent:
                            
                            if sec.firest_semstar.id == rec.semester_id.id:
                                subject_vals = []
                                existing_subjects = rec.subject_ids.mapped('subject_id')
                                for l in sec.absent_ids:
                                    if l.subject_id not in existing_subjects:
                                        subject_vals.append((0, 0, {
                                            'subject_id': l.subject_id.id,
                                        }))
                                if subject_vals:
                                    rec.subject_ids = subject_vals
                            
                            if sec.second_semstar.id == rec.semester_id.id:
                                subject_vals = []
                                existing_subjects = rec.subject_ids.mapped('subject_id')
                                for res in sec.absent_second_ids:
                                    if res.subject_id not in existing_subjects:
                                        subject_vals.append((0, 0, {
                                            'subject_id': res.subject_id.id,
                                        }))
                                if subject_vals:
                                    rec.subject_ids = subject_vals
        
    
class SubjectLine(models.Model):
    """
    Manages subject-specific details for an exam.
    
    This model stores information about individual subjects within an exam,
    including scheduling and marking details.
    
    Attributes:
        subject_id (Many2one): Reference to subject
        date (Date): Exam date for this subject
        time_from (Float): Start time
        time_to (Float): End time
        mark (Integer): Maximum marks
        exam_id (Many2one): Reference to parent exam
    """
    _name = 'ums.exam.subject.line'
    _description = 'Subject Line'

    subject_id = fields.Many2one('ums.subject', string='Subject', required=True, tracking=True)
    date = fields.Date(string='Date', required=False, tracking=True)
    time_from = fields.Float(string='Time From', required=False, tracking=True)
    time_to = fields.Float(string='Time To', required=False, tracking=True)
    mark = fields.Integer(string='Mark', tracking=True)
    exam_id = fields.Many2one('ums.exam', string='Exam', required=False)

