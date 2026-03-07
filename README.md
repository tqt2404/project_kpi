# Module Odoo: Project KPI Management (Quản lý KPI bằng Dự án)

**Project KPI** là một module tùy chỉnh (custom addon) dành cho Odoo 17. Module này tận dụng cấu trúc dữ liệu của ứng dụng Quản lý Dự án (Project) để xây dựng một hệ thống đánh giá hiệu suất nhân sự (KPI) tự động, trực quan và bảo mật.

---

## 1. Mô tả bài toán

**Bối cảnh:** Doanh nghiệp đang sử dụng Odoo để quản lý công việc và muốn tích hợp đánh giá nhân sự ngay trên hệ thống này, thay vì phải mua phần mềm bên ngoài hay tính toán thủ công bằng Excel.

**Giải pháp kiến trúc:**
* **Kế hoạch năm (Yearly Plan):** Ánh xạ vào Model `project.project`. Mỗi dự án đại diện cho một Kế hoạch KPI của một Phòng ban trong một năm.
* **KPI tháng (Monthly KPI):** Ánh xạ vào Model `project.task`. Mỗi nhiệm vụ (Task) đại diện cho một phiếu giao chỉ tiêu trong 1 tháng cụ thể cho 1 nhân sự.
* **Dashboard & Report:** Sử dụng OWL (Odoo Web Library) và Chart.js để build Dashboard, kết hợp với SQL Views (Pivot/Graph) của Odoo để tự động tổng hợp điểm.

---

## 2. Hướng dẫn cài đặt (Dành cho Lập trình viên)

Phần này hướng dẫn các Developer thiết lập môi trường Local từ con số 0 để chạy và phát triển module.

### Bước 2.1: Clone Source Code & Setup Môi trường
Mở Terminal (Linux/macOS) hoặc Git Bash (Windows) và chạy lần lượt các lệnh:

```bash
# 1. Tạo thư mục Workspace chứa toàn bộ dự án
mkdir odoo_kpi_workspace
cd odoo_kpi_workspace

# 2. Clone mã nguồn Odoo 17 (Bản gốc từ Github Odoo)
git clone [https://github.com/odoo/odoo.git](https://github.com/odoo/odoo.git) -b 17.0 --depth 1

# 3. Tạo thư mục chứa các custom modules
mkdir custom_addons
cd custom_addons

# 4. Clone module Project KPI từ Github
git clone [https://github.com/tqt2404/project_kpi.git](https://github.com/tqt2404/project_kpi.git)

# 5. Phân quyền (Bắt buộc nếu bạn dùng Linux Server)
# sudo chown -R odoo:odoo project_kpi/
# sudo chmod -R 755 project_kpi/

# 6. Quay lại thư mục gốc và Khởi chạy Odoo
cd ..
# Chạy lệnh odoo-bin, nhớ trỏ --addons-path tới cả 2 thư mục
python odoo/odoo-bin -r <db_user> -w <db_password> --addons-path="odoo/addons,custom_addons"

```

### Bước 2.2: Cài đặt trên giao diện Odoo

1. Truy cập `http://localhost:8069` và đăng nhập bằng tài khoản **Admin**.
2. Vào **Settings (Cài đặt)** -> Cuộn xuống dưới cùng nhấn **Activate the developer mode**.
3. Vào menu **Apps (Ứng dụng)** -> Bấm **Update Apps List (Cập nhật danh sách ứng dụng)** trên thanh công cụ -> Nhấn **Update**.
4. Xóa bộ lọc `Apps` mặc định ở thanh tìm kiếm, gõ `Project KPI`.
5. Nhấn **Install (Cài đặt)** và chờ hệ thống khởi động lại.

---

## 3. Hướng dẫn sử dụng chi tiết (Cho mọi người dùng)

Để một hệ thống KPI hoạt động, chúng ta cần 2 vai trò: **Sếp (Người giao việc)** và **Nhân viên (Người làm việc)**. Hệ thống đã phân quyền sẵn cho 2 vai trò này.

### 👨‍💼 VAI TRÒ 1: QUẢN LÝ (Sếp / Trưởng phòng)

Sếp sẽ là người vạch ra mục tiêu cả năm, sau đó chia nhỏ việc cho từng nhân viên trong từng tháng.

**Thao tác 1: Tạo Kế hoạch cho cả năm**

1. Mở ứng dụng **Dự án (Project)** -> Bấm nút **Mới (New)**.
2. Đặt tên (VD: *Kế hoạch Kinh doanh 2026*).
3. **BƯỚC QUAN TRỌNG NHẤT:** Dưới tên dự án có một ô vuông nhỏ tên là **"Là Kế hoạch KPI"**. Bạn PHẢI tích vào ô này.
4. Ngay lập tức, một tab mới tên **"Kế hoạch KPI"** hiện ra. Bạn điền:
* **Năm:** 2026.
* **Phòng ban:** Chọn phòng ban của bạn.
* **KPI mục tiêu năm:** Nhập tổng con số cả phòng phải đạt (VD: 1200 sản phẩm).


5. Bấm **Lưu**.

**Thao tác 2: Giao việc từng tháng cho Nhân viên**

1. Mở Kế hoạch năm vừa tạo -> Bấm vào nút **Nhiệm vụ (Tasks)**.
2. Tạo mới một Nhiệm vụ (VD: *Chỉ tiêu Tháng 1 - Của Nhân viên A*).
3. Tìm đến nhóm **"Thông tin KPI"** và điền:
* **Tháng đánh giá:** Chọn "Tháng 1".
* **Nhân sự:** Chọn tên nhân viên A.
* **Trọng số KPI (%):** Nhập độ quan trọng của công việc này (VD: 10%).
* **KPI mục tiêu:** Nhập con số nhân viên A phải đạt trong tháng 1 (VD: 100 sản phẩm).


