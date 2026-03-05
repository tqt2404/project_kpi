{
    'name': 'Project KPI',
    'version': '1.2',
    'category': 'Project KPI',
    'sequence': 15,
    'summary': 'Project KPI Management',
    'description': "",
    'depends': [
        'base', 
        'project',
        'hr'
    ],
    'data': [
        'security/kpi_security.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/kpi_report_views.xml',
        'views/kpi_menus.xml',
        'views/kpi_dashboard_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'project_kpi/static/src/components/**/*.js',
            'project_kpi/static/src/components/**/*.xml',
            'project_kpi/static/src/components/**/*.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False
}