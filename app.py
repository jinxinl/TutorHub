import mysql.connector
from flask import Flask, request, redirect, render_template, jsonify, url_for, session, Response
from flask_session import Session
import operateDB
import generate_network

import json

app = Flask(__name__,static_folder='static')
app.config['SECRET_KEY'] = 'db_tutorhub' #设置密钥用于加密通话
app.config['SESSION_TYPE'] = 'filesystem' #使用文件系统存储会话数据
app.config['SESSION_COOKIE_SECURE'] = False #解决 set-cookie header doesn’t have the ‘secure’ directive
Session(app)


'''初始界面'''
@app.route('/')
def init():
    return redirect('/login')
    #return redirect('/main')


'''登录界面'''
@app.route('/login',methods=['Get','POST'])
def login():
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print("input username: ",username)
        print("input password: ",password)

        '''验证登陆是否成功'''
        sql = f"select * from User where UserName = '{username}'"
        result_tup = operateDB.db_interface(op="query",sql=sql)
        if len(result_tup) == 0: #查找不到用户
            return '<script> alert("用户不存在！");window.location.href="/login";</script>'
        else: #找的到用户
            #print(result_tup)
            real_password  =result_tup[0][2] #得到用户在数据库中的密码
            if password == real_password: #密码与用户名匹配
                #验证成功，存储用户信息到会话中
                session['username'] = username
                session['password'] = password
                session['userid'] = result_tup[0][0]
                return redirect('/main')
            else: #密码与用户名不匹配
                return '<script> alert("密码输入错误！");window.location.href="/login";</script>'

    return render_template('login.html')


'''注册界面'''
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method =='POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(new_username)
        print(new_password)
        print(confirm_password)

        '''
        验证两次密码是否填写一致
        '''
        if new_password != confirm_password:
            return render_template('register.html',error="两次输入的密码不一致")
        else:
            #收集用户账号信息，插入数据库中
            max_user_id = operateDB.db_interface(op="get_maxID",table_name="User")
            #print(max_user_id)

            new_ID = max_user_id + 1
            data = { "UserID": new_ID,
                     "UserName": new_username,
                     "Password": new_password,
                     "Role": "normal"} #第一次注册，身份都是普通用户

            #插入新用户数据
            operateDB.db_interface(op="insert_data",table_name="User",data=data)

            return redirect('/login')

    return render_template('register.html')

'''登出逻辑'''
@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('userid',None)
    session.pop('password',None)

    #重定向到登陆界面
    return redirect(url_for('login'))