4. Bấm **Lưu**.

**Thao tác 3: Xem báo cáo (Dashboard)**

* Sếp chỉ cần bấm vào chữ **Dashboard** trên menu ngang. Tại đây sếp chọn Năm, Tháng, Phòng ban là sẽ thấy ngay: Ai đang dẫn đầu (Top 10), phòng ban nào điểm cao nhất qua các biểu đồ tự động vẽ.

### 🧑‍💻 VAI TRÒ 2: NHÂN VIÊN (Người báo cáo)

*(Hệ thống bảo mật cực cao: Nhân viên đăng nhập vào CÓ TÌM MỎI MẮT cũng chỉ thấy được thẻ KPI của chính mình, không xem được của người khác).*

1. Vào ứng dụng **Dự án (Project)** -> Bấm chữ **Nhiệm vụ của tôi (My Tasks)** trên cùng.
2. Bấm vào Phiếu KPI của tháng này.
3. Kéo xuống phần **"Thông tin KPI"**. Bạn sẽ thấy "Mục tiêu" Sếp giao đã bị khóa xám lại (không thể ăn gian sửa mục tiêu thấp xuống).
4. Đến cuối tháng, bạn điền kết quả mình làm được vào ô **"KPI thực tế"**.
5. Bấm **Lưu**. Hệ thống sẽ tự nảy số ở ô **"Điểm KPI"** cho bạn biết mình được bao nhiêu điểm.

---

## 4. Giải thích logic tính KPI (Dễ hiểu cho người mới)

Phần này giải thích cách hệ thống tính điểm. Ngay cả khi bạn chưa từng làm nhân sự, bạn cũng sẽ hiểu ngay!

### KHÁI NIỆM CƠ BẢN CẦN BIẾT:

* **Mục tiêu:** Con số sếp muốn bạn đạt được (VD: Bán 100 cái áo).
* **Thực tế:** Con số bạn thực sự làm được (VD: Bán được 80 cái áo).
* **Trọng số (%):** Mức độ quan trọng của công việc đó trong cả năm. Tổng trọng số 12 tháng cộng lại thường là 100%. Nếu tháng 1 có trọng số là 10%, nghĩa là tháng 1 đóng góp tối đa 10 điểm vào quỹ 100 điểm của cả năm.

### A. Công thức tính điểm hàng tháng (Của Nhân viên)

Hệ thống dùng công thức toán học:

> **Điểm KPI = (Thực tế / Mục tiêu) × Trọng số**

*Ví dụ: Sếp giao mục tiêu 100 cái, trọng số 10%. Bạn làm được 80 cái.*

* *Cách tính: (80 / 100) * 10 = **8 điểm**.*

**🔥 Đặc biệt: Cơ chế khóa chống "Bơm điểm ảo" (Min/Max)**
Điều gì xảy ra nếu nhân viên bán được tới 300 cái áo? Nếu tính theo công thức trên: (300 / 100) * 10 = 30 điểm. Nếu điểm thưởng quy ra tiền, công ty sẽ vỡ quỹ!
Do đó, code của chúng tôi giới hạn:

1. **Không có điểm âm:** Kém nhất là 0 điểm.
2. **Khóa trần 120%:** Dù bạn làm vượt chỉ tiêu 200% hay 300%, điểm tối đa bạn nhận được chỉ bằng **120% của Trọng số**.
*(Ở ví dụ trên, trọng số là 10, vậy 120% của 10 là **12 điểm**. Nhân viên bán 300 cái áo cũng chỉ được tối đa 12 điểm cho tháng đó, để đảm bảo cân bằng quỹ thưởng của công ty).*

### B. Logic tính điểm cả năm (Của Phòng ban)

Hệ thống sẽ tự động làm toán cộng cho sếp:

* **Tổng điểm năm:** Lấy điểm KPI của 12 tháng cộng lại với nhau.
* **Tiến độ (%):** Bằng `(Tổng Thực tế của 12 tháng / Mục tiêu của cả năm) * 100`. Tiến độ này hiện ngay lên tên Kế hoạch để sếp nhìn lướt qua là biết.

### C. Các lớp "Chống phá hoại" (Bảo vệ dữ liệu)

Chúng tôi đã lập trình các quy tắc (Constraints) buộc người dùng không thể làm sai:

1. **Chống lặp:** Nếu phòng IT đã tạo Kế hoạch năm 2026 rồi, ai ấn tạo thêm cái thứ 2 hệ thống sẽ báo lỗi đỏ rực và chặn lại ngay.
2. **Mỗi tháng 1 phiếu:** Trong 1 năm, chỉ được tạo 1 phiếu cho Tháng 1. Cố tình tạo phiếu Tháng 1 thứ 2 sẽ bị phần mềm cấm.
3. **Ngăn sếp giao việc vô lý:** * Tổng các "Mục tiêu tháng" cộng lại phần mềm KHÔNG CHO PHÉP vượt qua "Mục tiêu cả năm".
* Tổng "Trọng số" các tháng cộng lại KHÔNG ĐƯỢC vượt quá 100%.


4. **Khóa chốt sổ:** Cuối năm, khi trạng thái dự án được chuyển thành **"Hoàn thành"**, toàn bộ số liệu của 12 tháng sẽ bị "hóa đá" (Readonly). Không một ai có thể sửa lại số để gian lận tiền thưởng.

```

```