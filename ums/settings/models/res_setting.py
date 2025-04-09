from odoo import models, fields


class InheritResSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    ac_name = fields.Char('Academic Secretary Arabic', config_parameter='ums.ac_name')
    ac_name_en = fields.Char('Academic Secretary English', config_parameter='ums.ac_name_en')
