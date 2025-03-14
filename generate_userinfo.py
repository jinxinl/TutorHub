import json
import random
import string
import datetime

def generate_random_str(characters,length):
    #characters = string.ascii_letters + string.digits  # 包括大小写字母和数字
    return ''.join(random.choice(characters) for _ in range(length))

#生成指定数量的用户账号和密码，并标记部分为会员
def generate_accounts(num_accounts, password_length, members_count):
    accounts = []
    member_index = random.sample(range(num_accounts), members_count)

    for i in range(num_accounts):
        username = generate_random_str(string.ascii_letters,random.randint(4,10))  #生成用户名
        password = generate_random_str(string.ascii_letters+string.digits,password_length) #生成密码
        is_member = i in member_index  # 检查是否为会员
        accounts.append({
            'username': username,
            'password': password,
            'is_member': is_member
        })

    return accounts

#生成指定范围内的随机日期时间
def generate_random_datetime(start_year, end_year):
    start_date = datetime.datetime(start_year, 1, 1, 0, 0, 0)  # 开始日期
    end_date = datetime.datetime(end_year, 12, 31, 23, 59, 59)  # 结束日期

    # 随机生成一个时间戳
    random_timestamp = random.random() * (end_date - start_date).total_seconds()
    random_date = start_date + datetime.timedelta(seconds=random_timestamp)

    return random_date

# 生成60个账号，密码长度为12，其中33个为会员
generated_accounts = generate_accounts(num_accounts=60, password_length=12, members_count=33)

user_list = []
member_list = []
# 打印生成的账号信息
count = 1
#print(generated_accounts)
for account in generated_accounts:
    user_dict = {}
    member_dict = {}
    user_dict['UserID'] = count
    user_dict['UserName'] = account['username']
    user_dict['Password'] = account['password']
    if account['is_member'] == False:
        user_dict['Role'] = 'normal'
    else:
        user_dict['Role'] = 'member'
        member_dict['MemberID'] = count
        member_dict['StartDay'] = generate_random_datetime(start_year=2020,end_year=2026)
        member_dict['ValidityTerm'] = random.randint(2,4)

        cur_date = datetime.datetime(2024,10,31,23,59,59)
        validity_term = member_dict['ValidityTerm']
        is_available = (member_dict['StartDay'] + datetime.timedelta(days=validity_term*365)) >= cur_date
        if is_available:
            member_dict['isAvailable'] = 'yes'
        else:
            member_dict['isAvailable'] = 'no'

        member_dict['StartDay'] = member_dict['StartDay'].strftime("%Y-%m-%dT%H:%M:%S")

        member_list.append(member_dict)

    user_list.append(user_dict)
    count += 1

#print(user_list)
#print(member_list)
#print(len(member_list))

with open('dataset/processed/User.json','w',encoding='utf-8') as f:
    json.dump(user_list,f,indent=4,ensure_ascii=False)

with open('dataset/processed/Member.json','w',encoding='utf-8') as f:
    json.dump(member_list,f,indent=4,ensure_ascii=False)

advice_list = [
    {
        'UserID':0,
        'TimeStamp':"2023-12-21T00:53:43",
        'Message':"老师信息很全"
    },
    {
        'UserID': 4,
        'TimeStamp': "2021-10-21T08:53:43",
        'Message': "希望可以有更多的学校和老师信息"
    },
    {
        'UserID': 3,
        'TimeStamp': "2022-01-21T10:03:13",
        'Message': "什么时候可以出一个老师评价功能，真的很需要"
    },
    {
        'UserID': 33,
        'TimeStamp': "2024-12-21T03:03:03",
        'Message': "今年希望能保研，正在看老师，祝我上岸吧"
    },
    {
        'UserID': 6,
        'TimeStamp': "2024-01-21T13:42:41",
        'Message': "怎么没有看见我导"
    },
    {
        'UserID': 19,
        'TimeStamp': "2020-01-31T18:15:45",
        'Message': "这个学术关系网络图什么时候可以在美化一下啊，现在看上去好简陋啊哈哈哈"
    }
]

with open('dataset/processed/Advice.json','w',encoding='utf-8') as f:
    json.dump(advice_list,f,indent=4,ensure_ascii=False)