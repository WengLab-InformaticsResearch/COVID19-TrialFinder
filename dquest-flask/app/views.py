from app import app
from flask import render_template, jsonify, request, session
from lib.log import logger
import lib.oformat as of
import lib.ctgov as ctgov
import lib.question_info_entropy as qst

# log = logger('dquest-view')

# home page
@app.route('/')
def index():
    # get trial number
    # nnct = ctgov.get_nct_number ('http://clinicaltrials.gov/search?term=&displayxml=True&count=0')
    nnct = ctgov.get_nct_number('http://clinicaltrials.gov/search?term=covid-19&displayxml=True&count=0')
    nnct_us = ctgov.get_nct_number('http://clinicaltrials.gov/search?term=covid-19&cntry=US&displayxml=True&count=0')
    # active_roster = qst.find_active_nct_id_list()
    # nnct_local_kb = len(active_roster)

    # testing without length of active trials
    active_roster = []
    nnct_local_kb = 0

    # store active nct_id list for later usage
    session.clear()
    # session['active_nct_list'] = active_roster
    # session.modified = True

    return render_template('index.html', nnct=of.format_nct_number(nnct), nnct_us=of.format_nct_number(nnct_us),
                           nnct_local_kb=nnct_local_kb)

# filter by the pre questions
@app.route('/_pre_questions')
def pre_questions_search():
    age = request.args.get('age')
    # gender = request.args.get('gender')
    exposure = request.args.get('exposure')
    domain = request.args.get('domain')
    user_picked_time = request.args.get('user_picked_time')
    stat = request.args.get('stat')
    preg = request.args.get('preg')
    pre_quest_answers = [age, exposure, domain, user_picked_time, stat, preg]
    result_ids = qst.filter_nct_ids_by_pre_questions(pre_quest_answers)
    return jsonify(result_ids)


# search for clinical trials
@app.route('/_ctgov_search')
def ctgov_search():
    stxt = request.args.get('stxt')
    npag = request.args.get('npag')
    (n, nct) = ctgov.search(stxt, npag)
    if (stxt is None) or (len(stxt) == 0):
        stxt = 'all'
    if npag == '1':
        log.info('%s -- ct.gov-search: q("%s") - res(%s trials)' % (request.remote_addr, stxt, n))
    return jsonify(n=n, nct=nct, q=stxt, npag=npag)


# advanced search for clinical trials.
@app.route('/_adv_search')
def ctgov_advanced_search():
    (n, nct) = ctgov.advanced_search(request.args)
    # term = request.args.get('term')
    npag = request.args.get('npag')
    fq = of.format_query2print(request.args)
    if npag == '1':
        log.info('%s -- ct.gov-advanced-search: q(%s) - res(%s trials)' % (request.remote_addr, fq, n))
    print(fq)
    return jsonify(n=n, nct=nct, q=fq, npag=npag)


# start question and init working_nct_id_list and question_answer_list.
@app.route('/_start_question')
def start_question():
    # get parameters
    stxt = request.args.get
    ('stxt')
    # save the query in session
    # session['query'] = stxt
    # get trials and tags
    rnct = ctgov.get_initial_nct(stxt)
    working_nct_id_list = qst.init_working_nct_id_list(rnct)
    question_answer_list = []
    question_answer_list = qst.find_new_question(question_answer_list, working_nct_id_list)
    log.info('%s -- first question' % (request.remote_addr))
    return jsonify(question_answer_list=question_answer_list, working_nct_id_list=working_nct_id_list)


# small function to make sure input zip code is valid and found in list
@app.route('/_check_homepage_parameters')
def check_homepage_parameters():
    # get parameters
    locn = request.args.get('locn')
    miles = request.args.get('miles')
    trial_type = request.args.get('trial_type')
    active_restriction = request.args.get('active_restriction')
    keyword_search = request.args.get('keyword')

    if keyword_search is None:
        keyword_search = ''

    print('keyword in views: ' + keyword_search)

    # trying zipcode search
    try:
        # fengyang: after change the output of get_nct_list_from_zip function
        nearby_nct = ctgov.get_nct_list_from_zip(locn, miles)[0]
        print('length of nearby nct: ' + str(len(nearby_nct)))
        # session['nearby_nct_list'] = nearby_nct
        valid_zip = True
        print('assigned new variable')
        # fengyang: return nearby zip list
        nearby_zip_list = ctgov.get_nct_list_from_zip(locn, miles)[1]

    except:
        nearby_nct = []
        valid_zip = False

        return jsonify(valid_zip=valid_zip, nearby_length=0, keyword_length=0, type_length=0,
                       working_nct_length=0)

    print('passing try piece')

    # testing keyword search
    klist = ctgov.get_nct_list_from_keywords(keyword_search)
    # session['keyword_trial_list'] = klist

    # testing additional trial information pull using active restriction and trial type
    # tlist = qst.find_active_nct_id_list(trial_type, active_restriction)
    tlist = qst.find_active_nct_id_list(active_restriction, trial_type)
    # session['trial_type_list'] = tlist

    # building working nct_id list from search parameters
    zanct = []
    nearby_nct_list = [x.split(';')[0] for x in nearby_nct]
    keyword_nct_list = [x.split(';')[0] for x in klist]
    for item in tlist:
        split_item = item.split(';')
        if split_item[1] in nearby_nct_list and split_item[1] in keyword_nct_list:
            zanct.append([split_item[0], split_item[1], int(split_item[2])])

    working_nct_id_list = qst.init_working_nct_id_list(zanct)
    session['working_nct_list_pre_process'] = zanct
    session.modified = True
    # session['working_nct_id_list'] = working_nct_id_list

    print(valid_zip)
    print(len(klist))
    print(len(tlist))
    print(len(zanct))

    # fengyang: add nearby_zip_list at return output
    return jsonify(valid_zip=valid_zip, nearby_length=len(nearby_nct), keyword_length=len(klist), type_length=len(tlist),
                   working_nct_length=len(zanct), nearby_zip_list = nearby_zip_list)

