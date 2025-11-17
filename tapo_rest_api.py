#!/usr/bin/env python3
"""
Tapo C225 REST API Server
提供 HTTP REST API 介面來控制 Tapo C225 攝影機

使用方式:
    python tapo_rest_api.py

API 端點:
    GET  /status              - 獲取攝影機狀態
    GET  /presets             - 獲取所有預設位置
    POST /move                - 移動攝影機 (body: {"x": 10, "y": 5})
    POST /goto_preset         - 移動到預設位置 (body: {"preset_id": "1"})
    POST /save_preset         - 儲存當前位置 (body: {"name": "位置名稱"})
    POST /calibrate           - 校準馬達
    POST /privacy_mode        - 設定隱私模式 (body: {"enabled": true/false})
    POST /auto_track          - 設定自動追蹤 (body: {"enabled": true/false})
"""

from flask import Flask, jsonify, request
from tapo_c225_controller import TapoC225Controller
import os

app = Flask(__name__)

# 配置 - 可透過環境變數設定
TAPO_HOST = os.environ.get("TAPO_HOST", "192.168.1.100")
TAPO_USER = os.environ.get("TAPO_USER", "admin")
TAPO_PASSWORD = os.environ.get("TAPO_PASSWORD", "")

# 全域控制器實例
controller = None


def get_controller():
    """獲取或建立控制器實例"""
    global controller
    if controller is None:
        controller = TapoC225Controller(TAPO_HOST, TAPO_USER, TAPO_PASSWORD)
        if not controller.connect():
            raise Exception("無法連接到攝影機")
    return controller


