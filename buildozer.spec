[app]

# Tên ứng dụng
title = LASEN SPA

# Tên package (không có khoảng trắng)
package.name = lasenspa

# Tên miền package
package.domain = org.lasen

# Thư mục chứa main.py
source.dir = .

# Các file được đóng gói
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,json

# Phiên bản ứng dụng
version = 1.0

# Thư viện cần thiết
requirements = python3,kivy

# Màn hình dọc
orientation = portrait

# Không fullscreen
fullscreen = 0


# Android

# Chỉ build 64-bit (Google Play yêu cầu)
android.archs = arm64-v8a

# API Android
android.api = 33

# Android tối thiểu
android.minapi = 24

# Chấp nhận giấy phép SDK
android.accept_sdk_license = True


# Icon (nếu có)
# icon.filename = %(source.dir)s/icon.png


# Cho phép internet nếu sau này cần đồng bộ
android.permissions = INTERNET


# Không dùng bootstrap SDL2 riêng
p4a.branch = master



[buildozer]

# Mức log chi tiết
log_level = 2

# Cảnh báo khi chạy quyền root
warn_on_root = 1
