from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from flask_cors import CORS  # 添加CORS支持

app = Flask(__name__)
CORS(app)  # 启用CORS

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
    try:
        return render_template('index.html')
    except:
        # 如果模板文件找不到，返回一个简单的HTML页面
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>部署测试</title></head>
        <body>
        <h1>Flask应用部署成功！</h1>
        <p>但是模板文件缺失，请检查templates文件夹是否正确上传到GitHub</p>
        <a href="/students">查看学生API</a>
        </body>
        </html>
        '''

@app.route('/static-test')
def static_test():
    """测试静态文件访问"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>静态文件测试</title></head>
    <body>
    <h1>静态文件测试</h1>
    <p>如果你能看到这个页面，说明路由工作正常</p>
    <p>尝试访问 <a href="/static/test.txt" target="_blank">静态文件</a></p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """健康检查端点"""
    try:
        # 测试数据库连接
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM students')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'students_count': count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search_student():
    """查询学生是否在班级里"""
    try:
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
    except Exception as e:
        print(f"搜索错误: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/students', methods=['GET'])
def get_all_students():
    """获取所有学生列表"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM students ORDER BY name')
        students = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        print(f"返回学生列表: {students}")
        return jsonify({'students': students})
    except Exception as e:
        print(f"获取学生列表错误: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 确保应用启动时初始化数据库
init_db()
print("数据库初始化完成")

if __name__ == '__main__':
    # 获取端口号（部署平台会提供PORT环境变量）
    port = int(os.environ.get('PORT', 5001))
    print(f"服务器启动在端口 {port}")
    app.run(debug=False, host='0.0.0.0', port=port)