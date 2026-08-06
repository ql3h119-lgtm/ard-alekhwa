[app]
title = Ard Alekhwa
package.name = ardalekhwa
package.domain = org.abujabr.land
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0

requirements = python3,kivy==2.1.0,pillow,arabic_reshaper,python-bidi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 1
warn_on_root = 0
