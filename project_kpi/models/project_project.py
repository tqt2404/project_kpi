from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = 'project.project'

    is_kpi_plan = fields.Boolean(string='Là Kế hoạch KPI', default=False)

    year = fields.Char(
        string='Năm kế hoạch', 
        default=lambda self: str(fields.Date.today().year)
    )
    department_id = fields.Many2one('hr.department', string='Phòng ban')
    kpi_year_target = fields.Float(string='KPI mục tiêu năm')
    
    kpi_year_score = fields.Float(
        string='KPI đạt được',
        compute='_compute_kpi_year_score',
        store=True
    )
    kpi_completion_rate = fields.Float(
        string='Tỷ lệ hoàn thành (%)',
        compute='_compute_kpi_completion_rate',
        store=True
    )

    @api.depends('task_ids.kpi_score', 'task_ids.kpi_month')
    def _compute_kpi_year_score(self):
        for record in self:
            if record.is_kpi_plan:
                kpi_tasks = record.task_ids.filtered(lambda t: t.kpi_month)
                record.kpi_year_score = sum(kpi_tasks.mapped('kpi_score'))
            else:
                record.kpi_year_score = 0.0

    @api.depends('kpi_year_score', 'kpi_year_target')
    def _compute_kpi_completion_rate(self):
        for record in self:
            if record.kpi_year_target and record.kpi_year_target > 0:
                record.kpi_completion_rate = (record.kpi_year_score / record.kpi_year_target) * 100
            else:
                record.kpi_completion_rate = 0.0

    @api.constrains('kpi_year_target', 'is_kpi_plan')
    def _check_kpi_year_target(self):
        for record in self:
            if record.is_kpi_plan and record.kpi_year_target <= 0:
                raise ValidationError("KPI mục tiêu năm phải lớn hơn 0!")