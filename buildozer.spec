[app]
title = Ard Alekhwa
package.name = ardalekhwa
package.domain = org.abujabr.land
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi,materialyoucolor,exceptiongroup,asyncgui,asynckivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
