import os

import pytz as pytz
from flask import Flask, render_template, request, jsonify, flash, redirect, json, Response
import mysql.connector
from datetime import datetime

secret_key = os.urandom(24)
vpp = Flask(__name__)

vpp.secret_key = secret_key

virtual = mysql.connector.connect(
    user='Medisim',
    password='K60KSH2DOXQn8BGnM3SA',
    database='PLATFORM',
    host='medisim-testdb.cbmmrisq24o6.us-west-2.rds.amazonaws.com',
    port=3306,
    auth_plugin='mysql_native_password',
    autocommit=True,
)
cursor = virtual.cursor()


# If we want to test in Local
# def user_time():
#     current_time = datetime.now()
#     formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
#     return formatted_time


# Before deployment have to discomment this
def user_time():
    ist = pytz.timezone('Asia/Kolkata')  # IST time zone
    utc_time = datetime.utcnow()
    ist_time = utc_time.astimezone(ist)
    formatted_time = ist_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time


def get_user_ip():
    if 'X-Forwarded-For' in request.headers:
        # Use the first IP in the X-Forwarded-For header
        user_ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    else:
        # Use the default remote_addr
        user_ip = request.remote_addr
    return user_ip


@vpp.route('/')
def index():
    global formatted_timestamp, formated_timestamp
    system_count_sql = "SELECT count(system_name) FROM system_names WHERE lock_status=0"
    cursor.execute(system_count_sql)
    system_count = cursor.fetchall()
    sys_count = [syc[0] for syc in system_count]

    organ_count_sql = "SELECT count(parent_name) FROM parent WHERE lock_status=0"
    cursor.execute(organ_count_sql)
    organ_count = cursor.fetchall()
    org_count = [org[0] for org in organ_count]

    disease_count_sql = "SELECT count(condition_name) FROM condition_names WHERE lock_status=0"
    cursor.execute(disease_count_sql)
    disease_count = cursor.fetchall()
    dis_count = [dc[0] for dc in disease_count]

    symptom_count_sql = "SELECT count(symptoms_name) FROM symptoms WHERE lock_status=0"
    cursor.execute(symptom_count_sql)
    symptom_count = cursor.fetchall()
    symp_count = [symc[0] for symc in symptom_count]

    questions_count_sql = "SELECT count(questions) FROM questions WHERE lock_status=0"
    cursor.execute(questions_count_sql)
    question_count = cursor.fetchall()
    ques_count = [qc[0] for qc in question_count]

    case_count_sql = "SELECT count(case_name) FROM cases WHERE lock_status=0"
    cursor.execute(case_count_sql)
    case_count = cursor.fetchall()
    cas_count = [cc[0] for cc in case_count]

    recent_case_sql = "SELECT case_name, timestamp FROM cases WHERE lock_status=0 ORDER BY timestamp DESC LIMIT 5"
    cursor.execute(recent_case_sql)
    recent_cases = cursor.fetchall()
    formated_timestamp = None

    for case_name, timestamp in recent_cases:
        formatted_timestamp = timestamp.strftime('%d %b, %Y')
        formated_timestamp = formatted_timestamp
    return render_template("dashboard.html", system_count=sys_count, org_count=org_count, dis_count=dis_count,
                           symp_count=symp_count, ques_count=ques_count, cas_count=cas_count, recent_cases=recent_cases,
                           formatted_timestamp=formated_timestamp)


@vpp.route('/vpp_system')
def vpp_system():
    clct_system_sql = "SELECT * FROM system_names ORDER BY system_name"
    cursor.execute(clct_system_sql)
    clct_systems = cursor.fetchall()
    return render_template("system.html", clct_systems=clct_systems)


@vpp.route('/vpp_system/creation', methods=['POST'])
def system_creation():
    global sys_id
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='system' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        sys_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='system' ", (new_current_id_str,))
    if request.method == 'POST':
        s_name = request.form['s_name']
        added_by = 'Sam'
        time = user_time()
        ip = get_user_ip()

        system_insert_sql = "INSERT INTO system_names (system_id, system_name, lock_status, added_by, timestamp, " \
                            "ip_address) VALUES (%s, %s, %s, %s, %s, %s) "
        system_add_val = (sys_id, s_name, 0, added_by, time, ip)
        cursor.execute(system_insert_sql, system_add_val)
        virtual.commit()
        flash("System Added Successfully..!")
        return redirect('/vpp_system')