@app.route("/status", methods=["GET"])
def get_status():
    """獲取攝影機狀態"""
    try:
        ctrl = get_controller()
        info = ctrl.get_device_info()
        return jsonify({
            "success": True,
            "data": {
                "device_info": info.get("device_info", {}).get("basic_info", {}),
                "motor_capability": ctrl.motor_capability,
                "connected": True
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/presets", methods=["GET"])
def get_presets():
    """獲取所有預設位置"""
    try:
        ctrl = get_controller()
        presets = ctrl.get_presets()
        return jsonify({
            "success": True,
            "data": presets
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/move", methods=["POST"])
def move():
    """
    移動攝影機
    Body: {"x": 10, "y": 5}
    """
    try:
        data = request.get_json()
        x = int(data.get("x", 0))
        y = int(data.get("y", 0))
        
        ctrl = get_controller()
        result = ctrl.move(x, y)
        
        return jsonify({
            "success": True,
            "message": f"已移動 X={x}, Y={y}",
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/move/left", methods=["POST"])
def move_left():
    """向左移動"""
    try:
        data = request.get_json() or {}
        amount = int(data.get("amount", 10))
        ctrl = get_controller()
        result = ctrl.move_left(amount)
        return jsonify({"success": True, "message": f"向左移動 {amount}", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/move/right", methods=["POST"])
def move_right():
    """向右移動"""
    try:
        data = request.get_json() or {}
        amount = int(data.get("amount", 10))
        ctrl = get_controller()
        result = ctrl.move_right(amount)
        return jsonify({"success": True, "message": f"向右移動 {amount}", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/move/up", methods=["POST"])
def move_up():
    """向上移動"""
    try:
        data = request.get_json() or {}
        amount = int(data.get("amount", 5))
        ctrl = get_controller()
        result = ctrl.move_up(amount)
        return jsonify({"success": True, "message": f"向上移動 {amount}", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/move/down", methods=["POST"])
def move_down():
    """向下移動"""
    try:
        data = request.get_json() or {}
        amount = int(data.get("amount", 5))
        ctrl = get_controller()
        result = ctrl.move_down(amount)
        return jsonify({"success": True, "message": f"向下移動 {amount}", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/goto_preset", methods=["POST"])
def goto_preset():
    """
    移動到預設位置
    Body: {"preset_id": "1"}
    """
    try:
        data = request.get_json()
        preset_id = str(data.get("preset_id"))
        
        if not preset_id:
            return jsonify({"success": False, "error": "缺少 preset_id"}), 400
        
        ctrl = get_controller()
        result = ctrl.goto_preset(preset_id)
        
        return jsonify({
            "success": True,
            "message": f"正在移動到預設位置 {preset_id}",
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/save_preset", methods=["POST"])
def save_preset():
    """
    儲存當前位置為預設
    Body: {"name": "位置名稱"}
    """
    try:
        data = request.get_json()
        name = data.get("name")
        
        if not name:
            return jsonify({"success": False, "error": "缺少 name"}), 400
        
        ctrl = get_controller()
        result = ctrl.save_preset(name)
        
        return jsonify({
            "success": True,
            "message": f"已儲存預設位置: {name}",
            "data": {"saved": result}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/delete_preset", methods=["POST"])
def delete_preset():
    """
    刪除預設位置
    Body: {"preset_id": "1"}
    """
    try:
        data = request.get_json()
        preset_id = str(data.get("preset_id"))
        
        if not preset_id:
            return jsonify({"success": False, "error": "缺少 preset_id"}), 400
        
        ctrl = get_controller()
        result = ctrl.delete_preset(preset_id)
        
        return jsonify({
            "success": True,
            "message": f"已刪除預設位置 {preset_id}",
            "data": {"deleted": result}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/calibrate", methods=["POST"])
def calibrate():
    """校準馬達（回到預設位置）"""
    try:
        ctrl = get_controller()
        result = ctrl.calibrate()
        return jsonify({
            "success": True,
            "message": "校準完成",
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/privacy_mode", methods=["GET"])
def get_privacy_mode():
    """獲取隱私模式狀態"""
    try:
        ctrl = get_controller()
        status = ctrl.tapo.getPrivacyMode()
        enabled = status.get("enabled") == "on"
        return jsonify({
            "success": True,
            "data": {"enabled": enabled}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/privacy_mode", methods=["POST"])
def set_privacy_mode():
    """
    設定隱私模式
    Body: {"enabled": true/false}
    """
    try:
        data = request.get_json()
        enabled = data.get("enabled", False)
        
        ctrl = get_controller()
        if enabled:
            ctrl.enable_privacy_mode()
        else:
            ctrl.disable_privacy_mode()
        
        return jsonify({
            "success": True,
            "message": f"隱私模式已{'啟用' if enabled else '停用'}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/auto_track", methods=["GET"])
def get_auto_track():
    """獲取自動追蹤狀態"""
    try:
        ctrl = get_controller()
        enabled = ctrl.get_auto_track()
        return jsonify({
            "success": True,
            "data": {"enabled": enabled}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/auto_track", methods=["POST"])
def set_auto_track():
    """
    設定自動追蹤
    Body: {"enabled": true/false}
    """
    try:
        data = request.get_json()
        enabled = data.get("enabled", False)
        
        ctrl = get_controller()
        ctrl.set_auto_track(enabled)
        
        return jsonify({
            "success": True,
            "message": f"自動追蹤已{'啟用' if enabled else '停用'}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """API 首頁"""
    return jsonify({
        "name": "Tapo C225 REST API",
        "version": "1.0.0",
        "endpoints": {
            "GET /status": "獲取攝影機狀態",
            "GET /presets": "獲取所有預設位置",
            "POST /move": "移動攝影機 (body: {x, y})",
            "POST /move/left": "向左移動 (body: {amount})",
            "POST /move/right": "向右移動 (body: {amount})",
            "POST /move/up": "向上移動 (body: {amount})",
            "POST /move/down": "向下移動 (body: {amount})",
            "POST /goto_preset": "移動到預設位置 (body: {preset_id})",
            "POST /save_preset": "儲存當前位置 (body: {name})",
            "POST /delete_preset": "刪除預設位置 (body: {preset_id})",
            "POST /calibrate": "校準馬達",
            "GET /privacy_mode": "獲取隱私模式狀態",
            "POST /privacy_mode": "設定隱私模式 (body: {enabled})",
            "GET /auto_track": "獲取自動追蹤狀態",
            "POST /auto_track": "設定自動追蹤 (body: {enabled})",
        }
    })


if __name__ == "__main__":
    print("=" * 50)
    print("Tapo C225 REST API Server")
    print("=" * 50)
    print(f"攝影機 IP: {TAPO_HOST}")
    print(f"使用者: {TAPO_USER}")
    print("-" * 50)
    
    # 啟動伺服器
    app.run(host="0.0.0.0", port=5000, debug=True)
