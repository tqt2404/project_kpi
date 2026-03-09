# Tài liệu Kỹ thuật: Module Project KPI Management

Project KPI là một module tùy chỉnh cấp doanh nghiệp (Enterprise Custom Addon) được phát triển trên nền tảng Odoo 17. Giải pháp này chuyển đổi ứng dụng Quản lý Dự án (Project) mặc định thành một hệ thống quản trị mục tiêu, đánh giá hiệu suất (KPI) tự động, trực quan và bảo mật. Thay vì phụ thuộc vào các bảng tính thủ công, Project KPI tập trung hóa toàn bộ quy trình đánh giá ngay trên hệ sinh thái quản trị của Odoo.

## 1. Kiến trúc và Tính năng Cốt lõi

Hệ thống được thiết kế tối ưu từ cấu trúc cơ sở dữ liệu, trải nghiệm người dùng (UI/UX) đến phân quyền bảo mật, bao gồm các nhóm tính năng sau:

### Quản trị Kế hoạch và Mục tiêu

* **Ánh xạ dữ liệu:** Sử dụng Model project.project để quản lý Kế hoạch KPI Năm và Model project.task để quản lý Phiếu KPI Tháng.
* **Tự động hóa khởi tạo (Wizard):** Tích hợp công cụ Khởi tạo nhanh cho phép cấp quản lý tạo lập hàng loạt phiếu KPI cho toàn bộ chu kỳ 12 tháng chỉ với một thao tác. Hệ thống tự động kiểm tra và chỉ bổ sung các kỳ đánh giá còn thiếu, loại bỏ rủi ro trùng lặp dữ liệu.
* **Chuẩn hóa quy trình (Workflow):** Tự động thiết lập các giai đoạn công việc tiêu chuẩn (Mới, Đang thực hiện, Đánh giá, Hoàn tất) và áp dụng chung cho mọi dự án KPI. Tự động tính toán ngày bắt đầu và hạn chót (Deadline) theo chu kỳ tháng được chọn.

### Kiểm soát Dữ liệu và Phân quyền Bảo mật (Security)

* **Phân quyền truy cập đa tầng (Record Rules):** Áp dụng nguyên tắc đặc quyền tối thiểu. Nhân sự chỉ được phép truy cập phiếu KPI của cá nhân. Cấp quản lý trực tiếp được quyền giám sát dữ liệu của phòng ban trực thuộc. Quản trị viên hệ thống có quyền quản lý toàn cảnh.
* **Bảo mật cấp Dự án:** Mọi Kế hoạch KPI khi được tạo ra đều tự động thiết lập chế độ bảo mật nội bộ (Followers Only), ngăn chặn rò rỉ dữ liệu nhạy cảm liên quan đến hiệu suất và lương thưởng.
* **Ràng buộc nghiệp vụ (Business Constraints):**
* Ngăn chặn tạo nhiều kế hoạch cho cùng một phòng ban trong một năm tài chính.
* Giới hạn tối đa một phiếu đánh giá cho mỗi nhân sự trong một chu kỳ tháng.
* Kiểm soát tổng mục tiêu phân bổ không vượt quá mục tiêu năm đã duyệt.
* Kiểm soát tổng trọng số không vượt ngưỡng 100%.


* **Đóng kỳ đánh giá (Freeze):** Khi kế hoạch chuyển sang trạng thái Hoàn tất, toàn bộ dữ liệu của chu kỳ đó sẽ bị khóa (Readonly), ngăn chặn mọi hành vi chỉnh sửa số liệu thực tế nhằm thay đổi kết quả đánh giá.

### Hệ thống Báo cáo và Phân tích (Dashboard & Analytics)

* **Dashboard:** Bảng điều khiển tổng quan, xử lý dữ liệu và Cung cấp bộ lọc động theo Năm, Tháng, Phòng ban và tự động tính toán các chỉ số tổng hợp.
* **Bảng xếp hạng hiệu suất:** Hiển thị danh sách nhân sự xuất sắc. Thuật toán tự động lấy điểm của nhân sự dẫn đầu làm hệ quy chiếu (100%) để phân loại và hiển thị cảnh báo bằng màu sắc tương đối, giúp duy trì tính chính xác của biểu đồ khi xem ở nhiều góc độ thời gian khác nhau.
* **Phân tích đa chiều:** Tích hợp sẵn các góc nhìn Pivot và Graph nguyên bản của Odoo, hỗ trợ ban lãnh đạo phân tích chéo dữ liệu hiệu suất theo phòng ban, nhân sự và thời gian.