# function to query aact_trial_info table and return data for trial information modal
@app.route('/_retrieve_modal_data')
def retrieve_modal_data():
    nct_id = request.args.get('nctid')

    # in case of error, returns string 'Error' in location 1
    trial_data = ctgov.query_trial_info_for_modal(nct_id)

    # simple post-processing on facility and facility contact information
    fc = []
    print(trial_data[15])
    if trial_data[15] is not None:              # what would be returned if no columns had values
        for item in trial_data[15].split('|'):
            fc.append(item.split('; '))

    # splitting central contact information
    cc = []
    print(trial_data[17])
    if trial_data[17] is not None:
        cc = (trial_data[17].split('; '))

    # fengyang: add location latlng info
    trial_loc_latlng_list = ctgov.get_nct_location_latlng(nct_id)
    # if nct_id is not in the pickle file, will return an empty list []

    return jsonify(official_title=trial_data[0], study_type=trial_data[1], primary_purpose=trial_data[2],
                   study_description=trial_data[3], gender=trial_data[4], minimum_age=trial_data[5],
                   maximum_age=trial_data[6], healthy_volunteers=trial_data[7], phase=trial_data[8],
                   allocation=trial_data[9], intervention_model=trial_data[10], observation_model=trial_data[11],
                   masking=trial_data[12], outcome_measure=trial_data[13], outcome_description=trial_data[14],
                   facilities_and_contacts=fc, intervention_names=trial_data[16], central_contact=cc,
                   # fengyang
                   location_latlng=trial_loc_latlng_list)

# start question and init working_nct_id_list and question_answer_list.
@app.route('/_hao_start_question')
def get_to_pre_questions():
    # # get parameters
    # locn = request.args.get('locn')
    # miles = request.args.get('miles')
    # trial_type = request.args.get('trial_type')
    # active_restriction = request.args.get('active_restriction')
    # keyword_search = request.args.get('keyword_search')

    # retrieve trials within set mile range of given zip code
    # znct = ctgov.get_nct_list_from_zip(locn, miles)
    # znct = session.get('nearby_nct_list')
    # print('rnct: ' + str(znct))

    # retrieve trials based on keyword search provided by user
    # knct = ctgov.get_nct_list_from_keywords(keyword_search)
    # knct = session.get('keyword_trial_list')
    # print('knct: ' + str(knct))


    # retrieve trials which are of a given trial type and status (based on active restriction checkbox)
    # anct = qst.find_active_nct_id_list(trial_type, active_restriction)
    # anct = session.get('trial_type_list')
    # print('anct: ' + str(anct))

    # compare nearby nct list with active list
    # zanct = []
    # nearby_nct_list = [x.split(';')[0] for x in znct]
    # keyword_nct_list = [x.split(';')[0] for x in knct]
    # for item in anct:
    #     split_item = item.split(';')
    #     if split_item[1] in nearby_nct_list and split_item[1] in keyword_nct_list:
    #         zanct.append([split_item[0], split_item[1], int(split_item[2])])
    #
    # working_nct_id_list = qst.init_working_nct_id_list(zanct)
    # session['nearby_active_nct_list'] = zanct
    working_nct_list_pre_process = session.get('working_nct_list_pre_process')
    working_nct_id_list = qst.init_working_nct_id_list(working_nct_list_pre_process)

    unique_nct_ct = qst.find_size_of_active_trials(working_nct_id_list)

    return jsonify(working_nct_id_list=working_nct_id_list, unique_nct_ct=unique_nct_ct)


