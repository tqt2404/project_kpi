from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = 'project.project'

    is_kpi_plan = fields.Boolean(string='Là Kế hoạch KPI', default=False)

    @api.model
    def _get_year_selection(self):
        current_year = fields.Date.context_today(self).year
        return [(str(y), str(y)) for y in range(2020, current_year + 6)]
    
    year = fields.Selection(
        selection='_get_year_selection',
        string='Năm kế hoạch', 
        default=lambda self: str(fields.Date.context_today(self).year)
    )
    
    department_id = fields.Many2one('hr.department', string='Phòng ban')
    kpi_year_target = fields.Float(string='KPI mục tiêu năm')
    
    kpi_year_actual = fields.Float(
        string='Tổng KPI thực tế năm',
        compute='_compute_kpi_year_score',
        store=True
    )

    kpi_year_score = fields.Float(
        string='KPI đạt được(Điểm)',
        compute='_compute_kpi_year_score',
        store=True
    )

    kpi_allocated_weight = fields.Float(
        string='Tổng trọng số đã giao (%)',
        compute='_compute_kpi_allocated_weight',
        store=True
    )

    kpi_completion_rate = fields.Float(
        string='Tỷ lệ hoàn thành (%)',
        compute='_compute_kpi_completion_rate',
        store=True
    )

    @api.depends('task_ids.kpi_actual', 'task_ids.kpi_score', 'is_kpi_plan')
    def _compute_kpi_year_score(self):
        for record in self:
            if record.is_kpi_plan:
                kpi_tasks = record.task_ids.filtered(lambda t: t.is_kpi_plan)
                record.kpi_year_actual = sum(kpi_tasks.mapped('kpi_actual'))
                record.kpi_year_score = sum(kpi_tasks.mapped('kpi_score'))
            else:
                record.kpi_year_actual = 0.0
                record.kpi_year_score = 0.0

    # Hàm tính tỷ lệ hoàn thành 
    @api.depends('kpi_year_actual', 'kpi_year_target')
    def _compute_kpi_completion_rate(self):
        for record in self:
            if record.kpi_year_target > 0:
                record.kpi_completion_rate = record.kpi_year_actual / record.kpi_year_target
            else:
                record.kpi_completion_rate = 0.0

    @api.depends('task_ids.kpi_weight', 'task_ids.is_kpi_plan')
    def _compute_kpi_allocated_weight(self):
        for record in self:
            if record.is_kpi_plan:
                kpi_tasks = record.task_ids.filtered(lambda t: t.is_kpi_plan)
                record.kpi_allocated_weight = sum(kpi_tasks.mapped('kpi_weight'))
            else:
                record.kpi_allocated_weight = 0.0

    @api.constrains('kpi_allocated_weight')
    def _check_allocated_weight(self):
        for record in self:
            if record.is_kpi_plan and round(record.kpi_allocated_weight, 2) > 100.0:
                raise ValidationError("Lỗi! Tổng trọng số không được vượt quá 100%.")

    @api.constrains('kpi_year_target', 'is_kpi_plan', 'task_ids')
    def _check_kpi_year_target(self):
        for record in self:
            if record.is_kpi_plan:
                if record.kpi_year_target <= 0:
                    raise ValidationError("KPI mục tiêu năm phải lớn hơn 0!")
    
                total_task_target = sum(record.task_ids.filtered('is_kpi_plan').mapped('kpi_target'))
                if total_task_target > record.kpi_year_target:
                    raise ValidationError(
                        "Lỗi! Tổng KPI mục tiêu các tháng (%s) không được vượt quá KPI mục tiêu năm (%s)." 
                        % (total_task_target, record.kpi_year_target)
                    )