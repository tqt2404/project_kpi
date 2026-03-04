from odoo import models, fields, api

class Task(models.Model):
    _inherit = 'project.task'

    is_kpi_plan = fields.Boolean(related='project_id.is_kpi_plan', string='Thuộc Kế hoạch KPI', store=True)
    
    kpi_month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng đánh giá')
    
    kpi_weight = fields.Float(string='Trọng số KPI (%)')
    kpi_target = fields.Float(string='KPI mục tiêu')
    kpi_actual = fields.Float(string='KPI thực tế')
    
    kpi_score = fields.Float(
        string='Điểm KPI',
        compute='_compute_kpi_score',
        store=True
    )
    kpi_user_id = fields.Many2one(
        'res.users', 
        string='Nhân sự KPI', 
        default=lambda self: self.env.user,
        store=True
    )
    
    kpi_year = fields.Selection(
        related='project_id.year', 
        string='Năm đánh giá', 
        store=True
    )
    
    department_id = fields.Many2one(
        'hr.department', 
        related='project_id.department_id',
        store=True,
        string='Phòng ban'
    )

    @api.depends('kpi_actual', 'kpi_target', 'kpi_weight')
    def _compute_kpi_score(self):
        for record in self:
            if not record.is_kpi_plan:
                record.kpi_score = 0.0
                continue
            if record.kpi_target and record.kpi_target > 0:
                score = (record.kpi_actual / record.kpi_target) * record.kpi_weight
                record.kpi_score = max(0.0, min(score, record.kpi_weight * 1.2))
            else:
                record.kpi_score = 0.0
                
    @api.constrains('kpi_target', 'project_id', 'is_kpi_plan')
    def _check_kpi_target_limit(self):
        for task in self:
            if task.is_kpi_plan and task.project_id:
                kpi_tasks = task.project_id.task_ids.filtered('is_kpi_plan')
                total_target = sum(kpi_tasks.mapped('kpi_target'))
                
                if total_target > task.project_id.kpi_year_target:
                    raise ValidationError(
                        "Lỗi! Tổng KPI mục tiêu của các Task (%s) vượt quá KPI mục tiêu năm của Dự án (%s)." % 
                        (total_target, task.project_id.kpi_year_target)
                    )

    @api.constrains('project_id', 'is_kpi_plan')
    def _check_max_tasks(self):
        for task in self:
            if task.is_kpi_plan and task.project_id:
                kpi_tasks = task.project_id.task_ids.filtered('is_kpi_plan')
                if len(kpi_tasks) > 12:
                    raise ValidationError("Lỗi! Một dự án KPI chỉ được phép tạo tối đa 12 Task (tương ứng với 12 tháng).")