@vpp.route('/vpp_system/organ')
def parent():
    clct_parent_name_sql = "SELECT * from parent"
    cursor.execute(clct_parent_name_sql)
    clct_parent = cursor.fetchall()

    system_category_sql = "SELECT system_name FROM system_names WHERE lock_status=0"
    cursor.execute(system_category_sql)
    system_names = cursor.fetchall()
    system_categories = [syscat[0] for syscat in system_names]
    return render_template("parent.html", clct_parent=clct_parent, system_categories=system_categories)


@vpp.route('/vpp_parent/creation', methods=['POST'])
def parent_creation():
    global parent_id
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='parent' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        parent_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='parent' ", (new_current_id_str,))
    if request.method == 'POST':
        sys_cat = request.form['sys_cat']
        p_name = request.form['p_name']
        added_by = 'Sam'
        time = user_time()
        ip = get_user_ip()

        parent_insert_sql = "INSERT INTO parent (parent_id, parent_name, system_category, lock_status, added_by, " \
                            "timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s) "
        parent_insert_val = (parent_id, p_name, sys_cat, 0, added_by, time, ip)
        cursor.execute(parent_insert_sql, parent_insert_val)
        virtual.commit()
        flash(f"Organ Name added in the {sys_cat} category successfully..!")
        return redirect('/vpp_system/parent')


@vpp.route('/vpp_system/disease')
def condition():
    clct_condn_sql = "select * FROM condition_names"
    cursor.execute(clct_condn_sql)
    clctd_condns = cursor.fetchall()

    clct_symp_sql = "select * FROM  symptoms WHERE lock_status=0"
    cursor.execute(clct_symp_sql)
    clctd_symps = cursor.fetchall()
    sympts = [sym[2] for sym in clctd_symps]

    prtn_cltn_sql = "SELECT parent_name FROM parent WHERE lock_status =0 "
    cursor.execute(prtn_cltn_sql)
    cltd_parents = cursor.fetchall()
    parents_name = [prnt[0] for prnt in cltd_parents]

    system_category_sql = "SELECT system_name FROM system_names WHERE lock_status=0"
    cursor.execute(system_category_sql)
    system_names = cursor.fetchall()
    system_categories = [syscat[0] for syscat in system_names]

    clct_condn_for_parent_sql = "select condition_name FROM condition_names WHERE lock_status=0"
    cursor.execute(clct_condn_for_parent_sql)
    clctd_condns_for_parent = cursor.fetchall()
    clctd_prnt_condn = [pc[0] for pc in clctd_condns_for_parent]
    return render_template("condition.html", clctd_condns=clctd_condns, parents_name=parents_name,
                           system_categories=system_categories, clctd_prnt_condn=clctd_prnt_condn, clctd_symps=sympts)


@vpp.route('/vpp_condition/creation', methods=['POST'])
def condn_creation():
    global condition_id
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='condition' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        condition_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='condition' ",
                       (new_current_id_str,))
    if request.method == 'POST':
        c_name = request.form['c_name']
        prnt_cat = request.form['prnt_cat']
        sys_cat = request.form['sys_cat']
        condn_prnt = request.form['condn_prnt']
        added_by = 'Sam'
        symptoms = request.form.getlist('symptoms[]')
        symptoms_str = ', '.join(symptoms)
        time = user_time()
        ip = get_user_ip()

        condition_insert_sql = "INSERT INTO condition_names (condition_id, condition_name, condition_parent, symptoms," \
                               "organ_name, category_name, lock_status, added_by, timestamp, ip_address) VALUES (%s, " \
                               "%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        condition_insert_val = (
            condition_id, c_name, condn_prnt, symptoms_str, prnt_cat, sys_cat, 0, added_by, time, ip)
        cursor.execute(condition_insert_sql, condition_insert_val)
        virtual.commit()
        flash("Disease added successfully..!")
        return redirect('/vpp_system/disease')


