#!/usr/bin/env python3
"""
Tapo C225 多攝影機管理器
支援同時控制多台 Tapo C225 攝影機

適用於：
- 辦公室多點監控
- 工廠生產線監控
- 倉儲管理
"""

import json
import time
from typing import Dict, List, Optional
from tapo_c225_controller import TapoC225Controller


class TapoMultiCameraManager:
    """多攝影機管理器"""
    
    def __init__(self):
        self.cameras: Dict[str, TapoC225Controller] = {}
        self.config_file = "cameras_config.json"
    
    def add_camera(self, camera_id: str, host: str, user: str = "admin", password: str = "") -> bool:
        """
        新增攝影機
        
        Args:
            camera_id: 攝影機識別 ID（例如："cam_1", "entrance", "warehouse"）
            host: IP 位址
            user: 使用者名稱
            password: 密碼
            
        Returns:
            bool: 成功返回 True
        """
        print(f"\n--- 新增攝影機: {camera_id} ---")
        controller = TapoC225Controller(host, user, password)
        
        if controller.connect():
            self.cameras[camera_id] = controller
            print(f"✓ 攝影機 {camera_id} 已加入管理")
            return True
        else:
            print(f"✗ 無法連接攝影機 {camera_id}")
            return False
    
    def remove_camera(self, camera_id: str):
        """移除攝影機"""
        if camera_id in self.cameras:
            del self.cameras[camera_id]
            print(f"✓ 攝影機 {camera_id} 已移除")
    
    def get_camera(self, camera_id: str) -> Optional[TapoC225Controller]:
        """獲取指定攝影機控制器"""
        return self.cameras.get(camera_id)
    
    def list_cameras(self) -> List[str]:
        """列出所有攝影機"""
        print(f"\n已管理的攝影機 ({len(self.cameras)} 台):")
        for cam_id, ctrl in self.cameras.items():
            print(f"  - {cam_id}: {ctrl.host}")
        return list(self.cameras.keys())
    
    # ========== 批次操作 ==========
    
    def calibrate_all(self):
        """校準所有攝影機"""
        print("\n🔧 正在校準所有攝影機...")
        for cam_id, ctrl in self.cameras.items():
            print(f"\n  [{cam_id}]")
            try:
                ctrl.calibrate()
            except Exception as e:
                print(f"  ✗ 校準失敗: {e}")
    
    def enable_privacy_all(self):
        """啟用所有攝影機的隱私模式"""
        print("\n🔒 啟用所有攝影機隱私模式...")
        for cam_id, ctrl in self.cameras.items():
            try:
                ctrl.enable_privacy_mode()
                print(f"  ✓ {cam_id}: 隱私模式已啟用")
            except Exception as e:
                print(f"  ✗ {cam_id}: {e}")
    
    def disable_privacy_all(self):
        """停用所有攝影機的隱私模式"""
        print("\n🔓 停用所有攝影機隱私模式...")
        for cam_id, ctrl in self.cameras.items():
            try:
                ctrl.disable_privacy_mode()
                print(f"  ✓ {cam_id}: 隱私模式已停用")
            except Exception as e:
                print(f"  ✗ {cam_id}: {e}")
    
    def set_auto_track_all(self, enabled: bool):
        """設定所有攝影機的自動追蹤"""
        status = "啟用" if enabled else "停用"
        print(f"\n🎯 {status}所有攝影機自動追蹤...")
        for cam_id, ctrl in self.cameras.items():
            try:
                ctrl.set_auto_track(enabled)
                print(f"  ✓ {cam_id}: 自動追蹤已{status}")
            except Exception as e:
                print(f"  ✗ {cam_id}: {e}")
    
    def goto_preset_all(self, preset_id: str):
        """
        讓所有攝影機移動到指定預設位置
        
        Args:
            preset_id: 預設位置 ID（所有攝影機都需要有此預設）
        """
        print(f"\n📍 所有攝影機移動到預設位置 {preset_id}...")
        for cam_id, ctrl in self.cameras.items():
            try:
                ctrl.goto_preset(preset_id)
                print(f"  ✓ {cam_id}: 移動到預設 {preset_id}")
            except Exception as e:
                print(f"  ✗ {cam_id}: {e}")
    
    def get_all_presets(self) -> Dict[str, Dict]:
        """獲取所有攝影機的預設位置"""
        print("\n📋 獲取所有攝影機預設位置...")
        all_presets = {}
        for cam_id, ctrl in self.cameras.items():
            try:
                presets = ctrl.tapo.getPresets()
                all_presets[cam_id] = presets
                print(f"  {cam_id}: {len(presets)} 個預設位置")
            except Exception as e:
                print(f"  ✗ {cam_id}: {e}")
                all_presets[cam_id] = {}
        return all_presets
    
    # ========== 場景管理 ==========
    
    def create_scene(self, scene_name: str, camera_presets: Dict[str, str]):
        """
        建立場景（多攝影機預設位置組合）
        
        Args:
            scene_name: 場景名稱
            camera_presets: {camera_id: preset_id} 字典
            
        Example:
            manager.create_scene("日間模式", {
                "entrance": "1",
                "warehouse": "2",
                "office": "1"
            })
        """
        scenes_file = "scenes.json"
        
        # 讀取現有場景
        try:
            with open(scenes_file, 'r', encoding='utf-8') as f:
                scenes = json.load(f)
        except FileNotFoundError:
            scenes = {}
        
        # 新增場景
        scenes[scene_name] = camera_presets
        
        # 儲存
        with open(scenes_file, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已建立場景: {scene_name}")
    
    def apply_scene(self, scene_name: str):
        """
        套用場景
        
        Args:
            scene_name: 場景名稱
        """
        scenes_file = "scenes.json"
        
        try:
            with open(scenes_file, 'r', encoding='utf-8') as f:
                scenes = json.load(f)
        except FileNotFoundError:
            print(f"✗ 找不到場景檔案")
            return
        
        if scene_name not in scenes:
            print(f"✗ 場景 '{scene_name}' 不存在")
            return
        
        print(f"\n🎬 套用場景: {scene_name}")
        camera_presets = scenes[scene_name]
        
        for cam_id, preset_id in camera_presets.items():
            if cam_id in self.cameras:
                try:
                    self.cameras[cam_id].goto_preset(preset_id)
                    print(f"  ✓ {cam_id} -> 預設 {preset_id}")
                except Exception as e:
                    print(f"  ✗ {cam_id}: {e}")
            else:
                print(f"  ⚠ {cam_id} 未連接")
    
    def list_scenes(self) -> List[str]:
        """列出所有場景"""
        scenes_file = "scenes.json"
        
        try:
            with open(scenes_file, 'r', encoding='utf-8') as f:
                scenes = json.load(f)
            
            print(f"\n已儲存的場景 ({len(scenes)} 個):")
            for name, presets in scenes.items():
                print(f"  - {name}:")
                for cam_id, preset_id in presets.items():
                    print(f"      {cam_id} -> 預設 {preset_id}")
            
            return list(scenes.keys())
        except FileNotFoundError:
            print("尚未建立任何場景")
            return []
    
    # ========== 配置管理 ==========
    
    def save_config(self, filename: str = None):
        """
        儲存攝影機配置
        
        Args:
            filename: 配置檔案名稱
        """
        if filename is None:
            filename = self.config_file
        
        config = {}
        for cam_id, ctrl in self.cameras.items():
            config[cam_id] = {
                "host": ctrl.host,
                "user": ctrl.user,
                # 注意：不儲存密碼，需要另外處理
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置已儲存到 {filename}")
    
    def load_config(self, filename: str = None, password: str = ""):
        """
        載入攝影機配置
        
        Args:
            filename: 配置檔案名稱
            password: 所有攝影機使用的密碼（假設相同）
        """
        if filename is None:
            filename = self.config_file
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n從 {filename} 載入配置...")
            for cam_id, cam_config in config.items():
                self.add_camera(
                    cam_id,
                    cam_config["host"],
                    cam_config.get("user", "admin"),
                    password
                )
        except FileNotFoundError:
            print(f"✗ 找不到配置檔案: {filename}")
    
    def export_status_report(self, filename: str = "status_report.json"):
        """
        匯出狀態報告
        
        Args:
            filename: 報告檔案名稱
        """
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cameras": len(self.cameras),
            "cameras": {}
        }
        
        for cam_id, ctrl in self.cameras.items():
            try:
                info = ctrl.get_device_info()
                device_info = info.get("device_info", {}).get("basic_info", {})
                
                report["cameras"][cam_id] = {
                    "host": ctrl.host,
                    "model": device_info.get("device_model", "Unknown"),
                    "firmware": device_info.get("sw_version", "Unknown"),
                    "motor_capability": ctrl.motor_capability,
                    "presets": ctrl.tapo.getPresets(),
                    "status": "online"
                }
            except Exception as e:
                report["cameras"][cam_id] = {
                    "host": ctrl.host,
                    "status": "error",
                    "error": str(e)
                }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 狀態報告已匯出到 {filename}")


def demo():
    """示範多攝影機管理"""
    print("=" * 60)
    print("Tapo C225 多攝影機管理系統 - 示範")
    print("=" * 60)
    
    manager = TapoMultiCameraManager()
    
    # 假設有三台攝影機（請根據實際環境修改）
    cameras_config = [
        ("entrance", "192.168.1.101"),
        ("warehouse", "192.168.1.102"),
        ("office", "192.168.1.103"),
    ]
    
    PASSWORD = "your_password"  # TP-Link 雲端密碼
    
    # 新增攝影機
    print("\n1. 新增攝影機")
    for cam_id, host in cameras_config:
        manager.add_camera(cam_id, host, "admin", PASSWORD)
    
    # 列出所有攝影機
    print("\n2. 列出攝影機")
    manager.list_cameras()
    
    # 獲取所有預設位置
    print("\n3. 獲取所有預設位置")
    all_presets = manager.get_all_presets()
    
    # 建立場景
    print("\n4. 建立場景")
    manager.create_scene("日間監控", {
        "entrance": "1",
        "warehouse": "1",
        "office": "1"
    })
    
    manager.create_scene("夜間巡邏", {
        "entrance": "2",
        "warehouse": "2",
        "office": "2"
    })
    
    # 列出場景
    print("\n5. 列出場景")
    manager.list_scenes()
    
    # 套用場景
    print("\n6. 套用場景")
    manager.apply_scene("日間監控")
    
    # 批次操作
    print("\n7. 批次操作 - 啟用自動追蹤")
    manager.set_auto_track_all(True)
    
    # 儲存配置
    print("\n8. 儲存配置")
    manager.save_config()
    
    # 匯出狀態報告
    print("\n9. 匯出狀態報告")
    manager.export_status_report()
    
    print("\n" + "=" * 60)
    print("示範完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
