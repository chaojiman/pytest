from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

# 数据库文件路径
DATABASE = 'students.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建学生表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # 插入10个中国人名字
    students = [
        '张三', '李四', '王五', '赵六', '陈七',
        '刘八', '杨九', '黄十', '周小明', '吴小红'
    ]
    
    for name in students:
        try:
            cursor.execute('INSERT INTO students (name) VALUES (?)', (name,))
        except sqlite3.IntegrityError:
            # 如果名字已存在，跳过
            pass
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_student():
    """查询学生是否在班级里"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '请输入姓名'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM students WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return jsonify({
            'found': True,
            'message': f'{name} 在班级里',
            'name': name
        })
    else:
        return jsonify({
            'found': False,
            'message': f'{name} 不在班级里',
            'name': name
        })

@app.route('/students', methods=['GET'])
def get_all_students():
    """获取所有学生列表"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM students ORDER BY name')
    students = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({'students': students})

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print("数据库初始化完成")
    
    # 获取端口号（部署平台会提供PORT环境变量）
    port = int(os.environ.get('PORT', 5001))
    print(f"服务器启动在端口 {port}")
    app.run(debug=False, host='0.0.0.0', port=port)