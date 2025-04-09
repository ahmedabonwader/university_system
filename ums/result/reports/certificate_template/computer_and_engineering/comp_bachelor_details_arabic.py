from odoo import models, api, _
from odoo.exceptions import ValidationError


# try:
#         self.env.cr.execute(query)
#         vals = self.env.cr.fetchall()
#         return vals
#     except Exception as e:
# raise Warning(_('An error occurred during the execution of the query.') + str(e))
def stars(count=0):
    star = ""
    for x in range(count):
        star += "*"

    return star

class BachelorDetails(models.AbstractModel):
    _name = 'report.ums.print_bachelor_details_arabic_computer'

    @api.model
    def _get_report_values(self, docids, data=None):
        student = data['form']['student']
        certificate_data = []
        name = ''
        student_number = ''
        final_result = ''
        degree_letter = ''
        grade_date = ''
        college = ''
        program = ''
        nationality_id = ''
        college_dean = ''
        college_register = ''
        ac_name = self.env['ir.config_parameter'].get_param('ums.ac_name')

        query = _("""select std.name , std.student_number , std.final_result , std.grade_date ,
                    program.name ,nation.name, college.name,college.dean_name,college.registrar_name,
                    degree.name
                    from ums_student as std
                    join ums_college as college ON college.id = std.college_id
                    join ums_program as program ON program.id = std.program
                    join ums_nationality as nation ON nation.id = std.nationality_id
                    join ums_letter_degree as degree on degree.id = std.final_result_letter
                    and std.program IS NOT NULL and std.nationality_id IS NOT NULL 
                    and std.grade_date IS NOT NULL and std.id = %s """) % (
            str(student))  # and r.program = 'bsc'
        self.env.cr.execute(query)
        vals = self.env.cr.fetchall()

        if vals:
            for va in vals:
                name = va[0]
                student_number = va[1]
                final_result = va[2]
                grade_date = va[3].strftime("%Y/%m/%d")
                program = va[4]
                nationality_id = va[5]
                college = va[6]
                college_dean = va[7]
                college_register = va[8]
                degree_letter = va[9]

            query = _("""select distinct r.result_date , r.name , level.name , academic_year.name , one.id , two.id , 
                        r.id , semester_one.name , semester_two.name,
                        r.first_semester_n,r.second_semester_n
                        from ums_result_first as one
                        join ums_result_second as two on two.student = %s and one.student = %s 
                        join ums_result as r on one.result_id = r.id and two.result_id = r.id
                        join ums_level as level on level.id = r.level
                        join ums_academic_year as academic_year on academic_year.id = r.academic_year
                        join ums_semester as semester_one on semester_one.id = r.firest_semstar
                        join ums_semester as semester_two on semester_two.id = r.second_semstar
                        order by r.result_date """) % (str(student), str(student))  # and r.program = 'bsc'
            self.env.cr.execute(query)
            vals = self.env.cr.fetchall()
            result_list = []
            notes_details = []
            stars_count = 0
            if vals:
                for va in vals:
                    first_result_obj = self.env["ums.result.first"].search([("id", "=", va[4])])
                    second_result_obj = self.env["ums.result.second"].search([("id", "=", va[5])])

                    first_row_count = self.env["result.subject.line"].search_count(
                        [("first_result_id", "=", first_result_obj.id)])
                    second_row_count = self.env["result.subject.line"].search_count(
                        [("second_result_id", "=", second_result_obj.id)])
                    count = first_row_count - second_row_count
                    if count > 0:
                        first_row_count = 0
                        second_row_count = count
                    elif count < 0:
                        first_row_count = count * -1
                        second_row_count = 0
                    elif count == 0:
                        first_row_count = 0
                        second_row_count = 0

                    query = _("""select note.note , note.note_details
                                             from ums_result_note as note
                                             where note.note_id = %s """) % (str(va[6]))
                    self.env.cr.execute(query)
                    notes = self.env.cr.fetchall()
                    note = []
                    for n in notes:
                        stars_count += 1
                        note.append({'key': stars(stars_count), 'note': n[0] if n[0] else "" + '\n'})
                        notes_details.append({
                            'key': stars(stars_count),
                            'value': n[1],
                        })
                    query = _("""select note.note , note.note_details
                                         from ums_result_note as note
                                         where note.note_first_id = %s """) % (str(first_result_obj.id))
                    self.env.cr.execute(query)
                    notes = self.env.cr.fetchall()
                    first_note = []
                    for n in notes:
                        stars_count += 1
                        first_note.append({'key': stars(stars_count), 'note': n[0] if n[0] else "" + '\n'})
                        notes_details.append({
                            'key': stars(stars_count),
                            'value': n[1],
                        })

                    query = _("""select  note.note , note.note_details
                                         from ums_result_note as note
                                         where note.note_second_id = %s """) % (str(second_result_obj.id))
                    self.env.cr.execute(query)
                    notes = self.env.cr.fetchall()
                    second_note = []
                    for n in notes:
                        note_in_first = False
                        stars_str = ""
                        for f_note in first_note:
                            if n[0] and n[0] == f_note['note']:
                                note_in_first = True
                                stars_str = f_note["key"]
                        if not note_in_first:
                            stars_count += 1
                            stars_str = stars(stars_count)

                        second_note.append({'key': stars_str, 'note': n[0] if n[0] else "" + '\n'})
                        notes_details.append({
                            'key': stars_str,
                            'value': n[1],
                        })

                    result_list.append({
                        'level': va[2],
                        'academic_year': va[3],
                        'first': first_result_obj,
                        'second': second_result_obj,
                        'first_semester_name': va[7],
                        'second_semester_name': va[8],
                        'first_semester_n': va[9],
                        'second_semester_n': va[10],
                        'first_semester_note': first_note,
                        'second_semester_note': second_note,
                        'first_row_count': first_row_count,
                        'second_row_count': second_row_count,
                        'note': note,
                    })

                # in last of certificate page when need to show note list without duplicated
                note_keys = [element['key'] for element in notes_details]
                notes_list = []
                uniqe_key = []
                for k in note_keys:
                    if k not in uniqe_key:
                        uniqe_key.append(k)

                for key in uniqe_key:
                    for note in notes_details:
                        if key == note['key']:
                            notes_list.append(note)
                            break

                query = _("""select name, maximum_marks, minimum_marks
                                from ums_division order by maximum_marks desc""")
                # where division.college_id = %s """) % (str(college))
                self.env.cr.execute(query)
                division = self.env.cr.fetchall()
                division_details = []
                for division in division:
                    division_details.append({
                        'name': division[0],
                        'max': division[1],
                        'min': division[2],
                    })

                certificate_data.append({
                    'name': name,
                    'student_number': student_number,
                    'final_result': final_result,
                    'degree_letter': degree_letter,
                    'grade_date': grade_date,
                    'program': program,
                    'nationality_id': nationality_id,
                    'results': result_list,
                    'college': college,
                    'college_dean': college_dean,
                    'college_register': college_register,
                    'ac_name': ac_name,
                    'notes_details': notes_list,
                    'division': division_details,
                })

            return {
                'docs_data': certificate_data,
            }

        else:
            raise ValidationError(_("Somethings Wrong can't completed"))
