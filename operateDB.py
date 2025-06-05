import json

import mysql.connector
from matplotlib.backend_bases import cursors
from mysql.connector import Error
from process_data import getTutorID

'''
mysql连接报错: Authentication plugin ‘caching_sha2_password‘ is not supported
解决方法:Terminal中输入
pip uninstall mysql-connector
pip uninstall mysql-connector-python
pip install mysql-connector-python
'''

def create_connection(host_name,user_name,user_password,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )

        print("连接成功!")
        return connection

    except Error as e:
        print(f"连接失败：{e}")
        return None

def create_table(connection,table_name,table_schema):
    cursor = connection.cursor()
    try:
        #创建表的SQL语句
        sql_create_table = f"create table {table_name} ({table_schema});"
        #执行sql语句
        cursor.execute(sql_create_table)
        #提交命令
        connection.commit()

        print(f"{table_name}表创建成功!")
    except Error as e:
        print(f"{table_name}表创建失败：{e}")
        connection.rollback()
    finally:
        cursor.close()

def insert_data(connection,table_name,data):
    cursor = connection.cursor()
    try:
        placeholders = ','.join(['%s']*len(data))
        columns = ','.join(data.keys())
        sql = f"insert into {table_name} ({columns}) values ({placeholders})"
        cursor.execute(sql,list(data.values()))
        connection.commit()

        print("数据插入成功!")

    except Error as e:
        print(f"数据插入失败：{e}")

    finally:
        cursor.close()

def query(connection,sql):
    result = None
    if sql:
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            print("查询成功！")

        except Error as e:
            print(f"查询失败：{e}")

        finally:
            cursor.close()

        return result

def update(connection,sql):
    result = None
    if sql:
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            connection.commit()  # 提交事务
            print("Update successful")
        except Exception as e:
            connection.rollback()  # 回滚事务
            print(f"Error during update: {e}")
        finally:
            cursor.close()

        return result



def get_maxID(connection,table_name):
    cursor = connection.cursor()
    try:
        if table_name == 'User':
            sql = f"select coalesce(max(UserID),0) as MaxUserID from {table_name}"

            cursor.execute(sql)

            result = cursor.fetchone()
            if result:
                max_user_id = result[0]
                return max_user_id
            else:
                print("无法获取最大的UserID")
                return None
    except Error as e:
        print(f"获取最大UsrrID出错: ",e)
        return None

    finally:
        cursor.close()

