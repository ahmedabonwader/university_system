# -*- coding: utf-8 -*-

from odoo import models, fields


def strip_string(word):

    return str(word).strip()


class Result(models.Model):
    _name = 'ums.import.result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Import old results"
    _order = 'id desc'

    name = fields.Char(string="Result Name", required=True)
    specialist = fields.Char(string="Specialist")
    college = fields.Char(string="College", required=True)
    department = fields.Char(string="Department", required=True)
    level = fields.Char(string="Level", required=True)
    academic_year = fields.Char(string="Academic Year")
    classes = fields.Char(string="Class")
    program = fields.Char(string="Program")
    result_date = fields.Date(string="Date", required=False)
    first_semester_result = fields.One2many("import.result.first", "result_id", string="First semester")
    second_semester_result = fields.One2many("import.result.second", "result_id", string="Second semester")
    firest_semstar = fields.Char('First Semstar')
    second_semstar = fields.Char('Second Semstar')

    def search_create_subject(self, name, college, hours):
        sub_obj = self.env['ums.subject'].search([('name', '=', strip_string(name)), ('college_id', '=', college.id)], limit=1)
        if not sub_obj:
            subject_vals = {
                'name': strip_string(name),
                'college_id': college.id,
                'hours': int(hours)
            }
            sub_obj = self.env['ums.subject'].create(subject_vals)

        return sub_obj

    def create_update_subject_degree(self, subject, degree, degree_letter, hours, first_result_id=False,
                                     second_result_id=False):
        existing_subject_line = self.env['result.subject.line'].search([
            ('subject', '=', subject.id),
            ('first_result_id', '=', first_result_id.id if first_result_id else first_result_id),
            ('second_result_id', '=', second_result_id.id if second_result_id else second_result_id),
        ])
        if not existing_subject_line:
            if degree:
                subject_result_vals = {
                    'subject': subject.id,
                    'degree': float(degree),
                    'degree_letter': strip_string(degree_letter),
                    'hours': int(hours),
                    'first_result_id': first_result_id.id if first_result_id else first_result_id,
                    'second_result_id': second_result_id.id if second_result_id else second_result_id,
                }
                existing_subject_line = self.env['result.subject.line'].create(
                    subject_result_vals)
        else:
            existing_subject_line.write({"degree": float(degree), "degree_letter": strip_string(degree_letter), "hours": int(hours), })
        return existing_subject_line

    def get_students_result(self):
        for record in self:
            # first Semester
            college = self.env['ums.college'].search([('name', '=',strip_string(record.college))], limit=1)
            if not college:
                vals = {
                    "name": strip_string(record.college),
                }
                college = self.env['ums.college'].create(vals)
            first_sem = self.env['ums.semester'].search(
                [('name', '=', strip_string(record.firest_semstar)), ('college_id', '=', college.id)], limit=1)
            if not first_sem:
                first_sem_vals = {
                    'name': strip_string(record.firest_semstar),
                    'college_id': college.id,
                }
                first_sem = self.env['ums.semester'].create(first_sem_vals)
            second_sem = self.env['ums.semester'].search(
                [('name', '=', strip_string(record.second_semstar)), ('college_id', '=', college.id)], limit=1)
            if not second_sem:
                second_sem_vals = {
                    'name': strip_string(record.second_semstar),
                    'college_id': college.id,
                }
                second_sem = self.env['ums.semester'].create(second_sem_vals)
            department = self.env['ums.department'].search(
                [('name', '=', strip_string(record.department)), ('college_id', '=', college.id)], limit=1)
            if not department:
                vals_1 = {
                    'name': strip_string(record.department),
                    'college_id': college.id,
                }
                department = self.env['ums.department'].create(vals_1)
            level = self.env['ums.level'].search([('name', '=', strip_string(record.level)), ('college_id', '=', college.id)],
                                                 limit=1)
            if not level:
                vals_2 = {
                    'name': strip_string(record.level),
                    'college_id': college.id,
                }
                level = self.env['ums.level'].create(vals_2)
            academic_year = self.env['ums.academic.year'].search(
                [('name', '=', strip_string(record.academic_year)), ('college_id', '=', college.id)], limit=1)
            if not academic_year:
                vals_3 = {
                    'name': strip_string(record.academic_year),
                    'college_id': college.id,
                }
                academic_year = self.env['ums.academic.year'].create(vals_3)

            specialist_id = False
            if record.specialist:
                specialist_id = self.env['ums.specialist'].search(
                    [('name', '=', strip_string(record.specialist)), ('college_id', '=', college.id)], limit=1)
                if not specialist_id:
                    specialist_vals = {
                        'name': strip_string(record.specialist),
                        'department_id': department.id,
                        'college_id': college.id,
                    }
                    specialist_id = self.env['ums.specialist'].create(specialist_vals)
            program = self.env['ums.program'].search(
                [('name', '=', strip_string(record.program)), ('college', '=', college.id)],
                limit=1)
            if not program:
                program_vals = {
                    'name': strip_string(record.program),
                    'college': college.id,
                    'department': department.id,
                }
                program = self.env['ums.program'].create(program_vals)
            class_record = False
            if specialist_id:
                class_record = self.env['ums.class'].search(
                    [('name', '=', strip_string(record.classes)), ('college_id', '=', college.id),
                     ('specialist_id', '=', specialist_id.id)], limit=1)
            else:
                class_record = self.env['ums.class'].search(
                    [('name', '=', strip_string(record.classes)), ('college_id', '=', college.id)], limit=1)

            if not class_record:
                class_vals = {
                    'name': strip_string(record.classes),
                    'college_id': college.id,
                    'department_id': department.id,
                    'level': level.id,
                    'academic_year': academic_year.id,
                    'program_id': program.id,
                    'specialist_id': specialist_id.id if specialist_id else specialist_id,
                }
                class_record = self.env['ums.class'].create(class_vals)
            else:
                class_record.write({"level": level.id, "academic_year": academic_year.id})

            result = self.env["ums.result"].search([('name', '=', strip_string(record.name)),
                                                    ('college', '=', college.id),
                                                    ("class_id", "=", class_record.id)], limit=1)
            if not result:
                vals_4 = {
                    'state': 'old',
                    'name': strip_string(record.name),
                    'college': college.id,
                    'department': department.id,
                    'level': level.id,
                    'academic_year': academic_year.id,
                    'class_id': class_record.id,
                    'program': program.id,
                    'exam_type': 'final',
                    'result_date': record.result_date,
                    'firest_semstar': first_sem.id,
                    'second_semstar': second_sem.id,
                    'specialist_id': specialist_id.id if specialist_id else specialist_id,
                }
                result = self.env['ums.result'].create(vals_4)

            sub1_obj = False
            sub2_obj = False
            sub3_obj = False
            sub4_obj = False
            sub5_obj = False
            sub6_obj = False
            sub7_obj = False
            sub8_obj = False
            sub9_obj = False
            sub10_obj = False

            sub1_hours = 0
            sub2_hours = 0
            sub3_hours = 0
            sub4_hours = 0
            sub5_hours = 0
            sub6_hours = 0
            sub7_hours = 0
            sub8_hours = 0
            sub9_hours = 0
            sub10_hours = 0
            for rec in record.first_semester_result:

                if rec.student_name == 'الاسم':
                    if rec.subject_1:
                        sub1_hours = int(rec.subject_1_letter) if rec.subject_1_letter else False
                        sub1_obj = record.search_create_subject(rec.subject_1, college, sub1_hours)
                    if rec.subject_2:
                        sub2_hours = int(rec.subject_2_letter) if rec.subject_2_letter else False
                        sub2_obj = record.search_create_subject(rec.subject_2, college, sub2_hours)
                    if rec.subject_3:
                        sub3_hours = int(rec.subject_3_letter) if rec.subject_3_letter else False
                        sub3_obj = record.search_create_subject(rec.subject_3, college, sub3_hours)
                    if rec.subject_4:
                        sub4_hours = int(rec.subject_4_letter) if rec.subject_4_letter else False
                        sub4_obj = record.search_create_subject(rec.subject_4, college, sub4_hours)
                    if rec.subject_5:
                        sub5_hours = int(rec.subject_5_letter) if rec.subject_5_letter else False
                        sub5_obj = record.search_create_subject(rec.subject_5, college, sub5_hours)
                    if rec.subject_6:
                        sub6_hours = int(rec.subject_6_letter) if rec.subject_6_letter else False
                        sub6_obj = record.search_create_subject(rec.subject_6, college, sub6_hours)
                    if rec.subject_7:
                        sub7_hours = int(rec.subject_7_letter) if rec.subject_7_letter else False
                        sub7_obj = record.search_create_subject(rec.subject_7, college, sub7_hours)
                    if rec.subject_8:
                        sub8_hours = int(rec.subject_8_letter) if rec.subject_8_letter else False
                        sub8_obj = record.search_create_subject(rec.subject_8, college, sub8_hours)
                    if rec.subject_9:
                        sub9_hours = int(rec.subject_9_letter) if rec.subject_9_letter else False
                        sub9_obj = record.search_create_subject(rec.subject_9, college, sub9_hours)
                    if rec.subject_10:
                        sub10_hours = int(rec.subject_10_letter) if rec.subject_10_letter else False
                        sub10_obj = record.search_create_subject(rec.subject_10, college, sub10_hours)
                if rec.student_name != 'الاسم':
                    student = self.env['ums.student'].search([('name', '=', strip_string(rec.student_name)),
                                                    ('student_number','=',strip_string(rec.student_number))])
                    if not student:
                        vals_5 = {
                            'state': 'old',
                            'name': strip_string(rec.student_name),
                            'college_id': college.id,
                            'department': department.id,
                            'level': level.id,
                            'academic_year': academic_year.id,
                            'program': program.id,
                            'class_id': class_record.id,
                            'student_number': strip_string(rec.student_number),
                            'specialist_id': specialist_id.id if specialist_id else specialist_id,
                        }
                        student = self.env['ums.student'].create(vals_5)
                    else:
                        student.write({"level": level.id})

                    result_line_first = self.env['ums.result.first'].search(
                        [('student', '=', student.id), ('result_id', '=', result.id)])
                    if not result_line_first:
                        vals_6 = {
                            'student': student.id,
                            'semster_degree': rec.semster_degree,
                            'result_id': result.id
                        }
                        result_line_first = self.env['ums.result.first'].create(vals_6)

                    if result_line_first:
                        if sub1_obj and rec.subject_1:
                            record.create_update_subject_degree(sub1_obj, rec.subject_1, rec.subject_1_letter,
                                                                sub1_hours, first_result_id=result_line_first)
                        if sub2_obj and rec.subject_2:
                            record.create_update_subject_degree(sub2_obj, rec.subject_2, rec.subject_2_letter,
                                                                sub2_hours, first_result_id=result_line_first)
                        if sub3_obj and rec.subject_3:
                            record.create_update_subject_degree(sub3_obj, rec.subject_3, rec.subject_3_letter,
                                                                sub3_hours, first_result_id=result_line_first)
                        if sub4_obj and rec.subject_4:
                            record.create_update_subject_degree(sub4_obj, rec.subject_4, rec.subject_4_letter,
                                                                sub4_hours, first_result_id=result_line_first)
                        if sub5_obj and rec.subject_5:
                            record.create_update_subject_degree(sub5_obj, rec.subject_5, rec.subject_5_letter,
                                                                sub5_hours, first_result_id=result_line_first)
                        if sub6_obj and rec.subject_6:
                            record.create_update_subject_degree(sub6_obj, rec.subject_6, rec.subject_6_letter,
                                                                sub6_hours, first_result_id=result_line_first)
                        if sub7_obj and rec.subject_7:
                            record.create_update_subject_degree(sub7_obj, rec.subject_7, rec.subject_7_letter,
                                                                sub7_hours, first_result_id=result_line_first)
                        if sub8_obj and rec.subject_8:
                            record.create_update_subject_degree(sub8_obj, rec.subject_8, rec.subject_8_letter,
                                                                sub8_hours, first_result_id=result_line_first)
                        if sub9_obj and rec.subject_9:
                            record.create_update_subject_degree(sub9_obj, rec.subject_9, rec.subject_9_letter,
                                                                sub9_hours, first_result_id=result_line_first)
                        if sub10_obj and rec.subject_10:
                            record.create_update_subject_degree(sub10_obj, rec.subject_10, rec.subject_10_letter,
                                                                sub10_hours, first_result_id=result_line_first)

            sub1_obj = False
            sub2_obj = False
            sub3_obj = False
            sub4_obj = False
            sub5_obj = False
            sub6_obj = False
            sub7_obj = False
            sub8_obj = False
            sub9_obj = False
            sub10_obj = False

            sub1_hours = 0
            sub2_hours = 0
            sub3_hours = 0
            sub4_hours = 0
            sub5_hours = 0
            sub6_hours = 0
            sub7_hours = 0
            sub8_hours = 0
            sub9_hours = 0
            sub10_hours = 0
            # Second Semester
            for rec in record.second_semester_result:

                if rec.student_name == 'الاسم':
                    if rec.subject_1:
                        sub1_hours = int(rec.subject_1_letter) if rec.subject_1_letter else False
                        sub1_obj = record.search_create_subject(rec.subject_1, college, sub1_hours)
                    if rec.subject_2:
                        sub2_hours = int(rec.subject_2_letter) if rec.subject_2_letter else False
                        sub2_obj = record.search_create_subject(rec.subject_2, college, sub2_hours)
                    if rec.subject_3:
                        sub3_hours = int(rec.subject_3_letter) if rec.subject_3_letter else False
                        sub3_obj = record.search_create_subject(rec.subject_3, college, sub3_hours)
                    if rec.subject_4:
                        sub4_hours = int(rec.subject_4_letter) if rec.subject_4_letter else False
                        sub4_obj = record.search_create_subject(rec.subject_4, college, sub4_hours)
                    if rec.subject_5:
                        sub5_hours = int(rec.subject_5_letter) if rec.subject_5_letter else False
                        sub5_obj = record.search_create_subject(rec.subject_5, college, sub5_hours)
                    if rec.subject_6:
                        sub6_hours = int(rec.subject_6_letter) if rec.subject_6_letter else False
                        sub6_obj = record.search_create_subject(rec.subject_6, college, sub6_hours)
                    if rec.subject_7:
                        sub7_hours = int(rec.subject_7_letter) if rec.subject_7_letter else False
                        sub7_obj = record.search_create_subject(rec.subject_7, college, sub7_hours)
                    if rec.subject_8:
                        sub8_hours = int(rec.subject_8_letter) if rec.subject_8_letter else False
                        sub8_obj = record.search_create_subject(rec.subject_8, college, sub8_hours)
                    if rec.subject_9:
                        sub9_hours = int(rec.subject_9_letter) if rec.subject_9_letter else False
                        sub9_obj = record.search_create_subject(rec.subject_9, college, sub9_hours)
                    if rec.subject_10:
                        sub10_hours = int(rec.subject_10_letter) if rec.subject_10_letter else False
                        sub10_obj = record.search_create_subject(rec.subject_10, college, sub10_hours)

                if rec.student_name != 'الاسم':
                    student = self.env['ums.student'].search([('name', '=', strip_string(rec.student_name)),
                                                    ('student_number', '=', strip_string(rec.student_number))])
                    if not student:
                        student_vals = {
                            'state': 'old',
                            'name': strip_string(rec.student_name),
                            'college_id': college.id,
                            'department': department.id,
                            'level': level.id,
                            'academic_year': academic_year.id,
                            'program': program.id,
                            'class_id': class_record.id,
                            'student_number': strip_string(rec.student_number),
                            'specialist_id': specialist_id.id if specialist_id else specialist_id,
                        }
                        student = self.env['ums.student'].create(student_vals)
                    else:
                        student.write({"level": level.id})

                    second_result = self.env['ums.result.second'].search(
                        [('student', '=', student.id), ('result_id', '=', result.id)], limit=1)
                    if not second_result:
                        second_result_vals = {
                            'student': student.id,
                            'semster_degree': rec.semster_degree,
                            'level_degree': rec.level_degree,
                            'result_id': result.id
                        }
                        second_result = self.env['ums.result.second'].create(second_result_vals)

                    if second_result:
                        if sub1_obj and rec.subject_1:
                            record.create_update_subject_degree(sub1_obj, rec.subject_1, rec.subject_1_letter,
                                                                sub1_hours, second_result_id=second_result)
                        if sub2_obj and rec.subject_2:
                            record.create_update_subject_degree(sub2_obj, rec.subject_2, rec.subject_2_letter,
                                                                sub2_hours, second_result_id=second_result)
                        if sub3_obj and rec.subject_3:
                            record.create_update_subject_degree(sub3_obj, rec.subject_3, rec.subject_3_letter,
                                                                sub3_hours, second_result_id=second_result)
                        if sub4_obj and rec.subject_4:
                            record.create_update_subject_degree(sub4_obj, rec.subject_4, rec.subject_4_letter,
                                                                sub4_hours, second_result_id=second_result)
                        if sub5_obj and rec.subject_5:
                            record.create_update_subject_degree(sub5_obj, rec.subject_5, rec.subject_5_letter,
                                                                sub5_hours, second_result_id=second_result)
                        if sub6_obj and rec.subject_6:
                            record.create_update_subject_degree(sub6_obj, rec.subject_6, rec.subject_6_letter,
                                                                sub6_hours, second_result_id=second_result)
                        if sub7_obj and rec.subject_7:
                            record.create_update_subject_degree(sub7_obj, rec.subject_7, rec.subject_7_letter,
                                                                sub7_hours, second_result_id=second_result)
                        if sub8_obj and rec.subject_8:
                            record.create_update_subject_degree(sub8_obj, rec.subject_8, rec.subject_8_letter,
                                                                sub8_hours, second_result_id=second_result)
                        if sub9_obj and rec.subject_9:
                            record.create_update_subject_degree(sub9_obj, rec.subject_9, rec.subject_9_letter,
                                                                sub9_hours, second_result_id=second_result)
                        if sub10_obj and rec.subject_10:
                            record.create_update_subject_degree(sub10_obj, rec.subject_10, rec.subject_10_letter,
                                                                sub10_hours, second_result_id=second_result)


