# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval


class Result(models.Model):
    _name = 'ums.result'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Results management"
    _order = 'id desc'

    name = fields.Char(string="Result Name", required=True)
    college = fields.Many2one("ums.college", string="College")
    department = fields.Many2one("ums.department", string="Department")
    level = fields.Many2one("ums.level", string="Level")
    academic_year = fields.Many2one("ums.academic.year", string="Academic Year")
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", tracking=True)

    program = fields.Many2one('ums.program', 'program')
    first_semester_result = fields.One2many("ums.result.first", "result_id", string="First semester")
    second_semester_result = fields.One2many("ums.result.second", "result_id", string="Second semester")
    class_id = fields.Many2one('ums.class', string='Class')
    result_date = fields.Date(string="Date", required=False)
    note_ids = fields.One2many('ums.result.note', 'note_id')
    state = fields.Selection(
        [("draft", "First Semester"), ("first_confirm", "Confirmed"), ("second_draft", "Second Semester"),
         ("second_confirm", "Confirmed"), ("old", "Old")], default="draft",
        string="status")
    approve_state = fields.Selection(
        [("preparation", "Preparation"), ("department", "Department"), ("academic_office", "Academic office")],
        default="preparation")

    firest_semstar = fields.Many2one('ums.semester', 'First Semstar')
    first_semester_n = fields.Char("First Semester note")
    second_semstar = fields.Many2one('ums.semester', 'Second Semstar')
    second_semester_n = fields.Char("Second Semester note")
    supplement_count = fields.Integer(string="Supplement Count", compute='_compute_supplement_count', tracking=True)
    portable_count = fields.Integer(string="portable Count", compute='_compute_portable_count', tracking=True)
    exam_type = fields.Selection(string='Result Type', selection=[
        ('final', 'Final Result (Result that promotes students to the next Semester)'),
        ('supplement_exam', 'Supplement Result'),
    ], required=True)
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)

    data_type = fields.Selection([('new_data', 'New Data'), ('old_data', 'Old Data')], default="old_data",
                                 string="Data Type")

    def action_add_degree(self):
        action = self.env.ref('ums.add_degree_wizard_action').read()[0]
        return action

    def execute_sql_query(self):

        wizard_model = self.env['result.wizard']
        vals = {
            'result_id': self.id
        }
        new = wizard_model.create(vals)
        return {
            'name': "Print Wizard",
            'type': 'ir.actions.act_window',
            'res_model': 'result.wizard',
            'res_id': new.id,
            'view_id': self.env.ref('ums.view_semester_result_wizard', False).id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

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

    # def action_done(self):
    #     total_hours = 0
    #     total_degree = 0
    #     for subject in self.first_semester_result.subject_line:
    #         total_hours += subject.hours
    #         total_degree += subject.degree

    #     if total_hours > 0:
    #         calculated_degree = (total_hours / 10) * (total_degree / total_hours)
    #         self.semester_degree = str(calculated_degree)

    def _compute_supplement_count(self):
        for rec in self:
            supplement_count = self.env['ums.supplement'].search_count([('result_id', '=', rec.id)])
            rec.supplement_count = supplement_count

    def _compute_portable_count(self):
        for rec in self:
            portable_count = self.env['ums.portable'].search_count([('result_id', '=', rec.id)])
            rec.portable_count = portable_count

    # This Function of Smart Button Supplement Count
    def action_supplement(self):
        for rec in self:
            domain = [('result_id', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Supplements',
                'res_model': 'ums.supplement',
                'domain': domain,
                'view_mode': 'tree,form',
                'target': 'current',
            }

    # This Function of Smart Button Portable Count
    def action_portable(self):
        for rec in self:
            domain = [('result_id', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Portables',
                'res_model': 'ums.portable',
                'domain': domain,
                'view_mode': 'tree,form',
                'target': 'current',
            }

    def first_draft(self):
        self.state = "draft"

    def action_back(self):
        for rec in self:
            rec.state = "draft"

    def first_confirm(self):
        for rec in self:
            rec.create_history_supplement_carry()
            rec.state = "first_confirm"

    def second_draft(self):
        self.state = "second_draft"

    def second_confirm(self):
        for rec in self:
            rec.create_history_supplement_carry()
            rec.state = "second_confirm"

    def set_approve_department(self):
        self.approve_state = "department"

    def set_approve_academic(self):
        self.approve_state = "academic_office"

    def create_history_supplement_carry(self):
        for rec in self:
            # program = self.env['ums.program'].search([('name', '=', rec.program.id)], limit=1)
            # if not program:
            #     program_vals = {
            #         'name': rec.program,
            #         'college': rec.college.id,
            #         'department': rec.department.id,
            #     }
            #     program = self.env['ums.program'].create(program_vals)
            result = self.env["ums.result"].search([('name', '=', rec.name)], limit=1)
            if not result:
                vals_4 = {
                    'name': rec.name,
                }
                result = self.env['ums.result'].create(vals_4)

            for line in rec.first_semester_result:
                for t in line.subject_line:
                    history = self.env['ums.result.history'].search([
                        ('result_id', '=', rec.id),
                        ('name', '=', line.student.id),
                        ('class_id', '=', rec.class_id.id),
                    ], limit=1)
                    if not history:
                        history_vals = {
                            'result_id': rec.id,
                            'name': line.student.id,
                            'collage_id': rec.college.id,
                            'department_id': rec.department.id,
                            'program_id': rec.program.id,
                            'class_id': rec.class_id.id,
                            'specialist_id': rec.specialist_id.id,
                            'level_id': rec.level.id,
                            'academic_year_id': rec.academic_year.id,
                            'date': rec.result_date,
                            'firest_semstar': rec.firest_semstar.id,
                            'second_semstar': rec.second_semstar.id,
                            # 'result_id': result.id,
                        }
                        history = self.env['ums.result.history'].create(history_vals)
                    history_line_first = self.env['first.result.history.line'].search([
                        ('subject_id', '=', t.subject.id),
                        ('history_id', '=', history.id),
                    ], limit=1)
                    degree_letter = self.env['ums.division'].search([
                        ('name', '=', t.degree_letter),
                    ], limit=1)
                    if not degree_letter:
                        degree_vals = {
                            'name': t.degree_letter
                        }
                        degree_letter = self.env['ums.division'].create(degree_vals)
                    if not history_line_first:
                        history_line_first_vals = {
                            'subject_id': t.subject.id,
                            'history_id': history.id,
                            'degree': t.degree,
                            'note': t.note,
                            'hours': t.hours,
                            'degree_letter': degree_letter.id,
                        }
                        history_line_first = self.env['first.result.history.line'].create(history_line_first_vals)
                    if not t.pass_or_fail:
                        if rec.exam_type == 'final':
                            supplement = self.env['ums.supplement'].search([
                                ('exam_name', '=', rec.name),
                                ('name', '=', line.student.id),
                                ('class_id', '=', rec.class_id.id),
                            ], limit=1)
                            if not supplement:
                                supplement_vals = {
                                    'exam_name': rec.name,
                                    'name': line.student.id,
                                    'class_id': rec.class_id.id,
                                    'department': rec.department.id,
                                    'program_id': rec.program.id,
                                    'level_id': rec.level.id,
                                    'academic_year': rec.academic_year.id,
                                    'college_id': rec.college.id,
                                    'specialist_id': rec.specialist_id.id,
                                    'date': rec.result_date,
                                    'firest_semstar': rec.firest_semstar.id,
                                    'second_semstar': rec.second_semstar.id,
                                    'result_id': rec.id,
                                }
                                supplement = self.env['ums.supplement'].create(supplement_vals)
                            supplement_line_first = self.env['first.supplement.line'].search([
                                ('subject_id', '=', t.subject.id),
                                ('supplement_id', '=', supplement.id),
                            ], limit=1)
                            degree_letter = self.env['ums.division'].search([
                                ('name', '=', t.degree_letter),
                            ], limit=1)
                            if not degree_letter:
                                degree_vals = {
                                    'name': t.degree_letter
                                }
                                degree_letter = self.env['ums.division'].create(degree_vals)

                            print("supplemnt")
                            if not supplement_line_first:
                                print("in if subject")
                                supplement_line_first_vals = {
                                    'subject_id': t.subject.id,
                                    'pass_or_fail': t.pass_or_fail,
                                    'mark_scored': t.degree,
                                    'degree_letter': degree_letter.id,
                                    'supplement_id': supplement.id,
                                    'sub_first_id': t.id,
                                }
                                supplement_line_first = self.env['first.supplement.line'].create(
                                    supplement_line_first_vals)
                            if t.degree_letter == "غ":
                                absent = self.env['ums.absent'].search([
                                    ('exam_name', '=', rec.name),
                                    ('name', '=', line.student.id),
                                    ('class_id', '=', rec.class_id.id),
                                ], limit=1)
                                if not absent:
                                    absent_vals = {
                                        'exam_name': rec.name,
                                        'name': line.student.id,
                                        'class_id': rec.class_id.id,
                                        'department': rec.department.id,
                                        'program_id': rec.program.id,
                                        'level_id': rec.level.id,
                                        'academic_year': rec.academic_year.id,
                                        'college_id': rec.college.id,
                                        'specialist_id': rec.specialist_id.id,
                                        'date': rec.result_date,
                                        'firest_semstar': rec.firest_semstar.id,
                                        'second_semstar': rec.second_semstar.id,
                                        'result_id': result.id,
                                    }
                                    absent = self.env['ums.absent'].create(absent_vals)
                                absent_line_first = self.env['first.absent.line'].search([
                                    ('subject_id', '=', t.subject.id),
                                    ('absent_id', '=', absent.id),
                                ], limit=1)
                                degree_letter = self.env['ums.division'].search([
                                    ('name', '=', t.degree_letter),
                                ], limit=1)
                                if not degree_letter:
                                    degree_vals = {
                                        'name': t.degree_letter
                                    }
                                    degree_letter = self.env['ums.division'].create(degree_vals)
                                if not absent_line_first:
                                    absent_line_first_vals = {
                                        'subject_id': t.subject.id,
                                        'pass_or_fail': t.pass_or_fail,
                                        'mark_scored': t.degree,
                                        'degree_letter': degree_letter.id,
                                        'absent_id': absent.id,
                                        'sub_first_id': t.id,
                                        'sub_first_regional_id': t.sub_id.id,
                                    }
                                    absent_line_first = self.env['first.absent.line'].create(absent_line_first_vals)
                                print('!!!!!!!!!!!MMMMMMMM!!!!!!!!!!!!!!', t.degree_letter)
                        elif rec.exam_type == 'supplement_exam':
                            portable = self.env['ums.portable'].search([
                                ('exam_name', '=', rec.name),
                                ('name', '=', line.student.id),
                                ('class_id', '=', rec.class_id.id),
                            ], limit=1)
                            if not portable:
                                portable_vals = {
                                    'exam_name': rec.name,
                                    'name': line.student.id,
                                    'class_id': rec.class_id.id,
                                    'department': rec.department.id,
                                    'program_id': rec.program.id,
                                    'level_id': rec.level.id,
                                    'academic_year': rec.academic_year.id,
                                    'college_id': rec.college.id,
                                    'specialist_id': rec.specialist_id.id,
                                    'date': rec.result_date,
                                    'firest_semstar': rec.firest_semstar.id,
                                    'second_semstar': rec.second_semstar.id,
                                    'result_id': result.id,
                                }
                                portable = self.env['ums.portable'].create(portable_vals)
                            portable_line_first = self.env['first.portable.line'].search([
                                ('subject_id', '=', t.subject.id),
                                ('portable_id', '=', portable.id),
                            ], limit=1)
                            degree_letter = self.env['ums.division'].search([
                                ('name', '=', t.degree_letter),
                            ], limit=1)
                            if not degree_letter:
                                degree_vals = {
                                    'name': t.degree_letter
                                }
                                degree_letter = self.env['ums.division'].create(degree_vals)
                            if not portable_line_first:
                                portable_line_first_vals = {
                                    'subject_id': t.subject.id,
                                    'pass_or_fail': t.pass_or_fail,
                                    'mark_scored': t.degree,
                                    'degree_letter': degree_letter.id,
                                    'portable_id': portable.id,
                                    'sub_first_id': t.id,
                                    'sub_first_regional_id': t.sub_id.id,
                                }
                                portable_line_first = self.env['first.portable.line'].create(portable_line_first_vals)
            for sec in rec.second_semester_result:
                for l in sec.subject_line:
                    history_second = self.env['ums.result.history'].search([
                        ('result_id', '=', result.id),
                        ('name', '=', sec.student.id),
                        ('class_id', '=', rec.class_id.id),
                    ], limit=1)
                    if not history_second:
                        history_vals_second = {
                            'result_id': result.id,
                            'name': sec.student.id,
                            'collage_id': rec.college.id,
                            'department_id': rec.department.id,
                            'program_id': rec.program.id,
                            'specialist_id': rec.specialist_id.id,
                            'level_id': rec.level.id,
                            'academic_year_id': rec.academic_year.id,
                            'date': rec.result_date,
                            'firest_semstar': rec.firest_semstar.id,
                            'second_semstar': rec.second_semstar.id,
                        }
                        history_second = self.env['ums.result.history'].create(history_vals_second)
                    history_line_second = self.env['second.result.history.line'].search([
                        ('subject_id', '=', l.subject.id),
                        ('history_id', '=', history_second.id),
                    ], limit=1)
                    degree_letter = self.env['ums.division'].search([
                        ('name', '=', l.degree_letter),
                    ], limit=1)
                    if not degree_letter:
                        degree_vals = {
                            'name': l.degree_letter
                        }
                        degree_letter = self.env['ums.division'].create(degree_vals)
                    if not history_line_second:
                        history_line_second_vals = {
                            'subject_id': l.subject.id,
                            'history_id': history_second.id,
                            'degree': l.degree,
                            'note': l.note,
                            'hours': l.hours,
                            'degree_letter': degree_letter.id,
                        }
                        history_line_second = self.env['second.result.history.line'].create(history_line_second_vals)
                    if not l.pass_or_fail:
                        if rec.exam_type == 'final':
                            supplement = self.env['ums.supplement'].search([
                                ('exam_name', '=', result.name),
                                ('name', '=', sec.student.id),
                                ('class_id', '=', rec.class_id.id),
                            ], limit=1)
                            if not supplement:
                                supplement_vals = {
                                    'exam_name': result.name,
                                    'name': sec.student.id,
                                    'class_id': rec.class_id.id,
                                    'department': rec.department.id,
                                    'program_id': rec.program.id,
                                    'level_id': rec.level.id,
                                    'academic_year': rec.academic_year.id,
                                    'college_id': rec.college.id,
                                    'specialist_id': rec.specialist_id.id,
                                    'date': rec.result_date,
                                    'firest_semstar': rec.firest_semstar.id,
                                    'second_semstar': rec.second_semstar.id,
                                    'result_id': result.id,
                                }
                                supplement = self.env['ums.supplement'].create(supplement_vals)
                            supplement_line_second = self.env['second.supplement.line'].search([
                                ('subject_id', '=', l.subject.id),
                                ('supplement_id', '=', supplement.id),
                            ], limit=1)
                            supplement.write({"second_semstar": rec.second_semstar.id})
                            degree_letter = self.env['ums.division'].search([
                                ('name', '=', l.degree_letter),
                            ], limit=1)
                            if not supplement_line_second:
                                supplement_line_second_vals = {
                                    'subject_id': l.subject.id,
                                    'pass_or_fail': l.pass_or_fail,
                                    'mark_scored': l.degree,
                                    'degree_letter': degree_letter.id,
                                    'supplement_id': supplement.id,
                                    'sub_second_id': l.id,
                                }
                                supplement_line_second = self.env['second.supplement.line'].create(
                                    supplement_line_second_vals)

                            if l.degree_letter == "غ":
                                absent = self.env['ums.absent'].search([
                                    ('exam_name', '=', rec.name),
                                    ('name', '=', sec.student.id),
                                    ('class_id', '=', rec.class_id.id),
                                ], limit=1)
                                if not absent:
                                    absent_vals = {
                                        'exam_name': rec.name,
                                        'name': sec.student.id,
                                        'class_id': rec.class_id.id,
                                        'department': rec.department.id,
                                        'program_id': rec.program.id,
                                        'level_id': rec.level.id,
                                        'academic_year': rec.academic_year.id,
                                        'college_id': rec.college.id,
                                        'specialist_id': rec.specialist_id.id,
                                        'date': rec.result_date,
                                        'firest_semstar': rec.firest_semstar.id,
                                        'second_semstar': rec.second_semstar.id,
                                        'result_id': result.id,
                                    }
                                    absent = self.env['ums.absent'].create(absent_vals)
                                absent_line_second = self.env['second.absent.line'].search([
                                    ('subject_id', '=', l.subject.id),
                                    ('absent_id', '=', absent.id),
                                ], limit=1)
                                absent.write({"second_semstar": rec.second_semstar.id})
                                degree_letter = self.env['ums.division'].search([
                                    ('name', '=', l.degree_letter),
                                ], limit=1)
                                if not degree_letter:
                                    degree_vals = {
                                        'name': l.degree_letter
                                    }
                                    degree_letter = self.env['ums.division'].create(degree_vals)
                                if not absent_line_second:
                                    absent_line_second_vals = {
                                        'subject_id': l.subject.id,
                                        'pass_or_fail': l.pass_or_fail,
                                        'mark_scored': l.degree,
                                        'degree_letter': degree_letter.id,
                                        'absent_id': absent.id,
                                        'sub_second_id': l.id,
                                        'sub_second_regional_id': l.sub_id.id,
                                    }
                                    absent_line_second = self.env['second.absent.line'].create(absent_line_second_vals)












                        elif rec.exam_type == 'supplement_exam':
                            portable = self.env['ums.portable'].search([
                                ('exam_name', '=', result.name),
                                ('name', '=', sec.student.id),
                                ('class_id', '=', rec.class_id.id),
                            ], limit=1)
                            if not portable:
                                portable_vals = {
                                    'exam_name': result.name,
                                    'name': sec.student.id,
                                    'class_id': rec.class_id.id,
                                    'department': rec.department.id,
                                    'program_id': rec.program.id,
                                    'level_id': rec.level.id,
                                    'academic_year': rec.academic_year.id,
                                    'college_id': rec.college.id,
                                    'specialist_id': rec.specialist_id.id,
                                    'date': rec.result_date,
                                    'firest_semstar': rec.firest_semstar.id,
                                    'second_semstar': rec.second_semstar.id,
                                    'result_id': result.id,
                                }
                                portable = self.env['ums.portable'].create(portable_vals)
                            portable_line_second = self.env['second.portable.line'].search([
                                ('subject_id', '=', l.subject.id),
                                ('portable_id', '=', portable.id),
                            ], limit=1)
                            portable.write({"second_semstar": rec.second_semstar.id})
                            degree_letter = self.env['ums.division'].search([
                                ('name', '=', l.degree_letter),
                            ], limit=1)
                            if not degree_letter:
                                degree_vals = {
                                    'name': l.degree_letter
                                }
                                degree_letter = self.env['ums.division'].create(degree_vals)
                            if not portable_line_second:
                                print("in if subject")
                                portable_line_second_vals = {
                                    'subject_id': l.subject.id,
                                    'pass_or_fail': l.pass_or_fail,
                                    'mark_scored': l.degree,
                                    'degree_letter': degree_letter.id,
                                    'portable_id': portable.id,
                                    'sub_second_id': l.id,
                                    'sub_second_regional_id': l.sub_id.id,
                                }
                                portable_line_second = self.env['second.portable.line'].create(
                                    portable_line_second_vals)

    # ======================Move Student==================#
    def move_to_next_semester(self):
        for rec in self:
            if rec.program:
                if rec.firest_semstar and not rec.second_semstar:
                    current_program_level = self.env["ums.program.level.line"].search(
                        [("program_id", '=', rec.program.id), ('level', '=', rec.level.id)], limit=1)
                    query_semester = _("""select semester_id,sem_seq from program_level_semester_line 
                                        where level_id = %s order by sem_seq asc; """) % (str(current_program_level.id))
                    self.env.cr.execute(query_semester)
                    level_semester_vals = self.env.cr.fetchall()
                    program_semester_id = [element[0] for element in level_semester_vals]
                    semester_index = program_semester_id.index((rec.firest_semstar.id))
                    print(semester_index)
                    if semester_index + 1 < len(program_semester_id):
                        next_semester_id = program_semester_id[semester_index + 1]
                        semester = self.env['ums.semester'].search([('id', '=', next_semester_id)], limit=1)
                        rec.class_id.semester_id = semester

                        # check if student not pass do action 
                        for student in rec.class_id.std_line_ids:
                            student.semester_id = semester
                elif rec.firest_semstar and rec.second_semstar:
                    query = _("""select level,level_seq from ums_program_level_line 
                                where program_id = %s order by level_seq asc;""") % (str(rec.program.id))
                    self.env.cr.execute(query)
                    program_level_vals = self.env.cr.fetchall()
                    program_level_id = [element[0] for element in program_level_vals]
                    level_index = program_level_id.index((rec.level.id))

                    if level_index + 1 < len(program_level_id):
                        next_level_id = program_level_id[level_index + 1]

                        level = self.env['ums.level'].search([('id', '=', next_level_id)], limit=1)
                        rec.class_id.level = level

                        current_program_level = self.env["ums.program.level.line"].search(
                            [("program_id", '=', rec.program.id), ('level', '=', next_level_id)], limit=1)
                        query_semester = _("""select semester_id,sem_seq from program_level_semester_line 
                                            where level_id = %s order by sem_seq asc; """) % (
                            str(current_program_level.id))
                        self.env.cr.execute(query_semester)
                        semester = self.env['ums.semester'].search([('id', '=', self.env.cr.fetchall()[0][0])], limit=1)
                        rec.class_id.semester_id = semester

                        # check if student not pass do action
                        for student in rec.class_id.std_line_ids:
                            student.level = level
                            student.semester_id = semester

                    else:
                        # this is the last level make students grade
                        current_program_level = self.env["ums.program.level.line"].search(
                            [("program_id", '=', rec.program.id), ('level', '=', program_level_id[level_index])],
                            limit=1)
                        if current_program_level.is_final:
                            wizard_model = self.env['grade.date.wizard']
                            vals = {
                                'result_id': rec.id
                            }
                            new = wizard_model.create(vals)
                            return {
                                'name': "This is Final year ,select grade date and press validate to confirm that "
                                        "and make students graduation",
                                'type': 'ir.actions.act_window',
                                'res_model': 'grade.date.wizard',
                                'res_id': new.id,
                                'view_id': self.env.ref('ums.view_grade_date_wizard', False).id,
                                'view_type': 'form',
                                'view_mode': 'form',
                                'target': 'new'
                            }

    def open_note_wizard(self):
        vals = {
            'result': self.id
        }
        new = self.env["note.wizard"].create(vals)
        return {
            'name': "Add note to all student in semester",
            'type': 'ir.actions.act_window',
            'res_model': 'note.wizard',
            'res_id': new.id,
            'view_id': self.env.ref('ums.view_note_wizard', False).id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }


class ResultNote(models.Model):
    _name = 'ums.result.note'
    _description = 'Result Note'

    note_id = fields.Many2one('ums.result', 'Result#')
    key = fields.Char("Key")
    note_select = fields.Many2one('ums.note.list', '#', required=True)
    note = fields.Char('Note')
    note_details = fields.Char('Note Details', required=True)
    note_en_details = fields.Char('Note English Details', required=True)
    note_second_id = fields.Many2one('ums.result.second')
    note_first_id = fields.Many2one('ums.result.first')

    @api.onchange('note_select')
    def change_note(self):
        for rec in self:
            rec.note = rec.note_select.note
            rec.note_details = rec.note_select.note_details
            rec.note_en_details = rec.note_select.note_en_details


class FirstSemesterResult(models.Model):
    _name = 'ums.result.first'
    _description = "Result of first semester in each year"

    result_id = fields.Many2one("ums.result", string="Result #")
    student = fields.Many2one("ums.student", string="Student")
    semster_degree = fields.Float("Semester degree", store=True, digits=(12, 2))
    # note = fields.Text("Note")
    subject_line = fields.One2many("result.subject.line", "first_result_id", string="Subject result")
    note_ids = fields.One2many('ums.result.note', 'note_first_id')
    student_status = fields.Many2one('ums.student.status', 'Student Status', readonly=True)
    class_id = fields.Many2one('ums.class', 'Class', readonly=True)
    semestar_pass_or_fail = fields.Boolean(string="Pass?")
    college_id = fields.Many2one(related='result_id.college', string="College")

    @api.onchange('subject_line')
    def _onchange_subject_line(self):
        for rec in self:
            rec.compute_semester_degree()


    def compute_semester_degree(self):
        for rec in self:
            # total_hours = 0
            # total_degree = 0
            # for subject in rec.subject_line:
            #     total_hours += subject.hours
            #     total_degree += (subject.hours / 10) * subject.degree
            #
            # if total_hours > 0:
            #     calculated_degree =  (total_degree / total_hours)
            #     rec.semster_degree = str(calculated_degree)

            # need a work in optimize rule make safe_eval instant of eval
            degrees = [line.degree for line in rec.subject_line]
            subject_hours = [line.hours for line in rec.subject_line]
            if rec.result_id.data_type == "new_data":
                rec.semster_degree = float(eval(self.result_id.college.python_code))


class SecondSemesterResult(models.Model):
    _name = 'ums.result.second'
    _description = "Result of second semester in each year"

    result_id = fields.Many2one("ums.result", string="Result #")
    student = fields.Many2one("ums.student", string="Student")
    semster_degree = fields.Float("Semester degree", digits=(12, 2))
    level_degree = fields.Float("Level degree", digits=(12, 2))
    # note = fields.Text("Note")
    note_ids = fields.One2many('ums.result.note', 'note_second_id')
    subject_line = fields.One2many("result.subject.line", "second_result_id", string="Subject result")
    student_status = fields.Many2one('ums.student.status', 'Student Status', readonly=True)
    class_id = fields.Many2one('ums.class', 'Class', readonly=True)
    semestar_pass_or_fail = fields.Boolean(string="Pass?")
    college_id = fields.Many2one(related='result_id.college', string="College")

    @api.onchange('subject_line')
    def _onchange_subject_line(self):
        for rec in self:
            rec.compute_semester_degree()

    def compute_semester_degree(self):
        for rec in self:
            # total_hours = 0
            # total_degree = 0
            # for subject in rec.subject_line:
            #     total_hours += subject.hours
            #     total_degree += (subject.hours / 10) * subject.degree
            #
            # if total_hours > 0:
            #     calculated_degree =  (total_degree / total_hours)
            #     rec.semster_degree = str(calculated_degree)

            # need a work in optimize rule make safe_eval instant of eval
            degrees = [line.degree for line in rec.subject_line]
            subject_hours = [line.hours for line in rec.subject_line]
            if rec.result_id.data_type == "new_data":
                rec.semster_degree = float(eval(self.result_id.college.python_code))
                rec.level_degree = float(eval(self.result_id.college.leveL_calculate))
                first_semester_degree = 0
                for line in rec.result_id.first_semester_result:
                    if line.student == rec.student:
                        first_semester_degree = line.semster_degree
                rec.level_degree = (first_semester_degree + rec.semster_degree)/2


class SubjectResult(models.Model):
    _name = "result.subject.line"
    _description = "subject result"

    first_result_id = fields.Many2one("ums.result.first", string="First semester result")
    second_result_id = fields.Many2one("ums.result.second", string="Second semester result")
    college_id = fields.Many2one(related='first_result_id.college_id', string="College")
    college = fields.Many2one(related='second_result_id.college_id', string="College")
    subject = fields.Many2one("ums.subject", string="Subject")
    degree = fields.Float("Degree")
    hours = fields.Integer(string='Hours')
    degree_letter = fields.Char("Degree in letter")
    pass_or_fail = fields.Boolean(string='Pass?', readonly=False)
    note = fields.Char("Note")
    sub_id = fields.Many2one('result.subject.line', string="ID")

    @api.onchange('subject')
    def subject_onchange(self):
        for rec in self:
            if rec.subject:
                rec.hours = rec.subject.hours

    # @api.onchange('college_id')
    # def onchange_college_id(self):
    #   for rec in self:
    #      return {'domain': {'subject': [('college_id', '=', rec.college_id.id)]}}

    # @api.onchange('college')
    # def onchange_college(self):
    #   for rec in self:
    #      return {'domain': {'subject': [('college_id', '=', rec.college.id)]}}
    # domain="['|',('college_id','=',college_id), ('college_id','=',college)]"