def db_interface(op='',sql='',table_name='',data=''):
    #连接到MySQL
    host_name = 'localhost'
    user_name = 'root'
    user_password = 'your_password'
    db_name = 'TutorHub'

    connection = create_connection(host_name,user_name,user_password,db_name)

    #flag =1：创建表；flag = 2：插入数据；flag = 3：查询
    tutorID_dict = getTutorID()

    '''
    cursor = connection.cursor()
    cursor.execute("drop table Member;")
    cursor.execute("drop table Advice;")
    cursor.execute("drop table User;")
    cursor.execute("drop table TutorOfTutor;")
    cursor.execute("drop table GraduateSchool;")
    cursor.execute("drop table TutorBasicInformation;")
    cursor.close()
    '''

    #创建表
    if connection and op == "create_table":

        table1_name = 'User'
        '''
        后续加上密码的加密存储
        '''
        table1_schema = """
            UserID int not null auto_increment,
            UserName varchar(255) not null unique,
            Password varchar(255) not null unique,
            Role varchar(255) not null,
            primary key (UserID),
            check(Role='normal' or Role='member')
        """
        create_table(connection,table1_name,table1_schema)

        table2_name = 'Member'
        table2_schema = """
            MemberID int not null,
            StartDay DateTime not null,
            ValidityTerm int not null,
            isAvailable varchar(5) not null,
            primary key (MemberID),
            foreign key (MemberID) references User(UserID),
            check(isAvailable='yes' or isAvailable='no')
        """
        create_table(connection,table2_name,table2_schema)

        table3_name = 'TutorBasicInformation'
        table3_schema = """
                TutorID int not null auto_increment,
                Name varchar(255) not null,
                School varchar(255) not null,
                Title varchar(255) ,
                Major varchar(255) ,
                Field varchar(255) ,
                Phone varchar(255) ,
                Email varchar(255) ,
                Introduction text not null,
                primary key (TutorID)
            """
        create_table(connection, table3_name, table3_schema)

        table4_name = 'TutorOfTutor'
        table4_schema = """
                    TutorID int not null,
                    Name varchar(255) not null,
                    TutorName varchar(255) not null,
                    primary key (TutorID),
                    foreign key (TutorID) references TutorBasicInformation(TutorID)
                """
        create_table(connection, table4_name, table4_schema)

        table5_name = 'GraduateSchool'
        table5_schema = """
                    TutorID int not null,
                    Name varchar(255) not null,
                    School varchar(255) not null,
                    primary key (TutorID),
                    foreign key (TutorID) references TutorBasicInformation(TutorID)
                """
        create_table(connection, table5_name, table5_schema)

        table6_name = 'Advice'
        table6_schema = """
                    UserID int not null,
                    TimeStamp Datetime not null,
                    Message text not null,
                    primary key (UserID,TimeStamp),
                    foreign key (UserID) references User(UserID)
                """
        create_table(connection, table6_name, table6_schema)


        connection.close()


    #插入数据
    elif connection and op == "initialize_table":

        #插入用户信息
        with open('dataset/processed/User.json', 'r', encoding='utf-8') as f:
            user_list = json.load(f)
        #for record in user_list:
        #    insert_data(connection,"User",record)

        #插入会员信息
        with open('dataset/processed/Member.json', 'r', encoding='utf-8') as f:
            member_list = json.load(f)
        #for record in member_list:
        #    record['StartDay'] = datetime.strptime(record['StartDay'],"%Y-%m-%dT%H:%M:%S")
        #    insert_data(connection,"Member",record)

        #插入反馈信息
        with open('dataset/processed/Advice.json', 'r', encoding='utf-8') as f:
            advice_list = json.load(f)
        #for record in advice_list:
        #    record['TimeStamp'] = datetime.strptime(record['TimeStamp'], "%Y-%m-%dT%H:%M:%S")
        #    insert_data(connection, "Advice", record)

        # 插入导师信息
        with open('dataset/processed/TutorBasic.json', 'r', encoding='utf-8') as f:
            tutor_basic_list = json.load(f)
        #for record in tutor_basic_list:
        #    insert_data(connection, 'TutorBasicInformation', record)

        #插入师承
        with open('dataset/processed/TutorRelation.json','r',encoding='utf-8') as f:
            tutor_rel_list = json.load(f)

        tutor_of_tutor_list = []
        for name,tutor_list in tutor_rel_list.items():
            rel_dict = {}

            rel_dict['TutorID'] = tutorID_dict[name]
            rel_dict['Name'] = name
            tutors_name = ''
            for TutorName in tutor_list:
                tutors_name = tutors_name + TutorName + ','

            tutors_name = tutors_name[:-1] #删去最后一个逗号
            rel_dict['TutorName'] = tutors_name
            tutor_of_tutor_list.append(rel_dict)

        #for record in tutor_of_tutor_list:
        #    insert_data(connection,'TutorOfTutor',record)

        #插入导师毕业学校信息
        with open("dataset/processed/AlumniRelation.json",'r',encoding='utf-8') as f:
            tutor_school_dict = json.load(f)

        #转换为{name:str ,school:list}
        converted_tutor_school_dict = {}
        for school,tutor_list in tutor_school_dict.items():
            for name in tutor_list:
                if name not in converted_tutor_school_dict.keys():
                    converted_tutor_school_dict[name] = [school]
                else:
                    converted_tutor_school_dict[name].append(school)

        tutor_school_list = []
        for name,school_list in converted_tutor_school_dict.items():
            sch_dict = {}
            sch_dict['TutorID'] = tutorID_dict[name]
            sch_dict['Name'] = name
            schools = ''
            for school in school_list:
                schools = schools + school + ','
            schools = schools[:-1]
            sch_dict['School'] = schools

            tutor_school_list.append(sch_dict)

        #for record in tutor_school_list:
        #    insert_data(connection,'GraduateSchool',record)

        connection.close()

    elif connection and op == "query":
        result = query(connection,sql=sql)
        connection.close()

        return result


    elif connection and op == "get_maxID":
        maxID = get_maxID(connection,table_name)
        connection.close()

        return maxID

    elif connection and op == "insert_data":
        insert_data(connection,table_name,data)

    elif connection and op == "update":
        update(connection,sql)
        connection.close()


        connection.close()











