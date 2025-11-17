#!/usr/bin/env python3
"""
Tapo C225 快速入門指南
用於測試和驗證攝影機連線

使用方式:
    python quick_start.py
"""

import sys
import time


def main():
    print("=" * 60)
    print("Tapo C225 PTZ 控制系統 - 快速入門")
    print("=" * 60)
    
    # 檢查 pytapo 是否安裝
    print("\n1. 檢查 pytapo 套件...")
    try:
        from pytapo import Tapo
        print("   ✓ pytapo 已安裝")
    except ImportError:
        print("   ✗ pytapo 未安裝")
        print("   請執行: pip install pytapo")
        sys.exit(1)
    
    # 獲取攝影機資訊
    print("\n2. 輸入攝影機資訊")
    print("   (按 Enter 使用預設值)")
    
    host = input("   攝影機 IP [192.168.1.100]: ").strip()
    if not host:
        host = "192.168.1.100"
    
    user = input("   使用者名稱 [admin]: ").strip()
    if not user:
        user = "admin"
    
    password = input("   密碼: ").strip()
    if not password:
        print("   ✗ 密碼不能為空")
        sys.exit(1)
    
    # 連線測試
    print(f"\n3. 連線到 {host}...")
    try:
        tapo = Tapo(host, user, password)
        print("   ✓ 連線成功!")
    except Exception as e:
        print(f"   ✗ 連線失敗: {e}")
        print("\n   故障排除:")
        print("   - 確認 IP 位址正確")
        print("   - 嘗試使用 'admin' 作為使用者名稱")
        print("   - 使用 TP-Link 雲端帳號密碼")
        print("   - 在 Tapo App 啟用「Tapo Lab > 第三方相容性」")
        sys.exit(1)
    
    # 獲取基本資訊
    print("\n4. 獲取設備資訊...")
    try:
        basic_info = tapo.getBasicInfo()
        device_info = basic_info.get("device_info", {}).get("basic_info", {})
        print(f"   設備型號: {device_info.get('device_model', 'Unknown')}")
        print(f"   設備名稱: {device_info.get('device_alias', 'Unknown')}")
        print(f"   韌體版本: {device_info.get('sw_version', 'Unknown')}")
        print(f"   MAC 位址: {device_info.get('mac', 'Unknown')}")
    except Exception as e:
        print(f"   ⚠ 無法獲取資訊: {e}")
    
    # 檢查馬達能力
    print("\n5. 檢查 PTZ 能力...")
    try:
        motor_cap = tapo.getMotorCapability()
        cap = motor_cap.get("motor", {}).get("capability", {})
        print(f"   X 軸範圍: {cap.get('x_coord_min')} ~ {cap.get('x_coord_max')}")
        print(f"   Y 軸範圍: {cap.get('y_coord_min')} ~ {cap.get('y_coord_max')}")
        print(f"   最大速度: X={cap.get('x_max_speed')}, Y={cap.get('y_max_speed')}")
        print(f"   預設支援: {cap.get('preset')}")
        print(f"   校準支援: {cap.get('calibrate')}")
    except Exception as e:
        print(f"   ⚠ 無法獲取馬達能力: {e}")
    
    # 檢查預設位置
    print("\n6. 檢查預設位置...")
    try:
        presets = tapo.getPresets()
        if presets:
            print(f"   已設定 {len(presets)} 個預設位置:")
            for preset_id, name in presets.items():
                print(f"      ID {preset_id}: {name}")
        else:
            print("   尚未設定任何預設位置")
    except Exception as e:
        print(f"   ⚠ 無法獲取預設位置: {e}")
    
    # 檢查隱私模式
    print("\n7. 檢查隱私模式...")
    try:
        privacy = tapo.getPrivacyMode()
        enabled = privacy.get("enabled") == "on"
        print(f"   隱私模式: {'啟用' if enabled else '停用'}")
        if enabled:
            print("   ⚠ PTZ 操作前需要關閉隱私模式")
    except Exception as e:
        print(f"   ⚠ 無法檢查隱私模式: {e}")
    
    # 檢查自動追蹤
    print("\n8. 檢查自動追蹤...")
    try:
        auto_track = tapo.getAutoTrackTarget()
        enabled = auto_track.get("enabled") == "on"
        print(f"   自動追蹤: {'啟用' if enabled else '停用'}")
    except Exception as e:
        print(f"   ⚠ 無法檢查自動追蹤: {e}")
    
    # 互動式測試
    print("\n" + "=" * 60)
    print("互動式測試")
    print("=" * 60)
    
    while True:
        print("\n選擇操作:")
        print("  1. 向左移動")
        print("  2. 向右移動")
        print("  3. 向上移動")
        print("  4. 向下移動")
        print("  5. 校準（回到預設位置）")
        print("  6. 儲存當前位置為預設")
        print("  7. 移動到預設位置")
        print("  8. 切換隱私模式")
        print("  9. 切換自動追蹤")
        print("  0. 離開")
        
        choice = input("\n請選擇 [0-9]: ").strip()
        
        if choice == "0":
            print("\n感謝使用!")
            break
        
        # 確保隱私模式關閉
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            try:
                privacy = tapo.getPrivacyMode()
                if privacy.get("enabled") == "on":
                    print("⚠ 隱私模式開啟中，正在關閉...")
                    tapo.setPrivacyMode(False)
                    time.sleep(1)
            except:
                pass
        
        try:
            if choice == "1":
                amount = input("移動量 [10]: ").strip()
                amount = int(amount) if amount else 10
                tapo.moveMotor(-amount, 0)
                print(f"✓ 向左移動 {amount} 單位")
                
            elif choice == "2":
                amount = input("移動量 [10]: ").strip()
                amount = int(amount) if amount else 10
                tapo.moveMotor(amount, 0)
                print(f"✓ 向右移動 {amount} 單位")
                
            elif choice == "3":
                amount = input("移動量 [5]: ").strip()
                amount = int(amount) if amount else 5
                tapo.moveMotor(0, amount)
                print(f"✓ 向上移動 {amount} 單位")
                
            elif choice == "4":
                amount = input("移動量 [5]: ").strip()
                amount = int(amount) if amount else 5
                tapo.moveMotor(0, -amount)
                print(f"✓ 向下移動 {amount} 單位")
                
            elif choice == "5":
                print("正在校準...")
                tapo.calibrateMotor()
                print("✓ 校準完成")
                
            elif choice == "6":
                name = input("預設名稱: ").strip()
                if name:
                    tapo.savePreset(name)
                    print(f"✓ 已儲存預設位置: {name}")
                else:
                    print("✗ 名稱不能為空")
                    
            elif choice == "7":
                presets = tapo.getPresets()
                if presets:
                    print("可用預設位置:")
                    for pid, pname in presets.items():
                        print(f"  ID {pid}: {pname}")
                    preset_id = input("輸入預設 ID: ").strip()
                    if preset_id in presets:
                        tapo.setPreset(preset_id)
                        print(f"✓ 正在移動到預設位置 {preset_id}")
                    else:
                        print("✗ 無效的預設 ID")
                else:
                    print("尚未設定任何預設位置")
                    
            elif choice == "8":
                privacy = tapo.getPrivacyMode()
                current = privacy.get("enabled") == "on"
                tapo.setPrivacyMode(not current)
                print(f"✓ 隱私模式已{'停用' if current else '啟用'}")
                
            elif choice == "9":
                auto_track = tapo.getAutoTrackTarget()
                current = auto_track.get("enabled") == "on"
                tapo.setAutoTrackTarget(not current)
                print(f"✓ 自動追蹤已{'停用' if current else '啟用'}")
                
            else:
                print("無效選項")
                
        except Exception as e:
            print(f"✗ 操作失敗: {e}")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