@vpp.route('/get_condition_id', methods=['POST'])
def get_condition_id():
    condition_id = request.form['condition_id']
    cursor.execute("SELECT * FROM condition_names WHERE condition_id = %s", (condition_id,))
    condtns_for_update = cursor.fetchall()
    clct_condn_for_parent_sql = "select condition_name FROM condition_names WHERE lock_status=0"
    cursor.execute(clct_condn_for_parent_sql)
    clctd_condns_for_parent = cursor.fetchall()
    clctd_prnt_condn = [pc[0] for pc in clctd_condns_for_parent]
    return jsonify({'condtns_for_update': condtns_for_update, 'clctd_prnt_condn': clctd_prnt_condn})


@vpp.route('/vpp_condition/updation', methods=['POST'])
def condition_updation():
    if request.method == 'POST':
        update_condition_id = request.form['update_condition_id']
        update_condition_name = request.form['update_condition_name']
        update_condn_parent = request.form['update_condn_parent']
        update_organ_name = request.form['update_organ_name']
        update_concat_name = request.form['update_concat_name']

        condn_update_sql = "UPDATE condition_names SET condition_parent = %s WHERE condition_id = %s"
        condn_update_val = (update_condn_parent, update_condition_id)
        cursor.execute(condn_update_sql, condn_update_val)
        virtual.commit()
        flash(f"Updated Successfully for the condition {update_condition_name}")
        return redirect('/vpp_system/condition')


@vpp.route('/vpp_system/symptoms')
def symp():
    clct_symp_sql = "select * FROM symptoms"
    cursor.execute(clct_symp_sql)
    clctd_symps = cursor.fetchall()

    clct_condn_sql = "select * FROM condition_names WHERE lock_status =0 "
    cursor.execute(clct_condn_sql)
    clctd_condn = cursor.fetchall()
    clctd_condns = [dis[2] for dis in clctd_condn]

    clct_fields_sql = "SELECT meta_name FROM meta_data WHERE lock_status=0"
    cursor.execute(clct_fields_sql)
    clct_fields = cursor.fetchall()
    suggestions = [su[0] for su in clct_fields]

    prtn_cltn_sql = "SELECT parent_name FROM parent WHERE lock_status =0 "
    cursor.execute(prtn_cltn_sql)
    cltd_parents = cursor.fetchall()
    parents_name = [prnt[0] for prnt in cltd_parents]
    return render_template("symp.html", parents_name=parents_name, clctd_symps=clctd_symps, clctd_condns=clctd_condns,
                           suggestions=suggestions)


@vpp.route('/get_conditions', methods=['POST'])
def get_conditions():
    selectedParent = request.form['selectedParent']
    print(selectedParent)
    cursor.execute("SELECT condition_name FROM condition_names WHERE organ_name = %s", (selectedParent,))
    condtns = cursor.fetchall()
    conditionss = [condn[0] for condn in condtns]
    print(conditionss)
    return jsonify({'conditionss': conditionss})


@vpp.route('/vpp_symptom/creation', methods=['POST'])
def symp_creation():
    global symptom_id, prefix, new_current_id, new_current_id_str
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='symptom' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        symptom_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='symptom' ",
                       (new_current_id_str,))

    if request.method == 'POST':
        symptoms = request.form['symp_name']
        added_by = 'Sam'
        time = user_time()
        ip = get_user_ip()

        field_values = request.form.getlist('field')  # Assuming 'form' is the name attribute of the 'form' input
        default_values = request.form.getlist('value')  # Assuming 'value' is the name attribute of the 'value' input

        print("Symptom Name:", symptoms)
        print("Field Values:", field_values)
        print("Default Values:", default_values)

        symp_insert_sql = "INSERT INTO symptoms (symptoms_id, symptoms_name, lock_status, " \
                          "added_by, timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, %s) "
        symp_insert_val = (symptom_id, symptoms, 0, added_by, time, ip)
        cursor.execute(symp_insert_sql, symp_insert_val)
        virtual.commit()

        for field, value in zip(field_values, default_values):
            meta_insert_sql = "INSERT INTO meta_data (symptoms, meta_name, meta_default_value, lock_status, " \
                              "meta_added_by, timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s) "
            meta_insert_val = (symptoms, field, value, 0, added_by, time, ip)
            cursor.execute(meta_insert_sql, meta_insert_val)
            virtual.commit()
        flash(f"Symptom added Successfully..!")
        return redirect('/vpp_system/symptoms')


