# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import datetime


class ExamEvaluation(models.Model):
    _name = 'ums.exam.evaluation'
    _description = "Exam Valuation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Name', default='New')
    exam_id = fields.Many2one('ums.exam', string='Exam', required=True,
                              domain=[('state', '=', 'ongoing')])
    class_id = fields.Many2one(related='exam_id.class_id', string='Class', required=True, store=True)
    college_id = fields.Many2one(related='exam_id.college_id', string="College", tracking=True, store=True)
    specialist_id = fields.Many2one(related='exam_id.specialist_id', string="Specialist", tracking=True)
    teachers_id = fields.Many2one('ums.faculty', string='Evaluator')
    program_id = fields.Many2one(related='exam_id.program_id', string='Program')
    level_id = fields.Many2one(related='exam_id.level_id', string='Level')
    mark = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    assignment = fields.Float(string="Max Assignment")
    pass_assignment = fields.Float(string="Pass Assignment")
    state = fields.Selection([('draft', 'Draft'), ('alternative', 'Alternative'), ('completed', 'Completed'),
                              ('cancel', 'Canceled')], default='draft')
    evaluation_line = fields.One2many('exam.evaluation.line', 'evaluation_id', string='Students')
    subject_id = fields.Many2one('ums.subject', string='Subject', required=True)
    mark_sheet_created = fields.Boolean(string='Mark sheet Created')
    date = fields.Date(string='Date', default=fields.Date.today)
    academic_year = fields.Many2one('ums.academic.year', string='Academic Year', related='exam_id.academic_year',
                                    store=True)
    semester_id = fields.Many2one(related='exam_id.semester_id', string="Semester", readonly=True)
    exam_type = fields.Selection(related='exam_id.exam_type', store=True)
    department_id = fields.Many2one(related='class_id.department_id', string='Department', store=True)
    result_test = fields.Boolean(string="Test", store=True)
    reason_test = fields.Boolean(string="Reason", store=True)
    is_portable = fields.Boolean(string="Is Portable?", store=True, compute="_compute_portable")
    is_department = fields.Boolean(string="Is Department ?", store=True, )
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True, )

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

    @api.depends('college_id.is_portable')
    def _compute_portable(self):
        for rec in self:
            if rec.college_id.is_portable == True:
                rec.is_portable = True
            else:
                rec.is_portable = False

    @api.onchange('college_id')
    def onchange_college_id(self):
        for rec in self:
            return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}

    @api.onchange('specialist_id')
    def onchange_specialist_id(self):
        for rec in self:
            return {'domain': {'class_id': [('specialist_id', '=', rec.specialist_id.id)]}}

    @api.onchange('exam_id', 'subject_id')
    def onchange_exam_id(self):
        self.mark = ''
        if self.subject_id:
            for sub in self.exam_id.subject_ids:
                if sub.subject_id.id == self.subject_id.id:
                    if sub.mark:
                        self.mark = sub.mark
        domain = []
        subjects = self.exam_id.subject_ids
        for items in subjects:
            domain.append(items.subject_id.id)
        return {'domain': {'subject_id': [('id', 'in', domain)]}}

    @api.onchange('pass_mark')
    def onchange_pass_mark(self):
        if self.pass_mark > self.mark:
            raise UserError(_('Pass mark must be less than Max Mark'))
        for records in self.evaluation_line:
            records.pass_or_fail = True if records.mark_scored >= self.pass_mark else False

    def create_portable_student(self):
        action = self.env.ref('ums.portable_wizard_action').read()[0]
        return action
    
    def create_transferred_student(self):
        action = self.env.ref('ums.add_transferred_wizard_action').read()[0]
        return action

    def create_mark_sheet(self):
        for rec in self:
            if rec.exam_type == 'final':
                evaluation_line_obj = self.env['exam.evaluation.line']
                students = self.class_id.std_line_ids
                if len(students) < 1:
                    raise UserError(_('There are no students in this Class'))
                for student in students:
                    data = {
                        'student_id': self.evaluation_line.student_id.id,
                        'student_name': student.id,
                        'student_status':student.student_status.id,
                        'evaluation_id': self.id,
                    }
                    evaluation_line_obj.create(data)
                self.mark_sheet_created = True
            elif rec.exam_type == 'supplement_exam':
                supplement = self.env['ums.supplement'].search([
                    ('class_id', '=', rec.class_id.id),
                    ('program_id', '=', rec.program_id.id),
                    ('level_id', '=', rec.level_id.id),
                ])
                if supplement:
                    for sec in supplement:
                        for l in sec.supplement_ids:
                            if l.subject_id.id == rec.subject_id.id:
                                student_vals_first = {
                                    'student_name': sec.name.id,
                                    # 'student_name': sec.name.name,
                                    'evaluation_id': self.id,
                                    'sub_id': l.sub_first_id.id,
                                }
                                evaluation_lines_obj_first = self.env['exam.evaluation.line'].create(student_vals_first)
                        for t in sec.supplement_second_ids:
                            if t.subject_id.id == rec.subject_id.id:
                                student_vals_second = {
                                    'student_name': sec.name.id,
                                    # 'student_name': sec.name.name,
                                    'evaluation_id': self.id,
                                    'sub_id': t.sub_second_id.id,
                                }
                                evaluation_lines_obj_second = self.env['exam.evaluation.line'].create(
                                    student_vals_second)
            elif rec.exam_type == 'absent_exam':
                absent = self.env['ums.absent'].search([
                    ('class_id', '=', rec.class_id.id),
                    ('program_id', '=', rec.program_id.id),
                    ('level_id', '=', rec.level_id.id),
                ])
                if absent:
                    for line in absent:
                        for l in line.absent_ids:                           
                            if l.subject_id == rec.subject_id and l.absent_check == False:
                                student_vals_first = {
                                    'student_name': line.name.id,
                                    'evaluation_id': self.id,
                                    'sub_id': l.sub_first_id.id,
                                }
                                evaluation_lines_obj_first = self.env['exam.evaluation.line'].create(student_vals_first)
                            elif l.subject_id == rec.subject_id and l.absent_check == True:
                                raise UserError(_('This Exam Evaluation was entered Before!!!'))
                        for t in line.absent_second_ids:
                            if t.subject_id == rec.subject_id and l.absent_check == False:
                                student_vals_second = {
                                    'student_name': line.name.id,
                                    'evaluation_id': self.id,
                                    'sub_id': t.sub_second_id.id,
                                }
                                evaluation_lines_obj_second = self.env['exam.evaluation.line'].create(student_vals_second)
                            elif t.subject_id == rec.subject_id and l.absent_check == True:
                                raise UserError(_('This Exam Evaluation was entered Before!!!'))
            self.mark_sheet_created = True

    def evaluation_done(self):
        for rec in self:
            rec.state = 'alternative'

    @api.onchange('evaluation_line')
    def _onchange_evaluation_line(self):
        for rec in self:
            if any(line.absent for line in rec.evaluation_line):
                rec.result_test = True
            else:
                rec.result_test = False
            if any(line.reason for line in rec.evaluation_line):
                rec.reason_test = True
            else:
                rec.reason_test = False

    def evaluation_completed(self):
        self.name = str(self.exam_id.type_name) + '-' + str(self.subject_id.name) + '-' + str(
            self.exam_id.start_date)[0:10]
        if self.pass_mark > self.mark:
            raise UserError(_('Pass mark must be less than Max Mark'))
        if self.pass_assignment > self.assignment:
            raise UserError(_('Pass assignment must be less than Max assignment'))
        # if not self.assignment:
        #     raise UserError(_('Please Add Max Assignment !!'))
        # if not self.pass_assignment:
        #     raise UserError(_('Please Add Pass Assignment !!'))
        if not self.mark:
            raise UserError(_('Please Add Max Mark !!'))
        if not self.pass_mark:
            raise UserError(_('Please Add Pass Mark !!'))
        # for records in self.evaluation_line:
            # records.pass_or_fail = True if records.mark_scored >= self.pass_mark else False

        # =======================Create Result Information For All Student=============================#
        if self.exam_type == 'final':
            result = self.env["ums.result"].search([("name", '=', 'نتيحة' + str(self.class_id.name) + ' ' + str(
                self.level_id.name) + ' ' + str(self.exam_id.academic_year.name))])
            if not result:
                result = self.env['ums.result'].sudo().create({
                    'name': 'نتيحة' + str(self.class_id.name) + ' ' + str(self.level_id.name) + ' ' + str(
                        self.exam_id.academic_year.name),
                    'result_date': datetime.datetime.now(),
                    'college': self.college_id.id,
                    'program': self.program_id.id,
                    'level': self.level_id.id,
                    'class_id': self.class_id.id,
                    'academic_year': self.exam_id.academic_year.id,
                    'department': self.department_id.id,
                    'specialist_id': self.specialist_id.id,
                    'exam_type': self.exam_type,
                })
                if not result.firest_semstar:
                    result.write({"firest_semstar": self.semester_id.id})
            for line in self.evaluation_line:
                if line.pass_or_fail:
                    if line.student_status:
                        update_vals = {
                            'degree': line.last_mark,
                            'pass_or_fail': line.pass_or_fail,
                            'degree_letter': line.degree_letter.name,
                            'note': line.note,
                            # 'sub_id':line.sub_id.id,
                        }
                        line.sub_id.write(update_vals)
                if not line.pass_or_fail:
                    if not line.student_status:
                        pass
                # student = self.env['ums.student'].search([("name", "=", line.student_name)], limit=1)
                # if student:
                # ================================///First Semester///=========================================#
                if self.semester_id.id == result.firest_semstar.id:
                    semester_result = result.first_semester_result.search(
                        [("student", "=", line.student_name.id), ('result_id', "=", result.id)], limit=1)
                    if not semester_result:
                        semester_result = self.env["ums.result.first"].create({
                            'student': line.student_name.id,
                            'student_status': line.student_status.id,
                            'class_id': line.class_id.id,
                            'result_id': result.id})

                    subject_line = self.env["result.subject.line"].search(
                        [("subject", "=", self.subject_id.id), ('first_result_id', "=", semester_result.id)])
                    if not subject_line:
                        subject_line = self.env["result.subject.line"].create({
                            'subject': self.subject_id.id,
                            'degree': line.last_mark,
                            'pass_or_fail': line.pass_or_fail,
                            'degree_letter': line.degree_letter.name,
                            'hours': self.subject_id.hours,
                            'note': line.note,
                            'sub_id': line.sub_id.id,
                            'first_result_id': semester_result.id})
                    else:
                        subject_line.write({"degree": line.last_mark})

                    semester_result.compute_semester_degree()
                # ========================== /Semester Second /=============================== #
                else:
                    result.write({"second_semstar": self.semester_id.id})
                    semester_result = result.second_semester_result.search(
                        [("student", "=", line.student_name.id), ('result_id', "=", result.id)], limit=1)
                    if not semester_result:
                        semester_result = self.env["ums.result.second"].create({
                            'student': line.student_name.id,
                            'student_status': line.student_status.id,
                            'class_id': line.class_id.id,
                            'result_id': result.id})
                    subject_line = self.env["result.subject.line"].search(
                        [("subject", "=", self.subject_id.id), ('second_result_id', "=", semester_result.id)])
                    if not subject_line:
                        subject_line = self.env["result.subject.line"].create({
                            'subject': self.subject_id.id,
                            'degree': line.last_mark,
                            'pass_or_fail': line.pass_or_fail,
                            'degree_letter': line.degree_letter.name,
                            'note': line.note,
                            'hours': self.subject_id.hours,
                            'sub_id': line.sub_id.id,
                            'second_result_id': semester_result.id})
                    else:
                        subject_line.write({"degree": line.last_mark})
                    semester_result.compute_semester_degree()
                    print("student", line.student_name.name)
        elif self.exam_type == 'supplement_exam':

            result = self.env["ums.result"].search([("name", '=',
                                                     'نتيحة ملاحق' + ' ' + str(self.class_id.name) + ' ' + str(
                                                         self.level_id.name) + ' ' + str(
                                                         self.exam_id.academic_year.name))])
            if not result:
                result = self.env['ums.result'].sudo().create({
                    'name': 'نتيحة ملاحق' + ' ' + str(self.class_id.name) + ' ' + str(self.level_id.name) + ' ' + str(
                        self.exam_id.academic_year.name),
                    'result_date': datetime.datetime.now(),
                    'college': self.college_id.id,
                    'program': self.program_id.id,
                    'level': self.level_id.id,
                    'class_id': self.class_id.id,
                    'academic_year': self.exam_id.academic_year.id,
                    'department': self.department_id.id,
                    'specialist_id': self.specialist_id.id,
                    'exam_type': self.exam_type,
                })
                if not result.firest_semstar:
                    result.write({"firest_semstar": self.semester_id.id})
            for line in self.evaluation_line:
                if line.pass_or_fail:
                    update_vals = {
                        'degree': line.last_mark,
                        'pass_or_fail': line.pass_or_fail,
                        'degree_letter': line.degree_letter.name,
                        'note': line.note,
                        # 'sub_id':line.sub_id.id,
                    }
                    line.sub_id.write(update_vals)
                elif line.pass_or_fail == False:

                    # update_vals ={
                    #     'degree':line.mark_scored,
                    #     'pass_or_fail':line.pass_or_fail,
                    #     'degree_letter':line.degree_letter.name,
                    #     'note':line.note,
                    #     'sub_id':line.sub_id.id,
                    # }
                    # line.sub_id.write(update_vals)
                    # print("!!!!!!!!!!!!!!!!",line.pass_or_fail)
                    # print("&&&&&&&&&&&&&&&&",line.sub_id)
                    # print("@@@@@@@@@@@@@@@@",update_vals)
                    pass
                if line.student_status:
                    update_vals = {
                        'degree': line.last_mark,
                        'pass_or_fail': line.pass_or_fail,
                        'degree_letter': line.degree_letter.name,
                        'note': line.note,
                        # 'sub_id':line.sub_id.id,
                    }
                    line.sub_id.write(update_vals)
                elif not line.student_status:
                    pass
                # student = self.env['ums.student'].search([("name", "=", line.student_name)], limit=1)
                # if student:
                # ================================///First Semester///=========================================#
                if self.semester_id.id == result.firest_semstar.id:
                    semester_result = result.first_semester_result.search(
                        [("student", "=", line.student_name.id), ('result_id', "=", result.id)], limit=1)
                    if not semester_result:
                        semester_result = self.env["ums.result.first"].create({
                            'student': line.student_name.id,
                            'result_id': result.id})

                    subject_line = self.env["result.subject.line"].search(
                        [("subject", "=", self.subject_id.id), ('first_result_id', "=", semester_result.id)])
                    if not subject_line:
                        subject_line = self.env["result.subject.line"].create({
                            'subject': self.subject_id.id,
                            'degree': line.last_mark,
                            'pass_or_fail': line.pass_or_fail,
                            'degree_letter': line.degree_letter.name,
                            'hours': self.subject_id.hours,
                            'note': line.note,
                            'sub_id': line.sub_id.id,
                            'first_result_id': semester_result.id})
                    else:
                        subject_line.write({"degree": line.last_mark})


                # ========================== /Semester Second /=============================== #
                else:
                    result.write({"second_semstar": self.semester_id.id})
                    semester_result = result.second_semester_result.search(
                        [("student", "=", line.student_name.id), ('result_id', "=", result.id)], limit=1)
                    if not semester_result:
                        semester_result = self.env["ums.result.second"].create({
                            'student': line.student_name.id,
                            'result_id': result.id})
                    subject_line = self.env["result.subject.line"].search(
                        [("subject", "=", self.subject_id.id), ('second_result_id', "=", semester_result.id)])
                    if not subject_line:
                        subject_line = self.env["result.subject.line"].create({
                            'subject': self.subject_id.id,
                            'degree': line.last_mark,
                            'pass_or_fail': line.pass_or_fail,
                            'degree_letter': line.degree_letter.name,
                            'note': line.note,
                            'sub_id': line.sub_id.id,
                            'hours': self.subject_id.hours,
                            'second_result_id': semester_result.id})
                    else:
                        subject_line.write({"degree": line.last_mark})

                    print("student", line.student_name.name)
        elif self.exam_type == 'absent_exam':
            for line in self.evaluation_line:
                update_vals = {
                    'degree': line.last_mark,
                    'pass_or_fail': line.pass_or_fail,
                    'degree_letter': line.degree_letter.name,
                    'note': line.note,
                    # 'sub_id':line.sub_id.id,
                }
                line.sub_id.write(update_vals)
                absent = self.env['ums.absent'].search([
                    ('name','=',line.student_name.id),
                ])
                if absent:
                    for record in absent:
                        if record.firest_semstar == self.semester_id:
                            for items in record.absent_ids:
                                if items.subject_id == self.subject_id:
                                    items.absent_check = True
                        elif record.second_semstar == self.semester_id:
                            for item in record.absent_second_ids:
                                if item.subject_id == self.subject_id:
                                    item.absent_check = True

        self.state = 'completed'

    def set_to_draft(self):
        self.state = 'draft'

    def evaluation_canceled(self):
        self.state = 'cancel'