class FirstSemesterResult(models.Model):
    _name = 'import.result.first'
    _description = "import Result of first semester in each year"

    result_id = fields.Many2one("ums.import.result", string="Result #")

    student_name = fields.Char(string="Student name")
    student_number = fields.Char(string="Student Number")

    subject_1 = fields.Char(string="Subject 1")
    subject_2 = fields.Char(string="Subject 2")
    subject_3 = fields.Char(string="Subject 3")
    subject_4 = fields.Char(string="Subject 4")
    subject_5 = fields.Char(string="Subject 5")
    subject_6 = fields.Char(string="Subject 6")
    subject_7 = fields.Char(string="Subject 7")
    subject_8 = fields.Char(string="Subject 8")
    subject_9 = fields.Char(string="Subject 9")
    subject_10 = fields.Char(string="Subject 10")

    subject_1_letter = fields.Char(string="Subject 1 letter")
    subject_2_letter = fields.Char(string="Subject 2 letter")
    subject_3_letter = fields.Char(string="Subject 3 letter")
    subject_4_letter = fields.Char(string="Subject 4 letter")
    subject_5_letter = fields.Char(string="Subject 5 letter")
    subject_6_letter = fields.Char(string="Subject 6 letter")
    subject_7_letter = fields.Char(string="Subject 7 letter")
    subject_8_letter = fields.Char(string="Subject 8 letter")
    subject_9_letter = fields.Char(string="Subject 9 letter")
    subject_10_letter = fields.Char(string="Subject 10 letter")
    semster_degree = fields.Char("Semester degree")
    note = fields.Text("Note")


