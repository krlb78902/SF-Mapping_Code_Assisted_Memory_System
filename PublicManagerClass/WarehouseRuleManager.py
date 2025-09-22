import datetime
import re  # 确保导入 re 模块
import sqlite3
import pandas as pd


class WarehouseRuleManager:
    def __init__(self, db_path='announcements.db'):
        """
        初始化仓库规则管理器
        :param db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self.warehouse_rules = None
        self.last_load_time = None

    def search_flows(self, query):
        """
        根据查询字符串搜索流向（模糊搜索）
        :param query: 查询字符串
        :return: 匹配的流向列表
        """
        # 确保规则已加载
        if self.warehouse_rules is None:
            self.warehouse_rules = self.load_rules_from_database()  # 修复：赋值给 self.warehouse_rules

        results = []

        # 如果查询为空，返回空结果
        if not query:
            return results

        # 转换为小写以便不区分大小写搜索
        query_lower = query.lower()

        for code, rule_info in self.warehouse_rules.items():
            # 检查代码是否匹配
            if query_lower in code.lower():
                results.append({
                    "type": "代码",
                    "code": code,
                    "name": rule_info['name'],
                    "mapping": rule_info['mapping']
                })
                continue

            # 检查流向名称是否匹配
            if query_lower in rule_info['name'].lower():
                results.append({
                    "type": "流向",
                    "code": code,
                    "name": rule_info['name'],
                    "mapping": rule_info['mapping']
                })
                continue

            # 检查映射是否匹配
            if query_lower in rule_info['mapping'].lower():
                results.append({
                    "type": "映射",
                    "code": code,
                    "name": rule_info['name'],
                    "mapping": rule_info['mapping']
                })

        return results

    @staticmethod
    def highlight_match(text, query):
        """
        高亮显示匹配的文本部分
        :param text: 原始文本
        :param query: 查询字符串
        :return: 带有高亮标记的HTML文本
        """
        if not query:
            return text

        # 使用正则表达式查找匹配部分（不区分大小写）
        pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="suggestion-highlight">\1</span>', text)
        return highlighted

    def get_database_connection(self):
        """
        创建并返回数据库连接
        :return: sqlite3.Connection对象
        """
        try:
            # 连接到SQLite数据库
            conn = sqlite3.connect(self.db_path)
            # 设置行工厂，使返回的行作为字典而不是元组
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")
            raise

    def load_rules_from_database(self, force_reload=False):
        """
        从数据库加载规则数据并转换为字典格式
        :param force_reload: 是否强制重新加载数据
        :return: 规则字典
        """
        # 如果已经加载过且不需要强制重新加载，则直接返回缓存
        if self.warehouse_rules is not None and not force_reload:
            return self.warehouse_rules

        warehouse_rules = {}
        conn = None

        try:
            # 获取数据库连接
            conn = self.get_database_connection()
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

            # 更新缓存
            self.warehouse_rules = warehouse_rules
            self.last_load_time = datetime.datetime.now()

        except sqlite3.Error as e:
            print(f"数据库查询错误: {e}")
            return {}
        finally:
            # 确保连接被关闭
            if conn:
                conn.close()

        return warehouse_rules

    def load_single_rule_from_db(self, code):
        """
        根据流向代码从数据库加载单条规则（优化版，减少内存使用）
        :param code: 流向代码
        :return: 单条规则字典或None
        """
        conn = None
        try:
            conn = self.get_database_connection()
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

    @staticmethod
    def parse_time_rule(rule_str, current_time):
        """
        解析自定义的时间规则字符串。
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

    def find_flow_by_mapping(self, mapping):
        """
        根据映射码查找对应的流向代码
        :param mapping: 映射码
        :return: 流向代码或None
        """
        # 确保规则已加载
        if self.warehouse_rules is None:
            self.load_rules_from_database()

        for code, rule_info in self.warehouse_rules.items():
            if rule_info['mapping'] == mapping:
                return code
        return None

    def resolve_attached_flow(self, code, visited=None):
        """
        解析挂靠流向，处理多级挂靠和循环挂靠
        :param code: 当前流向代码
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
        rule_info = self.warehouse_rules.get(code) if self.warehouse_rules else self.load_single_rule_from_db(code)
        if not rule_info:
            return code

        # 检查是否有挂靠流向（映射码）
        attached_mapping = rule_info.get('挂靠流向')
        if attached_mapping:
            # 根据映射码查找对应的流向代码
            attached_code = self.find_flow_by_mapping(attached_mapping)

            if attached_code and (self.warehouse_rules is None or attached_code in self.warehouse_rules):
                print(f"流向 {code} 挂靠到 {attached_code} (映射码: {attached_mapping})")
                return self.resolve_attached_flow(attached_code, visited)
            else:
                print(f"警告: 找不到映射码 {attached_mapping} 对应的流向")

        return code

    def find_current_locations(self, code, current_time):
        """
        根据流向代码和当前时间查找当前应使用的物理位置。
        :param code: 流向代码，如 "574W"
        :param current_time: 当前时间
        :return: 返回一个列表，包含所有适用的物理位置信息
        """
        # 如果未加载规则，则尝试加载单条规则
        if self.warehouse_rules is None:
            rule_info = self.load_single_rule_from_db(code)
        else:
            rule_info = self.warehouse_rules.get(code)

        if not rule_info:
            return None

        # 保存原始流向名称
        original_flow_name = rule_info['name']

        # 检查是否有挂靠流向
        final_code = code
        if rule_info.get('挂靠流向'):
            # 确保规则已加载（如果使用缓存）
            if self.warehouse_rules is None:
                self.load_rules_from_database()

            # 解析挂靠流向链
            final_code = self.resolve_attached_flow(code)
            print(f"流向 {code} 最终挂靠到 {final_code}")

            # 获取最终流向的规则
            if self.warehouse_rules:
                rule_info = self.warehouse_rules.get(final_code, rule_info)
            else:
                rule_info = self.load_single_rule_from_db(final_code) or rule_info

        # 存储所有适用的位置
        applicable_locations = []

        # 遍历该代码的所有位置规则，检查哪些在当前时间生效
        for loc_rule in rule_info["location_rules"]:
            if self.parse_time_rule(loc_rule["rule"], current_time):
                applicable_locations.append({
                    "映射": rule_info["mapping"],
                    "流向": rule_info["name"],
                    "原始流向名称": original_flow_name,  # 保存原始流向名称
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
                "原始流向名称": original_flow_name,  # 保存原始流向名称
                "当前物理位置": "未知（未找到适用于当前时间的位置规则）",
                "是否挂靠": final_code != code,
                "原始代码": code,
                "最终代码": final_code
            })

        return applicable_locations


# —————— 以下是主程序交互部分 ——————
if __name__ == '__main__':
    print("流向代码查询系统（数据库版）")

    # 创建仓库规则管理器
    rule_manager = WarehouseRuleManager()

    # 预加载所有规则到内存（适用于数据量不大且频繁查询的场景）
    print("正在从数据库加载规则数据...")
    try:
        warehouse_rules = rule_manager.load_rules_from_database()
        print(f"成功从数据库加载 {len(warehouse_rules)} 条规则")

        # 显示前5个代码作为示例
        print("可用代码示例:", list(warehouse_rules.keys())[:5])

    except Exception as e:
        print(f"加载数据时出错: {e}")
        print("将使用按需查询模式")

    print("\n请输入流向代码 (例如: 574W, 574TJL, S574WJ): ")
    target_code = input().strip()

    # 获取当前系统时间
    now = datetime.datetime.now()
    print(f"当前系统时间: {now.strftime('%Y-%m-%d %H:%M:%S 星期%w')}")

    # 查询并输出结果
    results = rule_manager.find_current_locations(target_code, now)
    if results:
        print(f"\n查询结果:")
        print(f"流向代码: {target_code}")

        # 如果是挂靠结果，显示原始流向和最终流向
        if results[0]['是否挂靠']:
            print(f"原始流向: {results[0]['原始流向名称']} (代码: {target_code})")
            print(f"最终流向: {results[0]['流向']} (代码: {results[0]['最终代码']})")
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