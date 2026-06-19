TRANSLATIONS = {
    "en": {
        # Context Menu
        "menu_dashboard": "📊 Show Dashboard",
        "menu_settings": "⚙️ Settings",
        "menu_ai_logs": "📂 Open AI Logs",
        "menu_hw_log": "📂 Open Hardware Log",
        "menu_debug": "🛠️ Test & Debug",
        "menu_fireworks": "🎆 Test Fireworks UI",
        "menu_exit": "❌ Exit",
        # Submenu
        "menu_idle": "IDLE (0x01)",
        "menu_thinking": "THINKING (0x02)",
        "menu_waiting": "WAITING (0x03)",
        "menu_error": "ERROR (0x04)",
        "menu_drink": "DRINK WATER (Audio)",
        
        # Tray Menu
        "tray_toggle": "Show/Hide Pet",
        "tray_settings": "Settings",
        "tray_quit": "Quit",
        
        # Pet Status
        "status_idle": "IDLE",
        "status_thinking": "THINKING",
        "status_waiting": "WAITING",
        "status_error": "ERROR",
        "status_unknown": "UNKNOWN",
        
        # Dialogs / Popups
        "dialog_not_found": "Not Found",
        "dialog_error": "Error",
        "dialog_saved": "Saved",
        "dialog_scan": "Scan",
        "msg_no_brain_dir": "No active log directory found.\nPlease configure it in Settings.",
        "msg_no_hw_log": "No hardware log found yet.\nLog will be created after the first BLE/Serial connection attempt.",
        "msg_open_log_err": "Could not open log: {e}",
        "msg_no_devices": "No devices found.",
        "msg_settings_saved": "Settings saved and applied successfully!",
        "msg_already_running": "AgyPet is already running in the background!\nCheck your system tray (near the clock).",
        
        # Dashboard
        "dash_title": "Today's Workload",
        "dash_requests": "User Requests: {val}",
        "dash_actions": "AI Actions: {val}",
        "dash_tools": "Tools Used: {val}",
        "dash_user_chars": "User Chars: {val}",
        "dash_ai_chars": "AI Chars: {val}",
        "dash_errors": "Errors: {val}",
        
        # Settings UI
        "set_title": "AgyPet Settings",
        "set_lang": "Language:",
        "set_conn_mode": "Connection Mode:",
        "set_mode_none": "No Hardware (Desktop Only)",
        "set_mode_serial": "Serial Port (USB/SPP)",
        "set_mode_ble": "Bluetooth LE (BLE)",
        "set_serial_settings": "Serial Settings:",
        "set_port": "Port:",
        "set_baud": "Baud:",
        "set_ble_settings": "BLE Settings:",
        "set_name_mac": "Name/MAC:",
        "set_scan": "Scan",
        "set_log_dir": "Log Directory:",
        "browse": "Browse",
        "set_volume": "Volume:",
        "set_voice_profile": "Voice Profile:",
        "set_webhook": "Webhook URL (Optional):",
        "set_water_reminder": "Water Reminder Times:",
        "set_water_subtext": "24-Hour times (e.g. 10:30, 15:00):",
        "set_about": "About AgyPet",
        "set_version": "Version: v0.1.2",
        "set_author": "Author: aning35",
        "set_save": "Save & Apply",
        
        # Voice profiles
        "voice_baba": "Papa",
        "voice_mama": "Mama",
        "voice_zhuren": "Master",
        "voice_laoban": "Boss",
        "voice_gege": "Brother",
        "voice_baobao": "Honey",
        "voice_dongshizhang": "Chairman",
        "voice_guozhu": "Monarch",
        "voice_huangshang": "Emperor",

        # Status text detail fallback translation keys
        "Startup": "Startup",
        "Test Hardware": "Test Hardware",
        "Restored from dock": "Restored from dock"
    },
    "zh": {
        # Context Menu
        "menu_dashboard": "📊 显示仪表盘",
        "menu_settings": "⚙️ 设置",
        "menu_ai_logs": "📂 打开 AI 日志",
        "menu_hw_log": "📂 打开硬件日志",
        "menu_debug": "🛠️ 测试与调试",
        "menu_fireworks": "🎆 测试烟花效果",
        "menu_exit": "❌ 退出",
        # Submenu
        "menu_idle": "空闲 (0x01)",
        "menu_thinking": "思考中 (0x02)",
        "menu_waiting": "等待确认 (0x03)",
        "menu_error": "错误 (0x04)",
        "menu_drink": "喝水提醒 (音频)",
        
        # Tray Menu
        "tray_toggle": "显示/隐藏宠物",
        "tray_settings": "设置",
        "tray_quit": "退出",
        
        # Pet Status
        "status_idle": "空闲",
        "status_thinking": "思考中",
        "status_waiting": "等待确认",
        "status_error": "错误",
        "status_unknown": "未知",
        
        # Dialogs / Popups
        "dialog_not_found": "未找到",
        "dialog_error": "错误",
        "dialog_saved": "已保存",
        "dialog_scan": "扫描",
        "msg_no_brain_dir": "未找到活跃的日志目录。\n请在设置中配置。",
        "msg_no_hw_log": "尚未找到硬件日志。\n在首次尝试 BLE/串口连接后将创建日志。",
        "msg_open_log_err": "无法打开日志: {e}",
        "msg_no_devices": "未找到设备。",
        "msg_settings_saved": "设置已保存并应用！",
        "msg_already_running": "AgyPet 已在后台运行！\n请检查系统托盘（时钟旁）。",
        
        # Dashboard
        "dash_title": "今日工作量",
        "dash_requests": "用户请求数: {val}",
        "dash_actions": "AI 执行步骤: {val}",
        "dash_tools": "工具调用数: {val}",
        "dash_user_chars": "用户字符数: {val}",
        "dash_ai_chars": "AI 字符数: {val}",
        "dash_errors": "错误数: {val}",
        
        # Settings UI
        "set_title": "AgyPet 设置",
        "set_lang": "语言：",
        "set_conn_mode": "连接模式：",
        "set_mode_none": "无硬件连接 (仅桌面)",
        "set_mode_serial": "串口连接",
        "set_mode_ble": "蓝牙连接",
        "set_serial_settings": "串口设置：",
        "set_port": "端口：",
        "set_baud": "波特率：",
        "set_ble_settings": "蓝牙设置：",
        "set_name_mac": "名称/MAC：",
        "set_scan": "扫描",
        "set_log_dir": "日志目录：",
        "browse": "浏览",
        "set_volume": "音量：",
        "set_voice_profile": "称呼方案：",
        "set_webhook": "Webhook 链接 (可选)：",
        "set_water_reminder": "喝水提醒时间：",
        "set_water_subtext": "24小时制时间 (例如 10:30, 15:00)：",
        "set_about": "关于 AgyPet",
        "set_version": "版本: v0.1.2",
        "set_author": "作者: aning35",
        "set_save": "保存并应用",
        
        # Voice profiles
        "voice_baba": "爸爸",
        "voice_mama": "妈妈",
        "voice_zhuren": "主人",
        "voice_laoban": "老板",
        "voice_gege": "哥哥",
        "voice_baobao": "宝宝",
        "voice_dongshizhang": "董事长",
        "voice_guozhu": "国主",
        "voice_huangshang": "皇上",

        # Status text detail fallback translation keys
        "Startup": "正在启动",
        "Test Hardware": "测试硬件",
        "Restored from dock": "从停靠栏恢复"
    }
}

def t(key, lang="en", **kwargs):
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    val = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            pass
    return val