class StudentsEvaluationLine(models.Model):
    _name = 'exam.evaluation.line'
    _description = 'Exam Evaluation Line'

    evaluation_id = fields.Many2one('ums.exam.evaluation', string='Evaluation Id')
    college_id = fields.Many2one(related='evaluation_id.college_id', string='College', store=True)
    student_id = fields.Many2one('ums.student', string='Students')
    student_name = fields.Many2one('ums.student', string='Students')
    mark_scored = fields.Float(string='Mark')
    assignment_mark = fields.Float(string='Assignment Mark')
    last_mark = fields.Float(string='Last Mark', readonly=True, store=True)
    pass_or_fail = fields.Boolean(string='Pass?', readonly=True)
    absent = fields.Boolean(string='Absent?')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter", readonly=True, store=True)
    sub_id = fields.Many2one('result.subject.line', string="ID", readonly=True)
    note = fields.Char("Note")
    student_status = fields.Many2one('ums.student.status', 'Student Status', readonly=True)
    class_id = fields.Many2one('ums.class', 'Class', readonly=True)
    exam_type = fields.Selection(related='evaluation_id.exam_id.exam_type', store=True)
    reason = fields.Boolean(string="Reason?")

    @api.onchange('mark_scored','assignment_mark')
    def change_mark_status(self):
        for rec in self:
            if rec.mark_scored >= rec.evaluation_id.pass_mark and rec.assignment_mark >= rec.evaluation_id.pass_assignment:
                rec.last_mark = rec.mark_scored + rec.assignment_mark
                rec.pass_or_fail = True
                
                rec.degree_letter = self.env["ums.division"].search([('maximum_marks', '>=', rec.last_mark),
                        ('college_id', '=', rec.college_id.id),('minimum_marks', '<=', rec.last_mark)],
                                                                    limit=1).id
            else:
                if rec.mark_scored < rec.evaluation_id.pass_mark and rec.assignment_mark >= rec.evaluation_id.pass_assignment:
                    rec.last_mark = rec.mark_scored
                if rec.mark_scored >= rec.evaluation_id.pass_mark and rec.assignment_mark < rec.evaluation_id.pass_assignment:
                    rec.last_mark = rec.assignment_mark
                rec.pass_or_fail = False
                rec.degree_letter = self.env["ums.division"].search([('is_fail', '=', True)], limit=1).id
                
    @api.onchange('absent','reason')
    def oncahnge_absent(self):
        for rec in self:
            if rec.absent:
                if rec.reason == False:
                    rec.degree_letter = self.env["ums.division"].search([('is_fail', '=', True)], limit=1).id
                if rec.reason == True:
                    degree_letter = self.env['ums.division'].search(
                        [('name','=','غ')], limit=1
                    ).id
                    if not degree_letter:
                        vals = {
                            'name': 'غ',
                            'english_name': 'غ',
                            'college_id':rec.college_id.id,
                            'maximum_marks':0,
                            'minimum_marks':0,
                        }
                        degree_letter = self.env['ums.division'].create(vals)
                    rec.degree_letter = degree_letter
            else:
                rec.degree_letter = False

                    
            


class StudentStatus(models.Model):
    _name = 'ums.student.status'
    _description = 'ums.student.status'

    name = fields.Char(string='Name')
    code = fields.Char('Code')
