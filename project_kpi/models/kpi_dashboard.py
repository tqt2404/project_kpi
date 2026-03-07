from odoo import models, api, fields

class KpiDashboard(models.AbstractModel):
    _name = 'kpi.dashboard'
    _description = 'KPI Dashboard Backend Data'

    @api.model
    def get_dashboard_data(self, filters):
        """
        RPC Endpoint: Lấy dữ liệu tổng hợp KPI - filters: dict chứa year, month, department_id, user_id
        """
        Task = self.env['project.task']
        base_domain = [('is_kpi_plan', '=', True)]
        
        #  LẤY DỮ LIỆU Năm & Phòng ban
        years_data = Task.read_group(base_domain, ['kpi_year'], ['kpi_year'])
        available_years = sorted([y['kpi_year'] for y in years_data if y['kpi_year']], reverse=True)
        
        depts_data = Task.read_group(base_domain, ['department_id'], ['department_id'])
        available_depts = [{'id': d['department_id'][0], 'name': d['department_id'][1]} for d in depts_data if d['department_id']]

        domain = list(base_domain)
        if filters.get('year'):
            domain.append(('kpi_year', '=', filters['year']))
        if filters.get('month'):
            domain.append(('kpi_month', '=', filters['month']))
        if filters.get('department_id'):
            domain.append(('department_id', '=', int(filters['department_id'])))

        # 1. Tổng hợp số liệu thẻ (Cards)
        summary_group = Task.read_group(domain, ['kpi_target:sum', 'kpi_actual:sum', 'kpi_score:sum'], [])[0] if Task.read_group(domain, ['kpi_target:sum', 'kpi_actual:sum', 'kpi_score:sum'], []) else {}

        # 2. Tổng hợp theo Phòng ban (Bar Chart)
        dept_group = Task.read_group(domain, ['kpi_score:sum'], ['department_id'])
        dept_labels = [d['department_id'][1] if d.get('department_id') else 'Chưa xác định' for d in dept_group]
        dept_scores = [round(d['kpi_score'], 2) for d in dept_group]

        # 3. Tổng hợp theo Trạng thái (Doughnut Chart)
        state_group = Task.read_group(domain, ['__count'], ['state'])
        state_mapping = {
            '01_in_progress': 'Đang tiến hành', 
            '1_done': 'Hoàn thành', 
            '04_waiting_normal': 'Chờ', 
            '03_approved': 'Đã duyệt', 
            '1_canceled': 'Đã hủy',
            '02_changes_requested': 'Yêu cầu thay đổi',
            False: 'Khác'
        }
        state_labels = [state_mapping.get(s.get('state'), 'Khác') for s in state_group]
        state_counts = [s['state_count'] for s in state_group]

        # 4. Tổng hợp Top 10 Nhân sự (Table)
        user_group = Task.read_group(
            domain, 
            fields=['kpi_score:sum'], 
            groupby=['kpi_user_id', 'department_id'], 
            orderby='kpi_score DESC', 
            limit=10,
            lazy=False
        )
        
        max_score = user_group[0].get('kpi_score', 0.0) if user_group else 1.0
        if max_score == 0: max_score = 1.0
        
        top_users = []
        for index, u in enumerate(user_group):
            score = round(u.get('kpi_score', 0.0), 2)
            
            # Tính tỷ lệ so với người Top 1
            ratio = score / max_score
            
            # Bảng màu chuẩn UX cho Dashboard
            color_class = 'danger'        # Đỏ: Báo động (< 50% so với Top 1)
            if ratio >= 0.9: 
                color_class = 'success'   # Xanh lá: Nhóm dẫn đầu (Xuất sắc)
            elif ratio >= 0.7: 
                color_class = 'info'      # Xanh lơ: Nhóm bám đuổi (Khá tốt)
            elif ratio >= 0.5: 
                color_class = 'warning'   # Vàng: Nhóm giữa (Cần cố gắng)

            top_users.append({
                'rank': index + 1,
                'name': u['kpi_user_id'][1] if u.get('kpi_user_id') else 'Ẩn danh',
                'dept': u['department_id'][1] if u.get('department_id') else 'Phòng ban khác',
                'score': score,
                'color': color_class
            })

        return {
            'filters': {
                'years': available_years,
                'departments': available_depts,
            },
            'summary': {
                'total_target': round(summary_group.get('kpi_target', 0) or 0.0, 2),
                'total_actual': round(summary_group.get('kpi_actual', 0) or 0.0, 2),
                'total_score': round(summary_group.get('kpi_score', 0) or 0.0, 2),
            },
            'charts': {
                'labels': dept_labels,
                'datasets': [{
                    'label': 'Điểm KPI',
                    'data': dept_scores,
                    'backgroundColor': '#36A2EB'
                }]
            },
            'status_data': {
                'labels': state_labels,
                'datasets': [{
                    'data': state_counts,
                    'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#C9CBCF']
                }]
            },
            'top_users': top_users
        }