@vpp.route('/vpp_system/analyse_tree')
def ana_tree():
    clct_condn_sql = "select * FROM condition_names"
    cursor.execute(clct_condn_sql)
    clctd_condns = cursor.fetchall()
    condtns = [cdn[2] for cdn in clctd_condns]

    return render_template("analyse_tree.html", condtns=condtns)


@vpp.route('/get_symptoms_details', methods=['POST'])
def get_symp_det():
    selectedCondition = request.form['selectedCondition']
    print(selectedCondition)
    symp_get_sql_for_condition = "SELECT symptoms FROM condition_names WHERE condition_name like %s"
    # cursor.execute(symp_get_sql_for_condition, (selectedCondition,))
    cursor.execute(symp_get_sql_for_condition, (f'%{selectedCondition}%',))
    symp_name = cursor.fetchall()
    print(symp_name)
    return jsonify({'symp_name': symp_name})


@vpp.route('/get_meta_details', methods=['POST'])
def get_meta_det():
    selected_symptom = request.form['selected_symptom']
    print(selected_symptom)
    meta_details_sql = "SELECT meta_name, meta_default_value FROM meta_data WHERE symptoms=%s"
    cursor.execute(meta_details_sql, (selected_symptom,))
    # cursor.execute(symp_get_sql_for_condition, (f'%{selectedCondition}%',))
    meta_name_details = cursor.fetchall()
    print(meta_name_details)
    return jsonify({'meta': meta_name_details})


@vpp.route('/vpp_condition/qa', methods=['POST'])
def vpp_condn_qa():
    if request.method == 'POST':
        selected_condition = request.form.get('condn')
        questions = request.form.getlist('symptoms')
        answers = request.form.getlist('ans')  # Get a list of selected answers
        details = request.form.getlist('details')
        user_name = 'Sam'
        time = user_time()
        ip = get_user_ip()
        print(selected_condition)
        print(questions)
        print(answers)
        print(details)
        for q, a, d in zip(questions, answers, details):
            tree_details_insert_sql = "INSERT INTO symptoms_trees_qa (condition_name, questions, answers, details, " \
                                      "lock_status, created_by, timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, " \
                                      "%s, %s, %s) "
            tree_details_val = (selected_condition, q, a, d, 0, user_name, time, ip)
            cursor.execute(tree_details_insert_sql, tree_details_val)
            virtual.commit()
    return "Tree Created Successfully..!"


