import datetime
from odoo import fields, api, models, _


class AddDegreeWizard(models.TransientModel):
    _name = "add.degree.wizard"
    _description = "Add Degree Wizard"
    _rec_name = 'result_id'

    def default_get(self, fields):
        res = super(AddDegreeWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        brw_id = self.env['ums.result'].browse(int(active_id))
        if active_id:
            res['result_id'] = active_id
            res['collage_id'] = brw_id.college.id
            res['department_id'] = brw_id.department.id
            res['level_id'] = brw_id.level.id
            res['program_id'] = brw_id.program.id
            if brw_id.firest_semstar:
                res['select_semester'] = brw_id.firest_semstar.id
            if brw_id.firest_semstar and brw_id.second_semstar:
                res['select_semester'] = brw_id.second_semstar.id

        return res

    result_id = fields.Many2one('ums.result', string="Result", readonly=True)
    first_semester = fields.Many2one(related='result_id.firest_semstar')
    second_semester = fields.Many2one(related='result_id.second_semstar')
    select_semester = fields.Many2one('ums.semester', domain="[('id', 'in', (second_semester,first_semester))]",
                                      string="Select Semester")
    collage_id = fields.Many2one('ums.college', string="Collage", readonly=True)
    department_id = fields.Many2one('ums.department', string="Department", readonly=True)
    level_id = fields.Many2one('ums.level', string="Level", readonly=True)
    program_id = fields.Many2one('ums.program', string="Program", readonly=True)
    degree_line_ids = fields.One2many('add.degree.line', 'add_degree_id', string="Degree Line")

    def action_add_subject(self):
        for rec in self:
            result = rec.result_id
            if result:
                for items in result:
                    if items.firest_semstar == rec.select_semester:
                        vals = []
                        for record in items.first_semester_result:
                            for line in record.subject_line:
                                if line.subject.id not in vals:
                                    subject_vals = {
                                        'subject_id': line.subject.id,
                                        'add_degree_id': rec.id,
                                        # 'degree': (line.degree) + (rec.degree_line_ids.value)
                                    }
                                    subject = self.env['add.degree.line'].create(subject_vals)

                                    vals.append(line.subject.id)

                    elif items.second_semstar == rec.select_semester:
                        vals = []
                        for record in items.second_semester_result:
                            for line in record.subject_line:
                                if line.subject.id not in vals:
                                    subject_vals = {
                                        'subject_id': line.subject.id,
                                        'add_degree_id': rec.id,
                                        # 'degree': (line.degree) + (rec.degree_line_ids.value)
                                    }
                                    subject = self.env['add.degree.line'].create(subject_vals)

                                    vals.append(line.subject.id)

    def action_degree_update(self):
        for rec in self:
            query = False
            for line in rec.degree_line_ids:
                if rec.result_id.firest_semstar == rec.select_semester:
                    query = _("""select sub.id from result_subject_line as sub
                                join ums_result_first as first on first.id = sub.first_result_id
                                and first.result_id = '%s'
                                and sub.subject = '%s' """) % (rec.result_id.id, line.subject_id.id)
                if rec.result_id.second_semstar == rec.select_semester:
                    query = _("""select sub.id from result_subject_line as sub
                                join ums_result_second as second on second.id = sub.second_result_id
                                and second.result_id = '%s'
                                and sub.subject = '%s' """) % (rec.result_id.id, line.subject_id.id)
                if query:
                    self.env.cr.execute(query)
                    vals = self.env.cr.fetchall()
                    if vals:
                        for va in vals:
                            sub_obj = self.env['result.subject.line'].search([('id', '=', va[0])])
                            sub_obj.degree += line.value


class AddDegreeLineWizard(models.TransientModel):
    _name = "add.degree.line"
    _description = "Add Degree Line"

    subject_id = fields.Many2one('ums.subject', string="Subject", store=True)
    value = fields.Float(string="Value")
    add_degree_id = fields.Many2one('add.degree.wizard')
