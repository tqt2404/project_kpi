from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
from dateutil.relativedelta import relativedelta

class Task(models.Model):
    _inherit = 'project.task'

    is_kpi_plan = fields.Boolean(related='project_id.is_kpi_plan', string='Thuộc Kế hoạch KPI', store=True,index=True)
    
    kpi_month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng đánh giá',index=True)
    
    kpi_weight = fields.Float(string='Trọng số KPI (%)',tracking=True)
    kpi_target = fields.Float(string='KPI mục tiêu',tracking=True)
    kpi_actual = fields.Float(string='KPI thực tế',tracking=True)
    
    kpi_score = fields.Float(
        string='Điểm KPI',
        compute='_compute_kpi_score',
        store=True
    )
    kpi_user_id = fields.Many2one(
        'res.users', 
        string='Nhân sự', 
        default=lambda self: self.env.user,
        store=True,
        index=True
    )
    
    kpi_year = fields.Selection(
        related='project_id.year', 
        string='Năm đánh giá', 
        store=True,
        index=True
    )
    
    department_id = fields.Many2one(
        'hr.department', 
        string='Phòng ban',
        default=lambda self: self.env.user.employee_id.department_id.id,
        store=True,
        required=True,
        index=True
    )
    
    kpi_completion_rate = fields.Float(
        related='project_id.kpi_completion_rate', 
        string='Tiến độ Dự án',
        store=True,
    )
    
    kpi_date_start = fields.Date(string='Ngày bắt đầu KPI')
    
    department_manager_user_id = fields.Many2one(
        'res.users', 
        string='Quản lý phòng ban',
        related='department_id.manager_id.user_id', 
        store=True, 
        index=True
    )

    @api.onchange('kpi_month', 'project_id')
    def _onchange_kpi_month_set_deadline(self):
        """Tự động tính ngày đầu tháng và ngày cuối tháng"""
        for record in self:
            if record.is_kpi_plan and record.kpi_month and record.project_id.year:
                try:
                    year = int(record.project_id.year)
                    month = int(record.kpi_month)
                    record.kpi_date_start = datetime.date(year, month, 1)
                    
                    # 2. Gán ngày cuối tháng
                    last_day = datetime.date(year, month, 1) + relativedelta(months=1, days=-1)
                    record.date_deadline = last_day
                except ValueError:
                    pass
                
    @api.constrains('is_kpi_plan', 'kpi_weight', 'kpi_target')
    def _check_kpi_required_fields(self):
        """Ràng buộc chỉ bắt lỗi thiếu số liệu đối với Task KPI"""
        for task in self:
            if task.is_kpi_plan:
                if not task.kpi_weight or task.kpi_weight <= 0:
                    raise ValidationError("Lỗi! Vui lòng nhập Trọng số KPI (%) lớn hơn 0.")
                if not task.kpi_target or task.kpi_target <= 0:
                    raise ValidationError("Lỗi! Vui lòng nhập KPI mục tiêu lớn hơn 0.")

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Khi người dùng chọn/đổi Phòng ban, tự động xóa Dự án cũ nếu không khớp"""
        if self.project_id and self.project_id.department_id != self.department_id:
            self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Trường hợp chọn Dự án trước, tự động điền Phòng ban tương ứng"""
        if self.project_id and self.project_id.department_id:
            self.department_id = self.project_id.department_id

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
                
    @api.constrains('kpi_month', 'project_id', 'is_kpi_plan')
    def _check_unique_kpi_month(self):
        """
        Ràng buộc: Mỗi tháng trong một dự án KPI chỉ được phép có 1 Task duy nhất.
        """
        for task in self:
            # Chỉ kiểm tra nếu task thuộc kế hoạch KPI, có dự án và đã chọn tháng
            if task.is_kpi_plan and task.project_id and task.kpi_month:
                # Tìm kiếm xem có task nào khác trong cùng dự án, cùng tháng không
                duplicate_tasks = self.env['project.task'].search_count([
                    ('project_id', '=', task.project_id.id),
                    ('is_kpi_plan', '=', True),
                    ('kpi_month', '=', task.kpi_month),
                    ('id', '!=', task.id) 
                ])
                
                if duplicate_tasks:
                    month_label = dict(self._fields['kpi_month'].selection).get(task.kpi_month, task.kpi_month)
                    
                    raise ValidationError(
                        "Lỗi logic! Dự án này đã có kế hoạch KPI cho %s. "
                        "Mỗi tháng chỉ được phép tạo một Task KPI duy nhất." % month_label
                    )
                    
    @api.onchange('kpi_user_id')
    def _onchange_sync_kpi_user_ids(self):
        """Tự động thêm kpi_user_id vào danh sách Assignees mặc định (Mục đích tối ưu tốc độ View)"""
        if self.kpi_user_id:
            self.user_ids = [(4, self.kpi_user_id.id)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('project_id'):
                project = self.env['project.project'].browse(vals['project_id'])
                if project.is_kpi_plan and getattr(project, 'kpi_state', False) == 'done':
                    raise ValidationError("Lỗi! Không thể tạo thêm nhiệm vụ vì Kế hoạch năm đã chốt.")
            
            if vals.get('kpi_user_id'):
                if 'user_ids' in vals:
                    vals['user_ids'].append((4, vals['kpi_user_id']))
                else:
                    vals['user_ids'] = [(4, vals['kpi_user_id'])]
                    
        return super(Task, self).create(vals_list)

    def write(self, vals):
        for task in self:
            # 1. Chặn sửa nếu dự án đã đóng
            if task.is_kpi_plan and task.project_id and getattr(task.project_id, 'kpi_state', False) == 'done':
                raise ValidationError("Lỗi! Không thể chỉnh sửa dữ liệu vì Kế hoạch năm đã Đã chốt năm.")
            
            if task.is_kpi_plan:
                restricted_fields = {'kpi_target', 'kpi_weight', 'kpi_month'}
                for field in restricted_fields:
                    if field in vals and vals[field] != task[field]:
                        if not self.env.user.has_group('project.group_project_manager'):
                            raise ValidationError("Lỗi Bảo mật: Bạn chỉ được phép cập nhật số liệu [Thực tế]...")

        res = super(Task, self).write(vals)
    
        if 'kpi_user_id' in vals:
            for task in self:
                if task.kpi_user_id:
                    task.user_ids = [(4, task.kpi_user_id.id)]
                    
        return res