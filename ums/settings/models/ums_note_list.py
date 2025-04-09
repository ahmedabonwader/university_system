from odoo import models, fields


class StudentNoteList(models.Model):
    _name = 'ums.note.list'
    _description = "Ums Note List"
    _rec_name = 'note'

    note = fields.Char('Note', required=True)
    note_details = fields.Char('Note Details', required=True)
    note_en_details = fields.Char('Note English Details', required=True)
    