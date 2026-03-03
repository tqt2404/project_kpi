from odoo import models, fields, api

class Task(models.Model):
    _inherit = 'project.task'

    # Trường liên kết để điều khiển giao diện (ẩn/hiện nhóm KPI)
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
    
    department_id = fields.Many2one(
        'hr.department', 
        related='project_id.department_id',
        store=True,
        string='Phòng ban'
    )

    @api.depends('kpi_actual', 'kpi_target', 'kpi_weight')
    def _compute_kpi_score(self):
        for record in self:
            if record.kpi_target and record.kpi_target > 0:
                score = (record.kpi_actual / record.kpi_target) * record.kpi_weight
                record.kpi_score = max(0.0, min(score, record.kpi_weight * 1.2))
            else:
                record.kpi_score = 0.0