'''响应搜索按钮点击事件'''
@app.route('/search',methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    if query:
        sql = f"select * from TutorBasicInformation where Name = '{query}'"
        result_tup = operateDB.db_interface(op="query",sql=sql)

        if result_tup[0] is not None:

            print("result: ",result_tup)

            key_list = ['ID','姓名','任职学校','职称','专业','研究领域','联系电话','电子邮件','个人简介']
            value_list = [elem for elem in result_tup[0]]
            result_dict = dict(zip(key_list,value_list))
            del result_dict['ID']

            if len(result_tup) > 1:
                for i in range(1,len(result_tup)):
                    result_dict['个人简介'] += (',' + result_tup[i][8])

            info_str = '\n'.join([f"{key}: {value}" for key, value in result_dict.items()])

            print("info_str: ",info_str)

            return jsonify({'redirectUrl': url_for('teacher_info', info=info_str,name=query)})
        else:
            return jsonify({'message': '未找到相关信息'}), 404

    else:
        return jsonify({'message': '未找到相关信息'}), 404


'''教师信息界面'''
@app.route('/teacher_info')
def teacher_info():
    info = request.args.get('info')
    tname = request.args.get('name')
    print("tname(/teacher_info): ",tname)
    print(info)
    tutor_school_dict, tutor_rel_list = generate_network.get_data()
    alumni_list = generate_network.transform_alumni_relation(tname, tutor_school_dict)
    #校友关系分为空与非空
    if len(alumni_list):
        alumni_graph = generate_network.create_graph(tname,alumni_list,'Alumnis')
    else:
        alumni_graph = generate_network.create_graph(tname,None)
    #师承关系分为空与非空
    if tname in tutor_rel_list.keys():
        tutor_rel_graph = generate_network.create_graph(tname,tutor_rel_list[tname],'Tutors')
    else:
        tutor_rel_graph = generate_network.create_graph(tname,None)


    return render_template('teacher_info.html',tname=tname,info=info,alumni_graph=alumni_graph,tutor_rel_graph=tutor_rel_graph)

'''响应查看导师学术关系链接点击情况'''
@app.route('/check_membership')
def check_membership():
    username = session.get('username')
    userid = session.get('userid')
    tname = request.args.get('tname')

    print("tname(/check_membership): ",tname)

    if not userid:
        return Response(json.dumps({
            'status': 'error',
            'message': '用户未登录，请先登录！',
            'redirect': '/login'
        }), mimetype='application/json; charset=utf-8')

    sql = f"select * from Member where MemberID = {userid}"
    result_tup = operateDB.db_interface(op="query", sql=sql)
    if len(result_tup) == 0:
        return Response(json.dumps({
            'status': 'error',
            'message': '请先注册会员！',
            'redirect': '/main'
        }), mimetype='application/json; charset=utf-8')
    else:
        is_member_1 = result_tup[0][-1]
        if is_member_1 == 'yes':
            #获取图表
            tutor_school_dict, tutor_rel_list = generate_network.get_data()
            alumni_list = generate_network.transform_alumni_relation(tname, tutor_school_dict)
            # 校友关系分为空与非空
            if len(alumni_list):
                alumni_graph = generate_network.create_graph(tname, alumni_list, 'Alumnis')
            else:
                alumni_graph = generate_network.create_graph(tname, None)
            # 师承关系分为空与非空
            if tname in tutor_rel_list.keys():
                tutor_rel_graph = generate_network.create_graph(tname, tutor_rel_list[tname], 'Tutors')
            else:
                tutor_rel_graph = generate_network.create_graph(tname, None)

            #展示两张图表
            return Response(json.dumps({
                'status': 'success',
                'show_graphs': True,
                'alumni_graph':alumni_graph,
                'tutor_rel_graph':tutor_rel_graph
            }), mimetype='application/json; charset=utf-8')


        elif is_member_1 == 'no':
            return Response(json.dumps({
                'status': 'error',
                'message': '您的会员已过期！',
                'redirect': '/main'
            }), mimetype='application/json; charset=utf-8')

    return Response(json.dumps({
        'status': 'error',
        'message': '未知错误',
        'redirect': '/main'
    }), mimetype='application/json; charset=utf-8')

'''个人中心'''
@app.route('/user_center')
def user_center():
    #检查用户是否已登陆
    if 'username' not in session:
        return redirect(url_for('/login')) #若未登录，重定向到登录界面

    #获取登录时的用户名与密码
    username = session.get('username')
    password = session.get('password')
    userid = session.get('userid')
    is_member = False #默认为不是会员（未注册会员/会员已过期）

    sql = f"select * from Member where MemberID = {userid}"
    result_tup = operateDB.db_interface(op="query", sql=sql)

    #是会员且未过期
    if len(result_tup)!=0:
        is_member_1 = result_tup[0][-1]
        if is_member_1 == 'yes':
            is_member = True

    return render_template('user_center.html',username=username,password=password,is_member=is_member)

'''提交反馈'''
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.json.get('feedback')
    if not feedback:
        return jsonify({'success': False, 'message': '反馈内容不能为空'})

    # 假设反馈存储在Feedback表中，包含FeedbackID, UserID, FeedbackContent, FeedbackTime
    userid = session.get('userid')

    from datetime import datetime
    cur_time = datetime.now()
    data = {"UserID": userid,
            "TimeStamp": cur_time,
            "Message":feedback}  # 第一次注册，身份都是普通用户

    # 插入新用户数据
    operateDB.db_interface(op="insert_data", table_name="Advice", data=data)
    return jsonify({'success': True, 'message': '反馈提交成功'})


'''主界面'''
@app.route('/main')
def admin():
    return render_template('main.html')

if __name__ == '__main__':
    app.run()
