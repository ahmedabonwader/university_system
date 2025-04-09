# -*- coding: utf-8 -*-
{
    'name': "UMS",

    'summary': """unvierstey management system""",

    'description': """
        Student result
    """,

    'version': '16.0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'project'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'data/sequnece_data.xml',

        'student/views/student_view.xml',
        'student/views/ums_transferred.xml',
        'faculty/views/faculty_view.xml',
        'registration/views/ums_registration.xml',

        'exam/views/exam_view.xml',
        'exam/views/exam_evaluation_view.xml',

        'result/views/result_view.xml',
        'result/views/result_history.xml',
        'result/views/supplement.xml',
        'result/views/portable.xml',
        'result/views/ums_absent.xml',
        'result/views/freezing_year.xml',
        'result/views/quitted.xml',
        # 'result/views/mark_sheet.xml',
        'settings/views/settings_view.xml',

        'settings/views/college_view.xml',
        'settings/views/department_view.xml',
        'settings/views/level_view.xml',
        'settings/views/academic_year_view.xml',
        'settings/views/ums_subject_view.xml',
        'settings/views/ums_division.xml',
        'settings/views/ums_letter_degree.xml',
        'settings/views/ums_note_list.xml',
        'settings/views/ums_semester.xml',
        'settings/views/ums_group.xml',
        'settings/views/ums_specialist.xml',
        'settings/views/ums_program_view.xml',
        'settings/views/ums_nationality.xml',
        'settings/views/class_view.xml',

        'result/views/request_certificate_view.xml',
        # 'wizard/ceritifcat_wizard_view.xml',
        'wizard/portable_wizard.xml',
        'wizard/grade_date_wizard.xml',
        'wizard/note_wizard_view.xml',
        'wizard/transferred_wizard.xml',

        'result/reports/print_certificate.xml',
        'result/reports/semester_result/semester_result.xml',
        'result/reports/semester_result/semester_result_wizard.xml',
        'result/reports/semester_result/print_result.xml',
        'result/reports/certificate_template/footer_template.xml',

        # ============================ Medical cetificate ====================
        'result/reports/certificate_template/medicine/bachelor_detials_arabic.xml',
        'result/reports/certificate_template/medicine/bachelor_detials_english.xml',

        # ==================== bachelor cretificate ===========================
        'result/reports/certificate_template/certificate/bachelor_arabic.xml',
        'result/reports/certificate_template/certificate/bachelor_english.xml',
        'result/reports/certificate_template/certificate/bachelor_arabic_degree.xml',
        'result/reports/certificate_template/certificate/bachelor_english_degree.xml',

        # ============================bachelor details level degree ==============
        'result/reports/certificate_template/certificate/level_transcript_english.xml',

        # 'result/reports/certificate_template/account/bachelor_detials_arabic_degree_college.xml',
        # 'result/reports/certificate_template/engineering/engineering_bachelor_detials_arabic.xml',
        # 'result/reports/certificate_template/engineering/engineering_bachelor_detials_english.xml',
        # 'result/reports/certificate_template/computer_and_engineering/comp_bachelor_detials_arabic.xml',
        # 'result/reports/certificate_template/computer_and_engineering/comp_bachelor_detials_english.xml',

        # ==================== eng and  comp certificate ============================
        'result/reports/certificate_template/computer_and_engineering/bachelor_detials_arabic.xml',
        'result/reports/certificate_template/computer_and_engineering/bachelor_detials_english.xml',

        # ======================== Education certificate =================================
        'result/reports/certificate_template/education/bachelor_detials_english_edu.xml',
        'result/reports/certificate_template/education/bachelor_detials_arabic_edu.xml',

        'result/reports/certificate_template/medical_certificate_four_years/medical_bachelor_details_english.xml',
        'result/reports/certificate_template/medical_certificate_four_years/medical_bachelor_details_arabic.xml',
        
        # ===================== Deploma certificate ====================================
        'result/reports/certificate_template/deploma/deploma_details_arabic.xml',
        'result/reports/certificate_template/deploma/deploma_details_english.xml',
        
        # 'result/reports/certificate_template/medical_certificate_four_years/text.xml',
        # 'result/reports/certificate_template/certificate/level_transcript_arabic.xml',
        'settings/views/menu.xml',
    ],
}
