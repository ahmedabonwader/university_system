from odoo import models, fields


class College(models.Model):
    _name = 'ums.college'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'University College'

    name = fields.Char('Name', required=True, help='College name')
    english_name = fields.Char(string='English Name', required=False, help='College name')

    department_ids = fields.One2many('ums.department', 'college_id', string='Departments')
    dean_name = fields.Char(string="Dean Name", tracking=True)
    dean_english_name = fields.Char(string="Dean English Name", tracking=True)
    registrar_name = fields.Char(string="Registrar Name", tracking=True)
    registrar_english_name = fields.Char(string="Registrar English Name", tracking=True)

    report_certificate_id = fields.Many2one('ir.actions.report', 'Arabic Certificate Details Template', tracking=True)
    en_report_certificate_id = fields.Many2one('ir.actions.report', 'English Certificate Details Template', tracking=True)
    certificate_id = fields.Many2one('ir.actions.report', 'Arabic Certificate Template', tracking=True)
    en_certificate_id = fields.Many2one('ir.actions.report', 'English Certificate Template', tracking=True)
    is_portable = fields.Boolean(string="Is Portable ?")
    is_final_result_letter = fields.Boolean(string="Is Final Result Letter ?")
    department = fields.Boolean(string="Department ?")
    specialist = fields.Boolean(string="Specialist ?")
    python_code = fields.Text("Semester rate Equation(Python Code)",
                              default="""sum([((h/10) * d) for d, h in zip(degrees, subject_hours)]) / sum([ h for h in subject_hours ])""")
    leveL_calculate = fields.Text("Level rate Equation(Python Code)",
                                  default="""sum([((h/10) * d) for d, h in zip(degrees, subject_hours)]) / sum([ h for h in subject_hours ])""")

    hours_repeat_percent = fields.Float("Hours repeat %")
    repeat_count = fields.Integer("Repeat Count")

    external_1_percent = fields.Float("Hours External 1 %")
    external_2_percent = fields.Float("Hours External 2 %")
    external_3_percent = fields.Float("Hours External 3 %")

    external_1_count = fields.Integer("External 1 Count")
    external_2_count = fields.Integer("External 2 Count")
    external_3_count = fields.Integer("External 3 Count")
    # @api.onchange('college_id')
    # def onchange_collage(self):
    #     if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
    #         domain = []
    #         user = self.env.user.collage_ids
    #         for item in user:
    #             domain.append(item.id)
    #         return {'domain': {'college_id': [('id', 'in', domain)]}}

    # python_code = fields.Text("Python Code", default="""
    #                                                 # Available variables:
    #                                                 #----------------------
    #                                                 # degrees: list containing the student degrees on semester subjects
    #                                                 # subject_hours: list containing the hours of semester subjects
    #                                                 # inputs: object containing the computed inputs.
    #
    #                                                 sum([((h/10) * d) for d, h in zip(degrees, subject_hours)])/
    #                                                 sum([ h for h in subject_hours ])
    #                                                 """)