@vpp.route('/json_download')
def json_download():
    # json_download_sql = "select a.system_category, b.organ_name, c.condition_name, b.condition_parent, c.symptoms_name," \
    #                     "d.questions from PLATFORM.parent a, PLATFORM.condition_names b, PLATFORM.symptoms c, " \
    #                     "PLATFORM.questions d WHERE a.parent_name = b.organ_name and " \
    #                     "b.condition_name=c.condition_name "
    global formatted_symp_data, formatted_org_data
    json_download_sql = "SELECT symptoms, questions FROM PLATFORM.questions WHERE lock_status=0"
    cursor.execute(json_download_sql)
    json_results = cursor.fetchall()

    json_sym_download_sql = "SELECT distinct a.symptoms_name as Symptom_Name, a.condition_name as Disease_Name FROM " \
                            "PLATFORM.symptoms a, PLATFORM.condition_names b where a.lock_status=0 and " \
                            "a.condition_name like '%' || b.condition_name || '%' "
    cursor.execute(json_sym_download_sql)
    json_symp = cursor.fetchall()
    formatted_data = []

    json_org_sql = "SELECT a.condition_name, a.organ_name, b.system_category FROM PLATFORM.condition_names a, PLATFORM.parent b WHERE " \
                   "a.organ_name=b.parent_name "
    cursor.execute(json_org_sql)
    json_org = cursor.fetchall()
    # for row in json_results:
    #     formatted_data.append({
    #         # "System Category": row[0],
    #         # "Related Organ": row[1],
    #         # "Disease": row[2],
    #         # "Disease Parent": row[3],
    #         # "Symptoms": row[4],
    #         # "Questions": row[5],
    #         "Questions": row[1],
    #         "Symptoms" : row[0]
    #     })
    for row in json_results:
        symptoms_list = row[0].split(', ')  # Assuming symptoms are stored as a comma-separated string
        question_entry = {
            # "System Category": row[0],
            # "Related Organ": row[1],
            # "Disease": row[2],
            # "Disease Parent": row[3],
            # "Questions": row[5],
            "Questions": row[1],
            "Symptoms": symptoms_list
        }
        formatted_data.append(question_entry)

        formatted_symp_data = []
    for rows in json_symp:
        disease_list = rows[1].split(', ')  # Assuming symptoms are stored as a comma-separated string
        symp_entry = {
            # "System Category": row[0],
            # "Related Organ": row[1],
            # "Disease": row[2],
            # "Disease Parent": row[3],
            # "Questions": row[5],
            "Symptoms": rows[0],
            "Disease": disease_list
        }
        formatted_symp_data.append(symp_entry)

        formatted_org_data = []
    for rowss in json_org:
        organ_list = rowss[1].split(', ')  # Assuming symptoms are stored as a comma-separated string
        org_entry = {
            # "System Category": row[0],
            # "Related Organ": row[1],
            # "Disease": row[2],
            # "Disease Parent": row[3],
            # "Questions": row[5],
            "Disease": rowss[0],
            "Affected Organ": organ_list,
            "System": rowss[2]
        }
        formatted_org_data.append(org_entry)

    # Create a dictionary with headings and data
    json_data = {"data": formatted_data + formatted_symp_data + formatted_org_data}

    # Convert the data to JSON format
    json_data_str = json.dumps(json_data, indent=2, sort_keys=False)

    # Save the JSON data to a file
    with open('Virtual_Platform.json', 'w') as json_file:
        json_file.write(json_data_str)

    return Response(json_data_str, mimetype='application/json',
                    headers={'Content-Disposition': 'attachment;filename=Virtual_Platforms.json'})
    # return json_data_str


@vpp.route('/vpp_system/questions')
def ques():
    clct_ques_sql = "SELECT * FROM questions"
    cursor.execute(clct_ques_sql)
    cltd_ques = cursor.fetchall()

    clct_symp_sql = "select symptoms_name FROM symptoms WHERE lock_status=0"
    cursor.execute(clct_symp_sql)
    clctd_symp = cursor.fetchall()
    clctd_symps = [cs[0] for cs in clctd_symp]

    return render_template("questions.html", cltd_ques=cltd_ques, clctd_symps=clctd_symps)


@vpp.route('/vpp_question/creation', methods=['POST'])
def que_creation():
    global question_id, prefix, new_current_id, new_current_id_str
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='question' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        question_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='question' ",
                       (new_current_id_str,))

    if request.method == 'POST':
        que = request.form['que']
        syms = request.form.getlist('symptoms[]')  # Use a more descriptive variable name
        symptoms_str = ', '.join(syms)
        added_by = 'Sam'
        time = user_time()
        ip = get_user_ip()

        symp_insert_sql = "INSERT INTO questions (que_id, questions, symptoms, lock_status, added_by, timestamp, " \
                          "ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s) "
        symp_insert_val = (question_id, que, symptoms_str, 0, added_by, time, ip)
        cursor.execute(symp_insert_sql, symp_insert_val)
        virtual.commit()

        flash("Question added Successfully..!")
        return redirect('/vpp_system/questions')


