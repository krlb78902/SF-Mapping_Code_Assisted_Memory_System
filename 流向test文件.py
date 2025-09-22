import datetime
import sqlite3
import pandas as pd


def get_database_connection():
    """
    创建并返回数据库连接
    :return: sqlite3.Connection对象
    """
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('PublicManagerClass/announcements.db')
        # 设置行工厂，使返回的行作为字典而不是元组
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接失败: {e}")
        raise


def load_rules_from_database():
    """
    从数据库加载规则数据并转换为字典格式
    :return: 规则字典
    """
    warehouse_rules = {}

    try:
        # 获取数据库连接
        conn = get_database_connection()
        cursor = conn.cursor()

        # 执行查询获取所有规则
        cursor.execute("SELECT * FROM warehouse_management")
        rows = cursor.fetchall()

        for row in rows:
            # 将sqlite3.Row转换为字典，方便访问
            row_dict = dict(row)
            code = row_dict['代码']  # 使用中文字段名

            # 构建位置规则列表
            location_rules = []

            # 添加物理位置1的规则（如果存在）
            if row_dict['物理位置1'] and row_dict['位置1适用时间']:  # 使用中文字段名
                location_rules.append({
                    "location": row_dict['物理位置1'],  # 使用中文字段名
                    "rule": row_dict['位置1适用时间']  # 使用中文字段名
                })

            # 添加物理位置2的规则（如果存在）
            if row_dict['物理位置2'] and row_dict['位置2适用时间']:  # 使用中文字段名
                location_rules.append({
                    "location": row_dict['物理位置2'],  # 使用中文字段名
                    "rule": row_dict['位置2适用时间']  # 使用中文字段名
                })

            # 构建规则条目
            warehouse_rules[code] = {
                "mapping": row_dict['映射'],  # 使用中文字段名
                "name": row_dict['流向'],  # 使用中文字段名
                "location_rules": location_rules,
                "挂靠流向": row_dict.get('挂靠流向', None)  # 新增挂靠流向字段
            }

    except sqlite3.Error as e:
        print(f"数据库查询错误: {e}")
        return {}
    finally:
        # 确保连接被关闭
        if conn:
            conn.close()

    return warehouse_rules


