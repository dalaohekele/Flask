# coding=utf-8
from flask import render_template,request,jsonify
from . import main

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 蓝本中的错误处理程序,使用errorhandler修饰器

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# 404和500状态响应码需要特殊处理,因为这两个错误是由 Flask 自己生成的
# 其他状态码都由 Web 服务生成，因此可在api蓝本的 errors.py 模块作为辅助函数实现
# 在错误处理程序中根据客户端请求的格式改写响应，这种技术称为内容协商 （客户端请求为JSON格式）

@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accpet_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'地址输入错误'})
        response.status_code = 404
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accpet_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'服务器出错'})
        response.status_code = 500
    return render_template('500.html'), 500