# start question and init working_nct_id_list and question_answer_list.
@app.route('/_pts_start_question')
def start_question_detail():
    age = request.args.get('age')
    # gender = request.args.get('gender')
    exposure = request.args.get('exposure')
    domain = request.args.get('domain')
    user_picked_time = request.args.get('user_picked_time')
    stat = request.args.get('stat')
    preg = request.args.get('preg')
    miles = request.args.get('miles')

    pre_quest_answers = [age, exposure, domain, user_picked_time, stat, preg]

    # get trials and tags
    rnct = session.get('working_nct_list_pre_process')
    working_nct_id_list = qst.init_working_nct_id_list(rnct, pre_quest_answers)
    question_answer_list = []

    if len(working_nct_id_list) > 0:
        question_answer_list = qst.find_new_question(question_answer_list, working_nct_id_list)
        # log.info('%s -- first question' % (request.remote_addr))

    return jsonify(question_answer_list=question_answer_list, working_nct_id_list=working_nct_id_list)


# start question by adv seasrch and init working_nct_id_list and question_answer_list.
@app.route('/_advs_start_question')
def advs_start_question():
    qlabel = request.args.get('qlabel')
    # save the query in session
    # session.clear()
    # session['query'] = qlabel
    # session.modified = True
    # get trials
    print('request.args')
    print(request.args)
    url = ctgov.form_advanced_search_url(request.args)
    rnct = ctgov.get_initial_nct_from_url(url)
    working_nct_id_list = qst.init_working_nct_id_list(rnct)
    question_answer_list = []
    if len(working_nct_id_list) > 0:
        question_answer_list = qst.find_new_question(question_answer_list, working_nct_id_list)
        log.info('%s -- first question' % (request.remote_addr))
    return jsonify(question_answer_list=question_answer_list, working_nct_id_list=working_nct_id_list)


# load nct details.
@app.route('/_find_nct_by_page', methods=['POST'])
def find_nct_by_page():
    requestion_dict = request.get_json()
    working_nct_id_list = requestion_dict['working_nct_id_list']
    npag = requestion_dict['npag']
    nct_details_for_this_page = qst.find_nct_details(working_nct_id_list, npag)
    print('find_nct_by_page: ' + str(working_nct_id_list))
    size_of_active_trials = qst.find_size_of_active_trials(working_nct_id_list)
    print('size_of_active_trials: ' + str(size_of_active_trials))
    # fengyang
    nct_loc_for_this_page = qst.find_all_locations_on_current_page(working_nct_id_list, npag)[0]
    nct_id_rep_for_this_page = qst.find_all_locations_on_current_page(working_nct_id_list, npag)[1]
    # print('len_of_all_marker: '+ str(len(nct_loc_for_this_page)))
    # nct_log_nearby
    input_latlng = requestion_dict['input_zipcode_latlng']
    input_miles = requestion_dict['input_miles']
    nct_loc_nearby_for_this_page = qst.find_nct_loc_within_range(nct_loc_for_this_page, nct_id_rep_for_this_page,input_latlng, input_miles)[0]
    nct_id_nearby_for_this_page = qst.find_nct_loc_within_range(nct_loc_for_this_page, nct_id_rep_for_this_page,input_latlng, input_miles)[1]
    nct_title_nearby_for_this_page = \
    qst.find_nct_loc_within_range(nct_loc_for_this_page, nct_id_rep_for_this_page, input_latlng, input_miles)[2]

    return jsonify(working_nct_id_list=working_nct_id_list, npag=npag,
                   nct_details_for_this_page=nct_details_for_this_page, size_of_active_trials=size_of_active_trials,
                   # fengyang
                   nct_loc_for_this_page = nct_loc_for_this_page,
                   nct_loc_nearby_for_this_page = nct_loc_nearby_for_this_page,
                   nct_id_nearby_for_this_page = nct_id_nearby_for_this_page,
                   nct_title_nearby_for_this_page=nct_title_nearby_for_this_page,
                   )


# confirm the question.
@app.route('/_confirm', methods=['POST'])
def confirm():
    requestion_dict = request.get_json()
    question_answer_list = requestion_dict['question_answer_list']
    working_nct_id_list = requestion_dict['working_nct_id_list']
    domain = requestion_dict['domain']
    working_nct_id_list = qst.update_working_nct_id_list(question_answer_list, working_nct_id_list)
    print('working nctid list: ' + str(working_nct_id_list))
    print('question answer list: ' + str(question_answer_list))
    question_answer_list = qst.find_new_question(question_answer_list, working_nct_id_list, domain)
    print('qlist 2: ' + str(question_answer_list))
    return jsonify(question_answer_list=question_answer_list, working_nct_id_list=working_nct_id_list)


# close the session.
@app.route('/_clean')
def clean():
    q = session['query']
    session.clear()
    session.modified = True
    log.info('%s -- tag cloud closed' % request.remote_addr)
    return jsonify(n=0, q=q)
