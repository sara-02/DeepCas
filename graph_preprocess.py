import json
import os
import datetime
from datetime import datetime, timedelta
import random
import sys

file_path = "../TiDeH/data/reddit_data/selected_discussion_nov.jsonlist"
with open(file_path, "r") as f:
    data=f.readlines()
n=len(data)
print(n)
sys.stdout.flush()

with open("../TiDeH/data/reddit_data/post_author.json","r") as f:
    poster_ids=json.load(f)
with open("../TiDeH/data/reddit_data/comment_author.json","r") as f:
    commenter_ids=json.load(f)

print(len(poster_ids))
print(len(commenter_ids))
sys.stdout.flush()

def updated_mapping(raw_id, t):
    global id_count
    if raw_id not in user_count_mapping:
        user_count_mapping[raw_id] = id_count
        count_user_mapping[id_count] = raw_id
        if t=="p":
            post_id_set.add(raw_id)
        else:
            comment_id_set.add(raw_id)
        id_count+=1
    return user_count_mapping[raw_id]

user_count_mapping={}
count_user_mapping={}
weight_network={}
id_count = 0
post_id_set = set()
comment_id_set = set()

for i in range(n):
    print(i)
    sys.stdout.flush()
    each_reddit = json.loads(data[i])
    key = list(each_reddit.keys())[0]
    each_reddit = each_reddit[key]
    for each_post in each_reddit:
        if len(each_post['comments']) < 10:
            continue
        user_id = each_post['id']
        real_name = poster_ids[user_id]
        if real_name == '[deleted]':
            user_id_count = updated_mapping(user_id, "p")
        else:
            user_id_count = updated_mapping(real_name, "p")
        if user_id_count not in weight_network:
            weight_network[user_id_count]={}
        for each_comment in each_post['comments']:
            comment_id = each_comment['id']
            real_name = commenter_ids[comment_id]
            if real_name == '[deleted]':
                comment_id_count = updated_mapping(comment_id,"c")
            else:
                comment_id_count = updated_mapping(real_name,"c")
            if comment_id_count not in weight_network[user_id_count]:
                weight_network[user_id_count][comment_id_count] = 1
            else:
                weight_network[user_id_count][comment_id_count] +=1


def return_mapping(raw_id,t):
    if t=="p":
        id_key = poster_ids[raw_id]
    else:
        id_key = commenter_ids[raw_id]
    if id_key=="[deleted]":
        id_key=raw_id
    return user_count_mapping[id_key]

graph_line=[]
for each_node in weight_network:
    line = ""
    line = str(each_node) +"\t\t"
    flag = False
    for each_comment in weight_network[each_node]:
        flag = True
        line += str(each_node)+":"+str(each_comment)+":"+str(weight_network[each_node][each_comment])+"\t"
    if flag==False:
        line+=None+"\t"
    line +="\n"
    graph_line.append(line)

with open("global_graph.txt","w") as f:
    for each_line in graph_line:
            f.write(each_line)

cascade_line = []
cas_id = 0
print("________CASCADE____")
for i in range(n):
    print(i)
    sys.stdout.flush()
    each_reddit = json.loads(data[i])
    key = list(each_reddit.keys())[0]
    each_reddit = each_reddit[key]
    for each_post in each_reddit:
        count_delta_1=0
        count_delta_10=0
        count_delta_30=0
        count_1_hr=0
        d1 = datetime.fromtimestamp(each_post['created_utc'])
        if len(each_post['comments']) < 10:
            continue
        cas_line = ""
        user_id_count = return_mapping(each_post['id'],"p")
        cas_line = str(cas_id)+"\t"+str(user_id_count)+"\t2009\t"
        comment_str= ""
        for each_comment in each_post['comments']:
            comment_id_count = return_mapping(each_comment['id'],"c")
            d2 = datetime.fromtimestamp(each_comment['created_utc'])
            if d2>d1+timedelta(days=30):
                break
            if d2<d1+timedelta(hours=1):
                count_1_hr+=1
                comment_str+=str(user_id_count)+":"+str(comment_id_count)+":"+str(weight_network[user_id_count][comment_id_count])+" "
            else:
                if d2<d1+timedelta(days=1):
                    count_delta_1+=1
                    count_delta_10+=1
                    count_delta_30+=1
                elif d2<d1+timedelta(days=10):
                    count_delta_10+=1
                    count_delta_30+=1
                elif d2<d1+timedelta(days=30):
                    count_delta_30+=1
        if count_1_hr==0:
            continue
        else:
            cas_line+=str(count_1_hr)+"\t"+comment_str+"\t"+str(count_delta_1)+" "+str(count_delta_10)+" "+str(count_delta_30)+"\n"
            cascade_line.append(cas_line)
            cas_id+=1

print(len(cascade_line))
sys.stdout.flush()
p=int(len(cascade_line)*0.05)

random.shuffle(cascade_line)
random.shuffle(cascade_line)
random.shuffle(cascade_line)

with open("cascade_val.txt","w") as f:
    for each_line in cascade_line[:p]:
            f.write(each_line)

with open("cascade_test.txt","w") as f:
    for each_line in cascade_line[p:3*p]:
            f.write(each_line)

with open("cascade_train.txt","w") as f:
    for each_line in cascade_line[3*p:]:
            f.write(each_line)
print("----END___")
sys.stdout.flush()