class SecondSemesterResult(models.Model):
    _name = 'import.result.second'
    _description = "import Result of second semester in each year"

    result_id = fields.Many2one("ums.import.result", string="Result #")

    student_name = fields.Char(string="Student name")
    student_number = fields.Char(string="Student Number")

    subject_1 = fields.Char(string="Subject 1")
    subject_2 = fields.Char(string="Subject 2")
    subject_3 = fields.Char(string="Subject 3")
    subject_4 = fields.Char(string="Subject 4")
    subject_5 = fields.Char(string="Subject 5")
    subject_6 = fields.Char(string="Subject 6")
    subject_7 = fields.Char(string="Subject 7")
    subject_8 = fields.Char(string="Subject 8")
    subject_9 = fields.Char(string="Subject 9")
    subject_10 = fields.Char(string="Subject 10")

    subject_1_letter = fields.Char(string="Subject 1 letter")
    subject_2_letter = fields.Char(string="Subject 2 letter")
    subject_3_letter = fields.Char(string="Subject 3 letter")
    subject_4_letter = fields.Char(string="Subject 4 letter")
    subject_5_letter = fields.Char(string="Subject 5 letter")
    subject_6_letter = fields.Char(string="Subject 6 letter")
    subject_7_letter = fields.Char(string="Subject 7 letter")
    subject_8_letter = fields.Char(string="Subject 8 letter")
    subject_9_letter = fields.Char(string="Subject 9 letter")
    subject_10_letter = fields.Char(string="Subject 10 letter")

    semster_degree = fields.Char("Semester degree")
    level_degree = fields.Char(string="Level Degree")
    note = fields.Text("Note")
