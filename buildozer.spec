[app]

# Información básica
title = Switch Launcher
package.name = switchlauncher
package.domain = org.switchlauncher

# Versión
version = 1.0.0

# Archivos fuente
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# Archivo principal
entrypoint = main.py

# Requisitos de Python/Kivy
requirements = python3,kivy==2.3.0,kivymd,pillow,android

# Permisos necesarios para launcher
android.permissions = RECEIVE_BOOT_COMPLETED,QUERY_ALL_PACKAGES,PACKAGE_USAGE_STATS,SET_WALLPAPER,EXPAND_STATUS_BAR,READ_PHONE_STATE,INTERNET,ACCESS_NETWORK_STATE

# Versiones Android
android.minapi = 26
android.targetapi = 33
android.api = 33
android.ndk = 25b
android.sdk = 33

# Arquitecturas (incluye ambas para mayor compatibilidad)
android.archs = arm64-v8a, armeabi-v7a

# Importante: declara que es un launcher
android.add_activities = org.switchlauncher.MainLauncher

# Orientación
orientation = portrait

# Fullscreen
fullscreen = 1

# Modo pantalla completa inmersivo
android.add_flags = --flags-fullscreen

# Icono y pantalla de carga
#icon.filename = %(source.dir)s/assets/icon.png
#presplash.filename = %(source.dir)s/assets/splash.png
presplash.color = #0F0F1A

# NDK / SDK paths (buildozer los descarga automáticamente)
#android.ndk_path =
#android.sdk_path =

# Java extras — declara intent-filter como HOME launcher
android.manifest.intent_filters = %(source.dir)s/assets/intent_filters.xml

[buildozer]

# Log level: 0=error, 1=info, 2=debug
log_level = 2

# Advertencias como errores: desactivar para builds más permisivos
warn_on_root = 0
