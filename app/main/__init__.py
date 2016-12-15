# coding=utf-8
from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors
from app.table.models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


# 程序的路由保存在views中而错误处理程序保存在 app/main/errors.py 模块中。
# 导入这两个模块就能把路由和错误处理程序与蓝本关联起来。注意，这
# 些模块在 app/main/__init__.py 脚本的末尾导入，这是为了避免循环导入依赖，
# 因为在views.py 和 errors.py 中还要导入蓝本 main
# 字模块中的蓝本需要在app/init下注册