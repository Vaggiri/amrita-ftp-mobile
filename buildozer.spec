[app]
title = AmritaFTP
package.name = amritaftp
package.domain = org.girisudhan

source.dir = .
source.include_exts = py,kv,json,png,jpg

version = 1.0

requirements = python3,kivy,kivymd,plyer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

android.archs = arm64-v8a

android.allow_backup = True

log_level = 2
