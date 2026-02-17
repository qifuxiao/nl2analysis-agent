'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:30:20
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:30:23
FilePath: /nl2analysis-agent/app/utils/sse.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
def sse_pack(data: dict) -> str:
    from app.utils.json_utils import safe_json_dumps
    return f"data: {safe_json_dumps(data)}\n\n"