@vpp.route('/vpp_system/case')
def case():
    clct_symp_sql = "select symptoms_name FROM symptoms WHERE lock_status=0"
    cursor.execute(clct_symp_sql)
    clctd_symp = cursor.fetchall()
    clctd_symps = [cs[0] for cs in clctd_symp]

    clct_condn_sql = "select * FROM condition_names WHERE lock_status =0 "
    cursor.execute(clct_condn_sql)
    clctd_condn = cursor.fetchall()
    clctd_condns = [dis[2] for dis in clctd_condn]

    clct_case_sql = "SELECT * FROM cases"
    cursor.execute(clct_case_sql)
    clct_case = cursor.fetchall()

    return render_template("case.html", clctd_symps=clctd_symps, clctd_condns=clctd_condns, clct_case=clct_case)


@vpp.route('/vpp_case/creation', methods=['POST'])
def case_creation():
    global case_id, prefix, new_current_id, new_current_id_str
    cursor.execute("SELECT prefix, start_id, current_id FROM id_generation where category_name='case' ")
    result = cursor.fetchone()
    if result:
        prefix, start_number, current_id = result
        case_id = f"{prefix}{current_id}"
        new_current_id = int(current_id) + 1
        new_current_id_str = f"{new_current_id:03d}"
        cursor.execute("UPDATE id_generation SET current_id = %s where category_name='case' ",
                       (new_current_id_str,))

    if request.method == 'POST':
        caseName = request.form['caseName']
        age = request.form['age']
        gender = request.form['gender']
        disease = request.form['disease']
        syms = request.form.getlist('symp_name[]')  # Use a more descriptive variable name
        symptoms_str = ', '.join(syms)
        print("Symptoms are:" + str(symptoms_str))
        intro = request.form['into']
        # diagnosis = request.form['diagnosis']
        que1 = request.form['que1']
        ans = request.form.getlist('ans')
        score = request.form.getlist('score')
        keyss = request.form.getlist('keys')
        keys_and_values_str = keyss[0]
        keys = keys_and_values_str.split(',')
        valuesss = request.form.getlist('field_values')
        field_and_values_str = valuesss[0]
        values = field_and_values_str.split(',')
        created_by = 'Sam'
        time = user_time()
        ip = get_user_ip()

        case_insert_sql = "INSERT INTO cases (case_id, case_name, age, gender, case_disease, case_symptoms, " \
                          "introduction, diagnosis, lock_status, created_by, timestamp, ip_address) VALUES (%s, %s, " \
                          "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        case_insert_val = (case_id, caseName, age, gender, disease, symptoms_str, intro, que1, 0, created_by, time, ip)
        cursor.execute(case_insert_sql, case_insert_val)
        for ans, score in zip(ans, score):
            case_dia_ques_sql = "INSERT INTO case_diagnosis (case_id, question, answer, score, lock_status, " \
                                "created_by, timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            case_dia_ques_val = (case_id, que1, ans, score, 0, created_by, time, ip)
            cursor.execute(case_dia_ques_sql, case_dia_ques_val)
        for meta_field, meta_value in zip(keys, values):
            case_meta_insert_sql = "INSERT INTO case_meta (case_id, case_symptom_field, case_symptom_value, " \
                                   "lock_status,created_by, timestamp, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s) "
            case_meta_insert_val = (case_id, meta_field, meta_value, 0, created_by, time, ip)
            cursor.execute(case_meta_insert_sql, case_meta_insert_val)
        virtual.commit()
        flash(f"Case created successfully with case id {case_id}")
        return redirect('/vpp_system/case')


@vpp.route('/get_case_id', methods=['POST'])
def get_case_id():
    case_id = request.form['case_id']
    print(case_id)
    cursor.execute("SELECT * FROM case_diagnosis WHERE case_id = %s", (case_id,))
    case_que_details = cursor.fetchall()
    print(case_que_details)
    return jsonify({'case_que_details': case_que_details})


if __name__ == '__main__':
    vpp.run(debug=True)
