import sqlite3
import pandas as pd
import streamlit as st


class GenericDataManager:
    def __init__(self, db_path='announcements.db', table_name='warehouse_management'):
        """
        初始化通用数据管理器
        :param db_path: SQLite数据库文件路径
        :param table_name: 要管理的表名
        """
        self.db_path = db_path
        self.table_name = table_name
        self.conn = None
        self.cursor = None
        self.columns = []
        self.primary_key = '代码'  # 假设主键为"代码"

        # 初始化数据库连接
        self.connect_db()

        # 获取表结构信息
        self.get_table_structure()

    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            st.error(f"数据库连接失败: {str(e)}")
            raise

    def get_table_structure(self):
        """获取表结构信息"""
        try:
            # 获取所有列名
            self.cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns_info = self.cursor.fetchall()
            self.columns = [col[1] for col in columns_info]

            # 尝试确定主键
            self.cursor.execute(f"PRAGMA table_info({self.table_name})")
            for col in self.cursor.fetchall():
                if col[5] == 1:  # 主键标志
                    self.primary_key = col[1]
        except sqlite3.Error as e:
            st.error(f"获取表结构失败: {str(e)}")

    def get_all_data(self):
        """获取所有数据"""
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=self.columns)
        except sqlite3.Error as e:
            st.error(f"获取数据失败: {str(e)}")
            return pd.DataFrame()

    def get_row_by_id(self, row_id):
        """根据主键获取一行数据"""
        try:
            self.cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?",
                (row_id,)
            )
            row = self.cursor.fetchone()
            if row:
                return dict(zip(self.columns, row))
            return None
        except sqlite3.Error as e:
            st.error(f"获取行数据失败: {str(e)}")
            return None

    def add_row(self, row_data):
        """添加新行"""
        try:
            # 构建插入语句
            columns = ', '.join(row_data.keys())
            placeholders = ', '.join(['?'] * len(row_data))
            values = tuple(row_data.values())

            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"添加行失败: {str(e)}")
            return False

    def update_cell(self, row_id, column_name, new_value):
        """更新单个单元格"""
        try:
            query = f"UPDATE {self.table_name} SET {column_name} = ? WHERE {self.primary_key} = ?"
            self.cursor.execute(query, (new_value, row_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"更新单元格失败: {str(e)}")
            return False

    def update_row(self, row_id, new_data):
        """更新整行数据"""
        try:
            # 构建更新语句
            set_clause = ', '.join([f"{col} = ?" for col in new_data.keys()])
            values = tuple(new_data.values()) + (row_id,)

            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"更新行失败: {str(e)}")
            return False

    def delete_row(self, row_id):
        """删除行"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
            self.cursor.execute(query, (row_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"删除行失败: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()