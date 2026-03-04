# Project KPI Management (Giải pháp KPI Odoo)

Module giải quyết bài toán quản lý KPI bằng cách tận dụng tối đa hệ sinh thái có sẵn của module Project, giúp tiết kiệm tài nguyên hệ thống và tối ưu UX/UI.

## 1. Mô tả bài toán
Tích hợp khả năng Lập kế hoạch năm (Project) và Đánh giá KPI theo tháng (Task) cho nhân sự và phòng ban mà không sử dụng các ứng dụng KPI bên thứ ba.

## 2. Cách cài module
1. Copy thư mục `project_kpi` vào thư mục `addons` của Odoo.
2. Bật chế độ Developer Mode.
3. Cập nhật danh sách ứng dụng (Update Apps List).
4. Tìm kiếm `Project KPI` và nhấn Cài đặt (Install).

## 3. Giải thích logic tính KPI
* **Dự án (Kế hoạch năm):** Sử dụng trường Boolean `is_kpi_plan` làm cờ phân loại. Tổng điểm năm bằng tổng điểm các Task có chứa tháng đánh giá.
* **Công việc (KPI):** * Điểm KPI = (Thực tế / Mục tiêu) * Trọng số.
  * Giới hạn logic (Min/Max): Dùng hàm `max(0.0, min(score, weight * 1.2))` để khóa điểm ở mức tối thiểu 0 và tối đa 120% trọng số.

## 4. Cách sử dụng
1. Vào module **Project**. Mở hoặc tạo một Dự án, tích chọn **"Là Kế hoạch KPI"**. Tab "Kế hoạch KPI" sẽ xuất hiện.
2. Tạo các Task con. Khi Task thuộc Dự án KPI, nhóm "Thông tin KPI" sẽ hiện ra.
3. Xem báo cáo tổng hợp tại menu **Project -> Reporting -> Báo cáo KPI**.