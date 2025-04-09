# -*- coding: utf-8 -*-
{
    'name': "Import Results",

    'summary': """Import old student results""",

    'description': """
        import old student results
    """,
    
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','ums'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/import_result_view.xml',
    ],
}
