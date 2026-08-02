[app]
title = App Cua Toi
package.name = appcuatoi
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 0.1
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.accept_sdk_license = True

# --- CÁC DÒNG QUAN TRỌNG ĐỂ FIX LỖI ---
# Nâng cấp API Level tối thiểu và mục tiêu
android.api = 33
android.minapi = 21

# Bắt buộc dùng phiên bản NDK tương thích với Buildozer hiện tại
android.ndk_path = ${HOME}/.buildozer/android/platform/android-ndk-r25c
android.ndk_api = 21

# Thêm cấu hình hỗ trợ Gradle NDK
p4a.branch = master
# ----------------------------------------

[buildozer]
log_level = 2
warn_on_root = 1
