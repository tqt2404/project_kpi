from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectKpiWizard(models.TransientModel):
    _name = 'project.kpi.wizard'
    _description = 'Wizard khởi tạo KPI hàng tháng'

    project_id = fields.Many2one('project.project', string='Kế hoạch năm', required=True)
    line_ids = fields.One2many('project.kpi.wizard.line', 'wizard_id', string='Chi tiết các tháng')

    @api.model
    def default_get(self, fields_list):
        # Hệ thống gọi hàm này ngay khi màn hình Wizard chuẩn bị mở
        res = super(ProjectKpiWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        
        if not active_id:
            return res
            
        project = self.env['project.project'].browse(active_id)
        res['project_id'] = project.id

        # 1. Truy vấn các tháng đã được tạo Task
        existing_tasks = self.env['project.task'].search([
            ('project_id', '=', project.id),
            ('is_kpi_plan', '=', True),
            ('kpi_month', '!=', False)
        ])
        existing_months = existing_tasks.mapped('kpi_month')

        # 2. Loại trừ và tính toán các tháng còn thiếu
        all_months = [f"{i:02d}" for i in range(1, 13)]
        missing_months = [m for m in all_months if m not in existing_months]

        # 3. Chặn thao tác nếu đã đủ 12 tháng (Phòng hờ người dùng cố tình gọi Action)
        if not missing_months:
            raise UserError("Lỗi! Kế hoạch này đã phân bổ đủ 12 tháng, không thể tạo thêm.")

        # 4. Đẩy danh sách tháng còn thiếu xuống lưới One2many
        lines = []
        for month in missing_months:
            lines.append((0, 0, {
                'kpi_month': month,
                'kpi_user_id': self.env.user.id,
                'kpi_weight': 0.0,
                'kpi_target': 0.0,
            }))
        res['line_ids'] = lines
        return res

    def action_generate_kpi(self):
        """Hàm chạy khi người dùng bấm nút Xác nhận trên Popup"""
        self.ensure_one()
        task_vals_list = []
        for line in self.line_ids:
            task_vals_list.append({
                'name': f'KPI Tháng {line.kpi_month}',
                'project_id': self.project_id.id,
                'department_id': self.project_id.department_id.id,
                'kpi_month': line.kpi_month,
                'kpi_user_id': line.kpi_user_id.id,
                'kpi_weight': line.kpi_weight,
                'kpi_target': line.kpi_target,
                'is_kpi_plan': True,
            })
            
        if task_vals_list:
            self.env['project.task'].create(task_vals_list)
            
        return {'type': 'ir.actions.act_window_close'}


class ProjectKpiWizardLine(models.TransientModel):
    _name = 'project.kpi.wizard.line'
    _description = 'Dòng chi tiết khởi tạo KPI'

    wizard_id = fields.Many2one('project.kpi.wizard', ondelete='cascade')
    kpi_month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng đánh giá', readonly=True) # Chỉ đọc để người dùng không tự sửa sai tháng
    
    kpi_user_id = fields.Many2one('res.users', string='Nhân sự phụ trách', required=True)
    kpi_weight = fields.Float(string='Trọng số (%)')
    kpi_target = fields.Float(string='Mục tiêu')