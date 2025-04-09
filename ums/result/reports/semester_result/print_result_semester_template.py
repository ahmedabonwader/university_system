from odoo import models, api, _


class BachelorDetails(models.AbstractModel):
    _name = 'report.ums.print_result'

    @api.model
    def _get_report_values(self, docids, data=None):
        result_id = data['form']['result']
        semester = data['form']['semester']
        print_type = data['form']['print_type']
        p_type = ""
        if print_type == 'letter':
            p_type = """sl.degree_letter"""
        elif print_type == 'number':
            p_type = """sl.degree"""
        result = self.env["ums.result"].search([('id', '=', result_id)])
        semester_id = self.env["ums.semester"].search([('id', '=', semester)])
        subject_list = []
        hours_list = []
        result_data = []
        std_result = []
        semester_name = ''
        if semester_id == result.firest_semstar:
            semester_name = result.firest_semstar.name
            query = _("""select distinct sub.name , sl.id , sub.hours from result_subject_line as sl
                        join ums_subject as sub  on sl.subject = sub.id 
                        and first_result_id = 
                        (select f.id from ums_result_first as f 
                        join ums_result as r on f.result_id = r.id and r.id = %s limit 1) order by sl.id asc""") % (
                str(result_id))
            self.env.cr.execute(query)
            vals = self.env.cr.fetchall()
            count = 1
            if vals:
                total_hours = 0
                hours_list.append("###")
                hours_list.append("عدد الساعات")
                for va in vals:
                    hours_list.append(int(va[2]))
                    total_hours += int(va[2])
                hours_list.append(total_hours)
                hours_list.append(" ")
                subject_list.append("الرقم")
                subject_list.append("إسم الطالب")
                for va in vals:
                    subject_list.append(va[0])
                # subject_list.append("معدل الفصل الدراسي")
                subject_list.append("معدل " + semester_name)
                subject_list.append("ملاحظات")
                query = _("""select std.name , f.student ,f.semster_degree from ums_result_first  as f
                            join ums_student as std on std.id = f.student
                            and f.result_id = %s order by std.name asc""") % (str(result_id))
                self.env.cr.execute(query)
                students_vals = self.env.cr.fetchall()

                if students_vals:
                    for sva in students_vals:
                        degree_list = []
                        degree_list.append(count)
                        degree_list.append(sva[0])
                        count += 1

                        query = _("""select %s, sl.id from ums_result_first  as f
                                    join result_subject_line as sl on sl.first_result_id = f.id
                                    and f.result_id = %s
                                    and f.student = %s order by sl.id asc""") % (p_type,str(result_id), str(sva[1]))
                        self.env.cr.execute(query)
                        subject_vals = self.env.cr.fetchall()
                        for s in subject_vals:
                            degree_list.append(s[0] if print_type == 'letter' else int(s[0]))
                        degree_list.append(sva[2])
                        degree_list.append(" ")
                        std_result.append(degree_list)
        elif semester_id == result.second_semstar:
            semester_name = result.second_semstar.name
            query = _("""select distinct sub.name , sl.id from result_subject_line as sl
                                   join ums_subject as sub  on sl.subject = sub.id 
                                   and second_result_id = 
                                   (select s.id from ums_result_second as s 
                                   join ums_result as r on s.result_id = r.id and r.id = %s limit 1) order by sl.id asc""") % (
                str(result_id))
            self.env.cr.execute(query)
            vals = self.env.cr.fetchall()
            count = 1
            if vals:
                subject_list.append("الرقم")
                subject_list.append("إسم الطالب")
                for va in vals:
                    subject_list.append(va[0])
                # subject_list.append("معدل الفصل الدراسي")
                subject_list.append("معدل " + semester_name)
                # subject_lis[0] if print_type == 'letter' else int(s[0])st.append("معدل المستوى")
                subject_list.append("معدل " + result.level.name)
                query = _("""select std.name , s.student ,s.semster_degree,s.level_degree from ums_result_second  as s
                                       join ums_student as std on std.id = s.student
                                       and s.result_id = %s order by std.name asc""") % (str(result_id))
                self.env.cr.execute(query)
                students_vals = self.env.cr.fetchall()

                if students_vals:
                    for sva in students_vals:
                        degree_list = []
                        degree_list.append(count)
                        degree_list.append(sva[0])
                        count += 1
                        query = _("""select %s, sl.id from ums_result_second  as s
                                               join result_subject_line as sl on sl.second_result_id = s.id
                                               and s.result_id = %s
                                               and s.student = %s order by sl.id asc""") % (p_type,str(result_id), str(sva[1]))
                        self.env.cr.execute(query)
                        subject_vals = self.env.cr.fetchall()
                        for s in subject_vals:
                            degree_list.append(s[0] if print_type == 'letter' else int(s[0]))
                        degree_list.append(sva[2])
                        degree_list.append(sva[3])
                        std_result.append(degree_list)

        result_data.append({
            'name': result.name,
            'college': result.college.name,
            'department': result.department.name,
            'program': result.program.name,
            'year': result.academic_year.name,
            'semester_name': semester_name,
            'hours_list': hours_list,
            'header': subject_list,
            'result_line': std_result
        })

        return {
            'docs_data': result_data,
        }
