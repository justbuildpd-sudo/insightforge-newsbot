#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Management Server
중간에 API 계정을 추가/제거/수정할 수 있는 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify
import json
import logging
from datetime import datetime
from multi_api_manager import MultiAPIManager

app = Flask(__name__)
api_manager = MultiAPIManager()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('api_management.html')

@app.route('/api/status')
def get_status():
    """API 상태 조회"""
    try:
        usage_summary = api_manager.get_usage_summary()
        return jsonify({
            "success": True,
            "data": usage_summary
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """API 계정 목록 조회"""
    try:
        accounts = []
        for account in api_manager.accounts:
            accounts.append({
                "id": account.id,
                "client_id": account.client_id,
                "client_secret": "***" + account.client_secret[-4:],  # 보안을 위해 마스킹
                "daily_limit": account.daily_limit,
                "enabled": account.enabled,
                "priority": account.priority,
                "description": account.description,
                "used_today": account.used_today,
                "remaining": account.daily_limit - account.used_today
            })
        
        return jsonify({
            "success": True,
            "data": accounts
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/accounts', methods=['POST'])
def add_account():
    """새 API 계정 추가"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['id', 'client_id', 'client_secret', 'daily_limit']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"필수 필드 누락: {field}"
                })
        
        # 새 계정 추가
        api_manager.add_api_account(data)
        api_manager.save_config()
        
        return jsonify({
            "success": True,
            "message": f"API 계정 '{data['id']}' 추가 완료"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/accounts/<account_id>', methods=['PUT'])
def update_account(account_id):
    """API 계정 정보 업데이트"""
    try:
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        allowed_fields = ['client_id', 'client_secret', 'daily_limit', 'enabled', 'priority', 'description']
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not updates:
            return jsonify({
                "success": False,
                "error": "업데이트할 필드가 없습니다"
            })
        
        api_manager.update_api_account(account_id, updates)
        api_manager.save_config()
        
        return jsonify({
            "success": True,
            "message": f"API 계정 '{account_id}' 업데이트 완료"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """API 계정 제거"""
    try:
        api_manager.remove_api_account(account_id)
        api_manager.save_config()
        
        return jsonify({
            "success": True,
            "message": f"API 계정 '{account_id}' 제거 완료"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/reset', methods=['POST'])
def reset_usage():
    """사용량 리셋"""
    try:
        api_manager.reset_daily_usage()
        return jsonify({
            "success": True,
            "message": "사용량 리셋 완료"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/test/<account_id>')
def test_account(account_id):
    """API 계정 테스트"""
    try:
        # 해당 계정 찾기
        account = None
        for acc in api_manager.accounts:
            if acc.id == account_id:
                account = acc
                break
                
        if not account:
            return jsonify({
                "success": False,
                "error": "계정을 찾을 수 없습니다"
            })
        
        # 테스트 API 호출
        success, data, error = api_manager.make_api_call("테스트", display=1)
        
        if success:
            return jsonify({
                "success": True,
                "message": "API 테스트 성공",
                "data": data
            })
        else:
            return jsonify({
                "success": False,
                "error": f"API 테스트 실패: {error}"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
