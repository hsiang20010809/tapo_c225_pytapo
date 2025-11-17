#!/usr/bin/env python3
"""
Tapo C225 PTZ Controller
用於企業環境的 Tapo C225 攝影機 PTZ 控制系統

作者：資訊部
版本：1.0.0
"""

import json
import time
from typing import Optional, Dict, Any
from pytapo import Tapo


class TapoC225Controller:
    """Tapo C225 攝影機控制器"""
    
    def __init__(self, host: str, user: str = "admin", password: str = ""):
        """
        初始化控制器
        
        Args:
            host: 攝影機 IP 位址
            user: 使用者名稱（通常為 "admin"）
            password: TP-Link 雲端帳號密碼
        """
        self.host = host
        self.user = user
        self.password = password
        self.tapo: Optional[Tapo] = None
        self.motor_capability: Optional[Dict] = None
        
    def connect(self) -> bool:
        """
        連接到攝影機
        
        Returns:
            bool: 連接成功返回 True
        """
        try:
            self.tapo = Tapo(self.host, self.user, self.password)
            print(f"✓ 成功連接到 {self.host}")
            
            # 獲取基本資訊
            basic_info = self.tapo.getBasicInfo()
            device_info = basic_info.get("device_info", {}).get("basic_info", {})
            print(f"  設備型號: {device_info.get('device_model', 'Unknown')}")
            print(f"  韌體版本: {device_info.get('sw_version', 'Unknown')}")
            
            # 獲取馬達能力
            self._get_motor_capability()
            
            return True
        except Exception as e:
            print(f"✗ 連接失敗: {e}")
            return False
    
    def _get_motor_capability(self):
        """獲取馬達能力資訊"""
        try:
            result = self.tapo.getMotorCapability()
            self.motor_capability = result.get("motor", {}).get("capability", {})
            print(f"  座標範圍 X: {self.motor_capability.get('x_coord_min')} ~ {self.motor_capability.get('x_coord_max')}")
            print(f"  座標範圍 Y: {self.motor_capability.get('y_coord_min')} ~ {self.motor_capability.get('y_coord_max')}")
        except Exception as e:
            print(f"  警告: 無法獲取馬達能力資訊 - {e}")
    
    def ensure_privacy_mode_off(self) -> bool:
        """
        確保隱私模式已關閉（PTZ 操作前必須）
        
        Returns:
            bool: 隱私模式已關閉返回 True
        """
        try:
            privacy = self.tapo.getPrivacyMode()
            if privacy.get("enabled") == "on":
                print("⚠ 隱私模式開啟中，正在關閉...")
                self.tapo.setPrivacyMode(False)
                time.sleep(1)
                print("✓ 隱私模式已關閉")
            return True
        except Exception as e:
            print(f"✗ 無法檢查/設定隱私模式: {e}")
            return False
    
    # ========== PTZ 移動控制 ==========
    
    def move(self, x: int, y: int) -> Dict[str, Any]:
        """
        相對位移移動
        
        Args:
            x: 水平移動量（正值向右，負值向左）
            y: 垂直移動量（正值向上，負值向下）
            
        Returns:
            dict: API 回應
        """
        self.ensure_privacy_mode_off()
        result = self.tapo.moveMotor(x, y)
        print(f"✓ 移動指令發送: X={x}, Y={y}")
        return result
    
    def move_left(self, amount: int = 10):
        """向左移動"""
        return self.move(-amount, 0)
    
    def move_right(self, amount: int = 10):
        """向右移動"""
        return self.move(amount, 0)
    
    def move_up(self, amount: int = 5):
        """向上移動"""
        return self.move(0, amount)
    
    def move_down(self, amount: int = 5):
        """向下移動"""
        return self.move(0, -amount)
    
    def move_step(self, angle: int) -> Dict[str, Any]:
        """
        步進移動（角度控制）
        
        Args:
            angle: 移動角度 (0-359)
                   0 = 順時針/右
                   90 = 向上
                   180 = 逆時針/左
                   270 = 向下
                   
        Returns:
            dict: API 回應
        """
        if not (0 <= angle < 360):
            raise ValueError("角度必須在 0-359 之間")
        self.ensure_privacy_mode_off()
        result = self.tapo.moveMotorStep(angle)
        print(f"✓ 步進移動: {angle}°")
        return result
    
    # ========== 預設位置管理 ==========
    
    def get_presets(self) -> Dict[str, str]:
        """
        獲取所有預設位置
        
        Returns:
            dict: 預設位置字典 {id: name}
        """
        presets = self.tapo.getPresets()
        print(f"✓ 已獲取 {len(presets)} 個預設位置:")
        for preset_id, name in presets.items():
            print(f"   ID {preset_id}: {name}")
        return presets
    
    def save_preset(self, name: str) -> bool:
        """
        將當前位置儲存為預設
        
        Args:
            name: 預設位置名稱
            
        Returns:
            bool: 成功返回 True
        """
        self.ensure_privacy_mode_off()
        result = self.tapo.savePreset(name)
        print(f"✓ 已儲存預設位置: {name}")
        return result
    
    def goto_preset(self, preset_id: str) -> Dict[str, Any]:
        """
        移動到預設位置
        
        Args:
            preset_id: 預設位置 ID（字串）
            
        Returns:
            dict: API 回應
        """
        self.ensure_privacy_mode_off()
        result = self.tapo.setPreset(str(preset_id))
        print(f"✓ 正在移動到預設位置 ID: {preset_id}")
        return result
    
    def delete_preset(self, preset_id: str) -> bool:
        """
        刪除預設位置
        
        Args:
            preset_id: 預設位置 ID
            
        Returns:
            bool: 成功返回 True
        """
        result = self.tapo.deletePreset(preset_id)
        print(f"✓ 已刪除預設位置 ID: {preset_id}")
        return result
    
    # ========== 校準與狀態 ==========
    
    def calibrate(self):
        """
        校準馬達（重置到預設位置）
        這會讓攝影機回到出廠預設位置
        """
        print("⚙ 正在執行馬達校準...")
        result = self.tapo.calibrateMotor()
        print("✓ 校準完成 - 攝影機已回到預設位置")
        return result
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """
        獲取當前旋轉狀態
        
        Returns:
            dict: 旋轉狀態資訊
        """
        try:
            status = self.tapo.getRotationStatus()
            return status
        except Exception as e:
            print(f"⚠ 無法獲取旋轉狀態: {e}")
            return {}
    
    # ========== 自動追蹤 ==========
    
    def get_auto_track(self) -> bool:
        """
        獲取自動追蹤狀態
        
        Returns:
            bool: 啟用返回 True
        """
        result = self.tapo.getAutoTrackTarget()
        enabled = result.get("enabled") == "on"
        print(f"✓ 自動追蹤: {'啟用' if enabled else '停用'}")
        return enabled
    
    def set_auto_track(self, enabled: bool):
        """
        設定自動追蹤
        
        Args:
            enabled: True 啟用，False 停用
        """
        self.tapo.setAutoTrackTarget(enabled)
        print(f"✓ 自動追蹤已{'啟用' if enabled else '停用'}")
    
    # ========== 隱私模式 ==========
    
    def enable_privacy_mode(self):
        """啟用隱私模式（遮蔽鏡頭）"""
        self.tapo.setPrivacyMode(True)
        print("✓ 隱私模式已啟用 - 鏡頭已遮蔽")
    
    def disable_privacy_mode(self):
        """停用隱私模式"""
        self.tapo.setPrivacyMode(False)
        print("✓ 隱私模式已停用")
    
    # ========== 巡邏模式 ==========
    
    def start_patrol(self, preset_ids: list, interval_seconds: int = 10):
        """
        開始巡邏模式（在多個預設位置之間循環）
        
        Args:
            preset_ids: 預設位置 ID 列表
            interval_seconds: 每個位置停留時間（秒）
        """
        print(f"🔄 開始巡邏模式，位置數量: {len(preset_ids)}")
        try:
            while True:
                for preset_id in preset_ids:
                    self.goto_preset(preset_id)
                    print(f"   停留 {interval_seconds} 秒...")
                    time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n✓ 巡邏模式已停止")
    
    # ========== 工具方法 ==========
    
    def export_config(self, filename: str = "tapo_config.json"):
        """
        匯出當前配置
        
        Args:
            filename: 輸出檔案名稱
        """
        config = {
            "host": self.host,
            "motor_capability": self.motor_capability,
            "presets": self.tapo.getPresets() if self.tapo else {},
            "auto_track": self.get_auto_track() if self.tapo else False,
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置已匯出到 {filename}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        獲取完整設備資訊
        
        Returns:
            dict: 設備資訊
        """
        return self.tapo.getBasicInfo()


def demo():
    """示範用法"""
    print("=" * 50)
    print("Tapo C225 PTZ 控制系統 - 示範")
    print("=" * 50)
    
    # 配置（請根據實際環境修改）
    HOST = "192.168.1.100"  # 攝影機 IP
    USER = "admin"
    PASSWORD = "your_password"  # TP-Link 雲端密碼
    
    # 建立控制器
    controller = TapoC225Controller(HOST, USER, PASSWORD)
    
    # 連接
    if not controller.connect():
        return
    
    print("\n--- 基本操作示範 ---")
    
    # 1. 獲取預設位置
    print("\n1. 獲取預設位置:")
    presets = controller.get_presets()
    
    # 2. 移動控制
    print("\n2. 移動控制:")
    print("   向右移動 10 單位...")
    controller.move_right(10)
    time.sleep(2)
    
    print("   向上移動 5 單位...")
    controller.move_up(5)
    time.sleep(2)
    
    # 3. 儲存當前位置
    print("\n3. 儲存當前位置為預設:")
    controller.save_preset("測試位置_1")
    
    # 4. 校準（回到預設位置）
    print("\n4. 執行校準:")
    controller.calibrate()
    time.sleep(3)
    
    # 5. 自動追蹤
    print("\n5. 自動追蹤設定:")
    controller.get_auto_track()
    
    # 6. 匯出配置
    print("\n6. 匯出配置:")
    controller.export_config()
    
    print("\n" + "=" * 50)
    print("示範完成")
    print("=" * 50)


if __name__ == "__main__":
    demo()
