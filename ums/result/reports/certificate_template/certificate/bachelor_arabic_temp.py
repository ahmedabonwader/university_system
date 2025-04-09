from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class BachelorArabic(models.AbstractModel):
    _name = 'report.ums.print_bachelor_arabic'

    @api.model
    def _get_report_values(self, docids, data=None):
        student = data['form']['student']
        details = data['form']['details']
        docs = []

        # query = _("""select distinct  r.id , r.result_date from ums_result as r
        #              join ums_result_first as f ON f.result_id = r.id
        #              join result_subject_line as s ON  s.first_result_id = f.id
        #              and s.student = %s
        #              and r.program = 'bsc' order by r.result_date""")%(str(student))
        # self.env.cr.execute(query)
        # vals = self.env.cr.fetchall()
        # if vals:
        #     result_ids = self.env["ums.result"]
        #     for va in vals:
        #         result_obj = self.env["ums.result"].search([("id","=",va[0])])
        #         result_ids += result_obj
        #
        student_obj = self.env['ums.student'].search([("id","=",student)])
        docs.append({
            'student': student_obj,
            'ac_name': self.env['ir.config_parameter'].get_param('ums.ac_name')
        })
        print (docs)
        return {
            'docs_data': docs,
        }