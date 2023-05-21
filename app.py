from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

iimdf = pd.read_csv('all_courses.csv')


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        input_string = request.form['credits']
        final = org(input_string)
        return render_template('result.html', data=final)
    return render_template("index.html")


def org(input_str):

    lines = input_str.split('\n')
    course_id = []
    department = []
    course_name = []
    classes = []
    credits = []
    scores = []
    teachers = []

    for i, line in enumerate(lines):
        line = line.replace(' ', '')
        de = line.rstrip().split('\t')
        # for d in de:
        #     print(d)
        course_id.append(de[2])
        if de[3] == '資管碩':
            department.append(1)
        else:
            department.append(0)
        course_name.append(de[4])
        classes.append(de[5])
        credits.append(float(de[6]))
        if de[7] == '':
            scores.append('unfinised')
        elif de[7][0] == 'A' or de[7][0] == 'B':
            scores.append(float(de[6]))
        else:
            scores.append(0)
        teachers.append(de[9])

    student_df = pd.DataFrame({"course_id": course_id,
                               "department": department,
                               "course_name": course_name,
                               "classes": classes,
                               "credits": credits,
                               "scores": scores,
                               "teachers": teachers})

    all_teacher = np.unique(iimdf['任課老師'])
    special_teacher = ['劉敦仁', '古政元',  '李永銘', '林妙聰', '莊詠婷', '蔡銘箴', '陳柏安']
    all_courses = list(np.unique(iimdf['課程名稱']))

    got_credits = 0
    current_credits = 0
    need_credits = 30
    ###
    iim_credits = 0
    other_credits = 0
    need_seminar = 4
    ###
    need_class = 2
    need_teacher = 4
    need_course = 6

    current_class = set()
    current_teacher = set()
    current_iim_course = 0

    # credits

    for i in range(len(student_df)):

        # seminars or 個別
        # print(student_df.course_name[i])
        if student_df.course_name[i] in ['資訊系統論文研討', '企管資訊論文研討']:
            need_seminar -= 1
            continue
        # total credits
        if student_df.scores[i] != 'unfinised':
            got_credits += float(student_df.credits[i])
            need_credits -= float(student_df.credits[i])
        else:
            current_credits += float(student_df.credits[i])

        if student_df.course_name[i] == '個別研究':
            other_credits += 3
            continue

        # 外所
        # and student_df.scores[i]!='unfinised':
        if student_df.department[i] == 0:
            other_credits += float(student_df.credits[i])
            pass

        # 本系
        if student_df.department[i] == 1:
            current_iim_course += 1
            need_course -= 1
            id = all_courses.index(student_df.course_name[i])
            if iimdf['選別'][id] not in current_class:
                current_class.add(iimdf['選別'][id])
                need_class -= 1
            if student_df.teachers[i] not in special_teacher:
                continue
            if student_df.teachers[i] not in current_teacher:
                current_teacher.add(student_df.teachers[i])
                need_teacher -= 1

    need_credits = max(0, need_credits)
    need_seminar = max(0, need_seminar)
    need_class = max(0, need_class)
    need_teacher = max(0, need_teacher)
    need_course = max(0, need_course)

    result = {"need_seminar": need_seminar,
              "got_credits": got_credits,
              "current_credits": current_credits,
              "current_credits": current_credits,
              "need_credits": need_credits,
              "need_class": need_class,
              "need_teacher": need_teacher,
              "need_course": need_course}

    result_json = json.dumps(result)
    return result_json


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