def load_single_rule_from_db(code):
    """
    根据流向代码从数据库加载单条规则（优化版，减少内存使用）
    :param code: 流向代码
    :return: 单条规则字典或None
    """
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        # 使用参数化查询防止SQL注入
        cursor.execute(
            "SELECT * FROM warehouse_management WHERE 代码 = ?",  # 使用中文字段名
            (code,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        row_dict = dict(row)
        location_rules = []

        # 添加物理位置1的规则（如果存在）
        if row_dict['物理位置1'] and row_dict['位置1适用时间']:  # 使用中文字段名
            location_rules.append({
                "location": row_dict['物理位置1'],  # 使用中文字段名
                "rule": row_dict['位置1适用时间']  # 使用中文字段名
            })

        # 添加物理位置2的规则（如果存在）
        if row_dict['物理位置2'] and row_dict['位置2适用时间']:  # 使用中文字段名
            location_rules.append({
                "location": row_dict['物理位置2'],  # 使用中文字段名
                "rule": row_dict['位置2适用时间']  # 使用中文字段名
            })

        return {
            "mapping": row_dict['映射'],  # 使用中文字段名
            "name": row_dict['流向'],  # 使用中文字段名
            "location_rules": location_rules,
            "挂靠流向": row_dict.get('挂靠流向', None)  # 新增挂靠流向字段
        }

    except sqlite3.Error as e:
        print(f"数据库查询错误: {e}")
        return None
    finally:
        if conn:
            conn.close()


def parse_time_rule(rule_str, current_time):
    """
    解析您自定义的时间规则字符串。
    :param rule_str: 规则字符串，如 "7:0600and1-7:1230"
    :param current_time: 当前时间 datetime.datetime 对象
    :return: 如果当前时间符合规则，返回True，否则返回False
    """
    if rule_str == "all":
        return True

    current_weekday = current_time.weekday()
    current_time_str = current_time.strftime("%H%M")
    current_weekday_num = current_weekday + 1

    # 处理'or'连接的条件
    conditions = rule_str.split('or')
    for condition in conditions:
        # 处理'and'连接的条件
        and_conditions = condition.split('and')
        and_match = True

        for and_cond in and_conditions:
            if ':' in and_cond:
                weekday_part, time_part = and_cond.split(':', 1)
                target_time = time_part.strip()

                if '-' in weekday_part:
                    start_day, end_day = map(int, weekday_part.split('-'))
                    weekday_match = start_day <= current_weekday_num <= end_day
                else:
                    single_day = int(weekday_part)
                    weekday_match = (current_weekday_num == single_day)

                if not weekday_match:
                    and_match = False
                    break

                # 检查时间条件
                if current_time_str > target_time:
                    and_match = False
                    break

        if and_match:
            return True

    return False


def find_flow_by_mapping(mapping, warehouse_rules):
    """
    根据映射码查找对应的流向代码
    :param mapping: 映射码
    :param warehouse_rules: 规则字典
    :return: 流向代码或None
    """
    for code, rule_info in warehouse_rules.items():
        if rule_info['mapping'] == mapping:
            return code
    return None


def resolve_attached_flow(code, warehouse_rules, visited=None):
    """
    解析挂靠流向，处理多级挂靠和循环挂靠
    :param code: 当前流向代码
    :param warehouse_rules: 规则字典
    :param visited: 已访问的流向代码集合（用于检测循环）
    :return: 最终的基础流向代码
    """
    if visited is None:
        visited = set()

    # 检测循环挂靠
    if code in visited:
        print(f"警告: 检测到循环挂靠: {' -> '.join(visited)} -> {code}")
        return code

    visited.add(code)

    # 获取当前流向规则
    rule_info = warehouse_rules.get(code)
    if not rule_info:
        return code

    # 检查是否有挂靠流向（映射码）
    attached_mapping = rule_info.get('挂靠流向')
    if attached_mapping:
        # 根据映射码查找对应的流向代码
        attached_code = find_flow_by_mapping(attached_mapping, warehouse_rules)

        if attached_code and attached_code in warehouse_rules:
            print(f"流向 {code} 挂靠到 {attached_code} (映射码: {attached_mapping})")
            return resolve_attached_flow(attached_code, warehouse_rules, visited)
        else:
            print(f"警告: 找不到映射码 {attached_mapping} 对应的流向")

    return code


def find_current_locations(code, current_time, warehouse_rules=None):
    """
    根据流向代码和当前时间查找当前应使用的物理位置。
    :param code: 流向代码，如 "574W"
    :param current_time: 当前时间
    :param warehouse_rules: 规则字典（可选）
    :return: 返回一个列表，包含所有适用的物理位置信息
    """
    # 如果未提供规则字典，则从数据库加载单条规则
    if warehouse_rules is None:
        rule_info = load_single_rule_from_db(code)
    else:
        rule_info = warehouse_rules.get(code)

    if not rule_info:
        return None

    # 检查是否有挂靠流向
    final_code = code
    if warehouse_rules and '挂靠流向' in rule_info and rule_info['挂靠流向']:
        # 解析挂靠流向链
        final_code = resolve_attached_flow(code, warehouse_rules)
        print(f"流向 {code} 最终挂靠到 {final_code}")

        # 获取最终流向的规则
        if warehouse_rules:
            rule_info = warehouse_rules.get(final_code, rule_info)
        else:
            rule_info = load_single_rule_from_db(final_code) or rule_info

    # 存储所有适用的位置
    applicable_locations = []

    # 遍历该代码的所有位置规则，检查哪些在当前时间生效
    for loc_rule in rule_info["location_rules"]:
        if parse_time_rule(loc_rule["rule"], current_time):
            applicable_locations.append({
                "映射": rule_info["mapping"],
                "流向": rule_info["name"],
                "当前物理位置": loc_rule["location"],
                "是否挂靠": final_code != code,  # 标记是否为挂靠结果
                "原始代码": code,
                "最终代码": final_code
            })

    # 如果没有找到任何生效的位置规则
    if not applicable_locations:
        applicable_locations.append({
            "映射": rule_info["mapping"],
            "流向": rule_info["name"],
            "当前物理位置": "未知（未找到适用于当前时间的位置规则）",
            "是否挂靠": final_code != code,
            "原始代码": code,
            "最终代码": final_code
        })

    return applicable_locations


# —————— 以下是主程序交互部分 ——————
if __name__ == '__main__':
    print("流向代码查询系统（数据库版）")

    # 预加载所有规则到内存（适用于数据量不大且频繁查询的场景）
    print("正在从数据库加载规则数据...")
    try:
        warehouse_rules = load_rules_from_database()
        print(f"成功从数据库加载 {len(warehouse_rules)} 条规则")

        # 显示前5个代码作为示例
        print("可用代码示例:", list(warehouse_rules.keys())[:5])

    except Exception as e:
        print(f"加载数据时出错: {e}")
        print("将使用按需查询模式")
        warehouse_rules = None

    print("\n请输入流向代码 (例如: 574W, 574TJL, S574WJ): ")
    target_code = input().strip()

    # 获取当前系统时间
    now = datetime.datetime.now()
    print(f"当前系统时间: {now.strftime('%Y-%m-%d %H:%M:%S 星期%w')}")

    # 查询并输出结果
    results = find_current_locations(target_code, now, warehouse_rules)
    if results:
        print(f"\n查询结果:")
        print(f"流向代码: {target_code}")

        # 如果是挂靠结果，显示原始流向和最终流向
        if results[0]['是否挂靠']:
            # 获取原始流向名称
            if warehouse_rules:
                original_flow_name = warehouse_rules.get(target_code, {}).get('name', '未知')
            else:
                rule_info = load_single_rule_from_db(target_code)
                original_flow_name = rule_info.get('name', '未知') if rule_info else '未知'

            # 获取最终流向名称
            final_flow_name = results[0]['流向']

            print(f"原始流向: {original_flow_name} (代码: {target_code})")
            print(f"最终流向: {final_flow_name} (代码: {results[0]['最终代码']})")
        else:
            print(f"流向: {results[0]['流向']}")

        print(f"映射: {results[0]['映射']}")

        # 输出所有适用的物理位置
        print("当前适用的物理位置:")
        for i, result in enumerate(results, 1):
            location_info = result['当前物理位置']
            if result['是否挂靠']:
                location_info += " (挂靠)"
            print(f"{i}. {location_info}")
    else:
        print(f"\n错误: 未找到流向代码 '{target_code}' 的配置信息。")