## 2. Hướng dẫn Triển khai (Dành cho Lập trình viên)

Quy trình thiết lập môi trường phát triển và cài đặt module trên máy chủ:

```bash
# 1. Tạo thư mục làm việc
mkdir odoo_kpi_workspace && cd odoo_kpi_workspace

# 2. Tải mã nguồn Odoo 17
git clone https://github.com/odoo/odoo.git -b 17.0 --depth 1

# 3. Tạo thư mục chứa custom addons và tải module Project KPI
mkdir custom_addons && cd custom_addons
git clone https://github.com/tqt2404/project_kpi.git

# 4. Khởi chạy máy chủ Odoo với đường dẫn addons tương ứng
cd ..
python odoo/odoo-bin -r <db_user> -w <db_password> --addons-path='odoo/addons,custom_addons'

```

Truy cập hệ thống, kích hoạt Developer Mode, cập nhật danh sách ứng dụng và tiến hành cài đặt module Project KPI.

## 3. Hướng dẫn Vận hành

Quy trình vận hành được chia thành hai luồng tác vụ chính dành cho Cấp quản lý và Nhân sự thực thi.

### Vai trò Cấp quản lý

**Lập Kế hoạch Năm:**

1. Truy cập phân hệ Dự án, khởi tạo bản ghi mới.
2. Kích hoạt thuộc tính **Là Kế hoạch KPI**.
3. Cập nhật các thông tin cơ sở: Năm đánh giá, Phòng ban chịu trách nhiệm, và KPI mục tiêu năm.
4. Lưu bản ghi.

**Phân bổ Chỉ tiêu:**

1. Tại giao diện Kế hoạch Năm, chọn tác vụ Khởi tạo nhanh KPI Tháng.
2. Cập nhật danh sách nhân sự phụ trách, trọng số phần trăm và mục tiêu cụ thể cho từng chu kỳ.
3. Xác nhận tạo tự động các Phiếu KPI tháng.

**Giám sát và Phân tích:**
Truy cập trang Dashboard để theo dõi tiến độ tổng thể, phân tích biểu đồ cơ cấu và đánh giá danh sách nhân sự đạt hiệu suất cao nhất.

### Vai trò Nhân sự thực thi

1. Truy cập danh mục Nhiệm vụ của tôi để xem các Phiếu KPI được giao.
2. Hệ thống mặc định khóa các trường thông tin Mục tiêu và Trọng số để đảm bảo tính toàn vẹn của chỉ tiêu.
3. Tại thời điểm đánh giá, cập nhật số liệu vào trường KPI Thực tế.
4. Chuyển trạng thái phiếu sang giai đoạn Đánh giá. Hệ thống sẽ tự động tính toán và hiển thị Điểm KPI.

## 4. Logic Tính toán và Cơ chế Kiểm soát

Thuật toán tính điểm được thiết kế nhằm phản ánh chính xác hiệu suất đồng thời bảo vệ quỹ thưởng của doanh nghiệp trước các trường hợp vượt chỉ tiêu đột biến.

**Công thức cơ sở:**
Điểm KPI = (Thực tế / Mục tiêu) x Trọng số

**Cơ chế kiểm soát biên độ (Min/Max Capping):**
Hệ thống can thiệp vào kết quả tính toán cuối cùng thông qua các hàm điều kiện:

1. **Giới hạn dưới:** Áp dụng hàm max bảo đảm điểm số không nhận giá trị âm trong mọi tình huống.
2. **Giới hạn trần (120%):** Áp dụng hàm min để khống chế số điểm tối đa. Trong trường hợp nhân sự vượt chỉ tiêu ở mức không giới hạn, số điểm ghi nhận tối đa cho kỳ đánh giá đó không vượt quá 120% giá trị của Trọng số đã giao.

Tiến độ hoàn thành của toàn bộ dự án được tính bằng tỷ lệ phần trăm giữa Tổng thực tế tích lũy và Mục tiêu năm, được cập nhật theo thời gian thực trên tiêu đề của Kế hoạch KPI.