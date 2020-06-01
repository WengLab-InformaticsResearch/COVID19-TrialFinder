from app import general_pool_criteria,general_pool_aact


def filter_nct_ids_by_pre_questions(answer_list):
    '''
        find working nct id list after filter the answers to pre-questions
        :param answer_list: the list of the answers to pre-questions
        :return: a working nct id list in our annotation list
    '''
    answer_list = [str(x) for x in answer_list]
    age = answer_list[0]
    # gender = answer_list[1]
    exposure = answer_list[1]
    domain = answer_list[2]
    user_picked_time = answer_list[3]
    stat = answer_list[4]
    preg = answer_list[5]

    # query database filter nctids
    conn = general_pool_criteria.connection()
    cur = conn.cursor()

    sql = '''
            select distinct keyc.nct_id, keyc.pt_cohort
            from dbo.key_criteria_v2 as keyc
            left join dbo.aact_trial_info as aact
                on keyc.nct_id = aact.nct_id
            where
                (1= case
                    when %s <> 99999 and ((%s >= aact.minimum_age or aact.minimum_age is null) and 
                                         (%s <= aact.maximum_age or aact.maximum_age is null) ) then 1
                    when %s = 99999 then 1
                        else 0
                end )
            and
                (1= case
                    when '%s' = 'yes' and  keyc.disease_status in ('yes', 'all') then 1
                    when '%s' = 'no' and keyc.disease_status in ('no', 'all') then 1
                    when '%s' = 'cleared' and keyc.disease_status in ('cleared', 'all') then 1
                    when '%s' = 'idk' and keyc.disease_status in ('yes','no','cleared', 'all') then 1
                        else 0
                end)
            and
                (1= case
                    when '%s' = 'yes' and (keyc.exposure_status = 1 or keyc.exposure_status is null) then 1
                    when '%s' = 'no' and (keyc.exposure_status = 0 or keyc.exposure_status is null) then 1
                    when '%s' = 'idk' and (keyc.exposure_status in (1, 0) or keyc.exposure_status is null) then 1
                        else 0 
                end) 
            and
                (1= case
                    when '%s' = 'yes' and (keyc.is_hospitalized = 1 or keyc.is_hospitalized is null) then 1
                    when '%s' = 'no' and (keyc.is_hospitalized = 0 or keyc.is_hospitalized is null) then 1
                    when '%s' = 'idk' and (keyc.is_hospitalized in (1, 0) or keyc.is_hospitalized is null) then 1
                        else 0
                end)
            and
                (1= case
                    when '%s' = 'yes' and (keyc.preg_status = 1 or keyc.preg_status is null) then 1
                    when ('%s' = 'no' or '%s' = 'n/a') and (keyc.preg_status = 0 or keyc.preg_status is null) then 1
                    when '%s' = 'idk' and (keyc.preg_status in (1, 0) or keyc.preg_status is null) then 1
                        else 0
                    end)
             and(
                1= case
                    when ('%s' = 'None'  or '%s' = '') then 1
                    when '%s' <> 'None' and
            --             ((CURRENT_DATE  - TO_DATE(s, 'MM/DD/YYYY'))
                        (DATEDIFF(day, CONVERT(VARCHAR, '%s', 101), CONVERT(VARCHAR, getdate(), 101)) 
                        <= keyc.days_to_disease or keyc.days_to_disease is null) then 1
                    else 0
                end)
        ''' % (age, age, age, age, domain, domain, domain, domain, exposure, exposure, exposure, stat, stat,
               stat, preg, preg, preg, preg, user_picked_time, user_picked_time, user_picked_time, user_picked_time)

    print(sql)
    cur.execute(sql)
    nctids = cur.fetchall()
    conn.close()
    cur.close()

    result_ids = []
    if len(nctids) > 0:
        for nctid in nctids:
            result_ids.append([nctid[0], nctid[1]])

    return result_ids


def find_active_nct_id_list(active_restriction, trial_type='all'):
    '''
        find annotated working nct id list which is actively recruiting
        :param: none
        :return: a working nct id list in our annotation list
    '''
    # creating set of trial statuses based on user entry
    if active_restriction == 'true':
        active_restriction = True
    else:
        active_restriction = False
    if active_restriction:
        status_terms = ",".join(str("'" + x + "'") for x in ['Recruiting', 'Enrolling by Invitation', 'Available'])
    else:
        status_terms = 'select distinct status from dbo.aact_trial_info'

    active_trial_list = []
    conn = general_pool_criteria.connection()
    cur = conn.cursor()

    # managing different trial type based on user entry
    if trial_type == 'all':
        sql = '''
            select distinct nct_id_desc, pt_cohort, value
            from dbo.key_criteria_v2
                cross apply string_split(nct_id_desc, '_')
            where [value] in (select nct_id
                            from dbo.aact_trial_info
                            where status in (%s))
            order by nct_id_desc;
        ''' % status_terms
    else:
        type_search_terms = ''
        if trial_type == 'intervention':
            type_search_terms = ",".join(str("'" + x + "'") for x in ['interventional', 'expanded access'])
        elif trial_type == 'observation':
            type_search_terms = ",".join(
                str("'" + x + "'") for x in ['observational', 'observational [patient registry]'])
        sql = '''
            select distinct nct_id_desc, pt_cohort, value
            from dbo.key_criteria_v2
                cross apply string_split(nct_id_desc, '_')
            where [value] in (select nct_id
                            from dbo.aact_trial_info
                            where status in (%s) and 
                            lower(study_type) in (%s))
            order by nct_id_desc;
                ''' % (status_terms, type_search_terms)
    cur.execute(sql)
    nctids = cur.fetchall()
    conn.close()
    cur.close()

    if len(nctids) > 0:
        for nctid in nctids:
            active_trial_list.append(str(nctid[0]) + ';' + str(nctid[2]) + ';' + str(nctid[1]))

    return active_trial_list;


def init_working_nct_id_list(rnct, pre_quest_answers=[]):
    '''
    initialize working nct id list
    :param rnct: returned from ctgov search results [...,'NCT02733523;3431','NCT02075840;3432',...]
    :return: a working nct id list
    '''
    working_nct_id_list = []
    if len(pre_quest_answers) > 0:
        filtered_nct_list = filter_nct_ids_by_pre_questions(pre_quest_answers)

        for record in rnct:
            if [record[1], record[2]] in filtered_nct_list:
                working_nct_id_list.append([record[0], record[1], int(record[2]), 0])
    else:
        working_nct_id_list = [[record[0], record[1], int(record[2]), 0] for record in rnct]
    return working_nct_id_list


# working_nct_id_list = [['NCT02901717', 3431, 0], ['NCT01287182', 3432, 0],['NCT01035944', 3432, 0],['NCT00562068', 3431, 1], ['NCT00742300', 3431, 2]]
# question_answer_list = [{'answer': {}, 'question': {'domain': 'condition', 'entity_text': 'pregnant'}} ]
def find_new_question(question_answer_list, working_nct_id_list, domain='all'):
    '''
    find new question by frequency.
    alternatively, information entropy should be considered sum(plog(p))
    :param question_answer_list: questions already answered or skipped with their corresponding answers
    :param working_nct_id_list: a working nct id list
    :return: a updated question_answer_list by appending a new question

    Example
    working_nct_id_list = [['NCT02901717', 3431, 0], ['NCT01287182', 3432, 0],['NCT01035944', 3432, 0],['NCT00562068', 3431, 1], ['NCT00742300', 3431, 2]]
    question_answer_list = [{'answer': {}, 'question': (3, u'pregnant')}]
    '''
    # working_nct_id_frame = pd.DataFrame(working_nct_id_list,columns=['nct_id', 'ctgov_rank', 'num_of_question'])
    working_nct_id_0 = [record[0] for record in working_nct_id_list if record[3] == 0]

    working_nct_id_0_len = len(working_nct_id_0)
    placeholders1 = ",".join(str("'" + x + "'") for x in working_nct_id_0)
    ########################################################################################################################
    # placeholders1 = ",".join("?" * 2000)
    # working_nct_id_0 = [record[0] for record in working_nct_id_list if record[2] == 0][0:2000]
    # ERROR is raised if the nct list is larger than 2000
    # Use subsampling to solve this issue.
    # Select the first 2000 is better.
    if len(working_nct_id_0) > 2000:
        placeholders1 = ",".join("?" * 2000)
        working_nct_id_0 = working_nct_id_0[0:2000]
    ########################################################################################################################
    domain = domain.lower()
    conn = general_pool_criteria.connection()
    cur = conn.cursor()
    if domain != 'all':
        table_name = 'dbo.all_criteria_v2'
        placeholders2 = str(domain)
        active_question_0 = [qa['question']['entity_text'] for qa in question_answer_list if
                             qa['question']['domain'] == domain]
        print('active question: ' + str(active_question_0))
        placeholders3 = ",".join(str("'" + x + "'") for x in active_question_0)

        if len(active_question_0) == 0:

            sql = '''
                    SELECT TOP(1) sum(PlogP) AS IE, concept_name
                    FROM(
                        select concept_name, include, count, -(count/%s)*LOG((count/%s)) AS PlogP
                        FROM
                            (
                        select CAST(count(distinct nct_id_original) AS [float]) AS count, concept_name, include
                            from %s
                            where nct_id_original in (%s) and concept_name is NOT NULL
                            and lower(domain) = '%s'
                            and to_display = 1
                            group by concept_name, include
                        ) X
                    ) X
                    GROUP BY concept_name
                    ORDER BY sum(X.PlogP) DESC
                ''' % (working_nct_id_0_len, working_nct_id_0_len, table_name, placeholders1, placeholders2)
        else:
            sql = '''
                    SELECT TOP(1) sum(PlogP) AS IE, concept_name
                    FROM(
                        select concept_name, include, count, -(count/%s)*LOG((count/%s)) AS PlogP
                        FROM
                            (
                        select CAST(count(distinct nct_id_original) AS [float]) AS count, concept_name, include
                            from %s
                            where nct_id_original in (%s) and concept_name is NOT NULL
                            and lower(domain) = '%s'
                            and concept_name not in (%s)
                            and to_display = 1
                            group by concept_name, include
                        ) X
                    ) X
                    GROUP BY concept_name
                    ORDER BY sum(X.PlogP) DESC
                ''' % (working_nct_id_0_len, working_nct_id_0_len, table_name, placeholders1, placeholders2, placeholders3)
        cur.execute(sql)
        next_concept = cur.fetchall()
        conn.close()
        cur.close()

        if len(next_concept) > 0:
            this_q = {'question': {'domain': domain, 'entity_text': next_concept[0][1]}}
        else:
            this_q = {'question': {'domain': domain, 'entity_text': 'NQF'}}
        question_answer_list.append(this_q)

    else:
        table_name = 'dbo.all_criteria_v2'
        active_question_0 = [qa['question']['entity_text'] for qa in question_answer_list]
        placeholders2 = ", ".join(str("'" + x + "'") for x in active_question_0)

        if len(active_question_0) == 0:
            sql = '''
                    SELECT TOP(1) sum(PlogP) AS IE, concept_name, domain, include
                    FROM(
                        select concept_name, include, domain, count, -(count/%s)*LOG((count/%s)) AS PlogP
                        FROM
                            (
                        select CAST(count(distinct nct_id_original) AS [float]) AS count, concept_name, include, domain
                            from %s
                            where nct_id_original in (%s) and concept_name is NOT NULL
                            and to_display = 1
                            group by concept_name, include, domain
                        ) X
                    ) X
                    GROUP BY concept_name, domain, include
                    ORDER BY sum(X.PlogP) DESC
                ''' % (working_nct_id_0_len, working_nct_id_0_len, table_name, placeholders1)
        else:
            sql = '''
                    SELECT TOP(1) sum(PlogP) AS IE, concept_name, domain, include
                    FROM(
                        select concept_name, include, domain, count, -(count/%s)*LOG((count/%s)) AS PlogP
                        FROM
                            (
                            select CAST(count(distinct nct_id_original) AS [float]) AS count, concept_name, include, domain
                                from %s
                                where nct_id_original in (%s) and concept_name is NOT NULL
                                and concept_name not in (%s)
                                and to_display = 1
                                group by concept_name, include, domain
                        ) X
                    ) X
                    GROUP BY concept_name, domain, include
                    ORDER BY sum(X.PlogP) DESC
                ''' % (working_nct_id_0_len, working_nct_id_0_len, table_name, placeholders1, placeholders2)
        cur.execute(sql)
        next_concept = cur.fetchall()
        conn.close()
        cur.close()

        if len(next_concept) > 0:
            this_q = {'question': {'domain': next_concept[0][2], 'entity_text': next_concept[0][1]}}
        else:
            this_q = {'question': {'domain': domain, 'entity_text': 'NQF'}}
        question_answer_list.append(this_q)

    return question_answer_list


def find_nct_details(working_nct_id_list, npag):
    '''
    find nct details by connecting to AACT
    :param working_nct_id_list:
    :param npag: page number of result to return
    :return: nct_details_for_this_page is a list of list [[nct_id1, nct_title, nct_summary],[]]. similar to (n, nct) = ctgov.search (stxt, npag)
    '''
    working_nct_id_0 = [(record[1], record[2]) for record in working_nct_id_list if record[3] == 0]
    srt_working_nct_id_0 = sorted(working_nct_id_0, key=lambda x: x[1], reverse=False)
    start_idx = (npag - 1) * 20
    end_idx = min(len(srt_working_nct_id_0), npag * 20)
    nct_id_this_page = [srt[0] for srt in srt_working_nct_id_0[start_idx:end_idx]]
    nct_id_this_page = list(set(nct_id_this_page))
    nct_id_rank = {}
    for srt in srt_working_nct_id_0[start_idx:end_idx]:
        nct_id_rank[srt[0]] = srt[1]

    if len(nct_id_this_page) == 0:
        nct_details_for_this_page = []
    else:
        nct_id_this_page = [str(x) for x in nct_id_this_page]
        placeholder = ", ".join(str("'" + x + "'") for x in nct_id_this_page)
        # placeholder = (tuple(nct_id_this_page))
        # nct_id_this_page = ['NCT02901717','NCT01287182']
        sql = '''
                select c.nct_id,s.brief_title,c.name
                from studies AS s
                left join conditions AS c
                on s.nct_id = c.nct_id
                where s.nct_id in (%s)
            ''' % (placeholder)
        print(sql)
        conn = general_pool_aact.connection()
        cur = conn.cursor()
        cur.execute(sql)
        details = cur.fetchall()
        conn.close()
        cur.close()
        # join condition
        nct_id_condition = {}
        nct_id_title = {}
        for r in details:
            if r[0] not in nct_id_condition.keys():
                nct_id_condition[r[0]] = r[2]
            else:
                nct_id_condition[r[0]] += ',' + r[2]

            if r[0] not in nct_id_title.keys():
                nct_id_title[r[0]] = r[1]

        nct_details_for_this_page = [[nct_id, nct_id_rank[nct_id], nct_id_title[nct_id], nct_id_condition[nct_id]] for
                                     nct_id in nct_id_condition.keys()]
        nct_details_for_this_page = sorted(nct_details_for_this_page, key=lambda x: x[1], reverse=False)
    return nct_details_for_this_page

def find_size_of_active_trials(working_nct_id_list):
    '''
    find size of the remaining trials
    :param working_nct_id_list:
    :return: size
    '''
    size = 0
    working_nct_id_0 = [record[1] for record in working_nct_id_list if record[3] == 0]
    size = len(list(set(working_nct_id_0)))
    return size

# working_nct_id_list = [['NCT02901717', 3431, 0], ['NCT01287182', 3432, 0],['NCT01035944', 3432, 0],['NCT00562068', 3431, 1], ['NCT00742300', 3431, 2]]
# question_answer_list = [{'answer':{'include':'EXC'},'question': {'domain': 'condition', 'entity_text': 'pregnant'}} ]
def update_working_nct_id_list(question_answer_list, working_nct_id_list):
    '''
    update working_nct_id_list by comparing question_answer_list with criteria knowledge base
    :param question_answer_list:
    :param working_nct_id_list:
    :return: an updated working_nct_id_list

    working_nct_id_list = [('NCT02901717', 3431, 0), ('NCT01287182', 3432, 0),('NCT01035944', 3432, 0),('NCT00562068', 3431, 1),('NCT00742300', 3431, 2),]
    question_answer_list = [{'answer': {}, 'question': (3, u'pregnant')}]
    '''
    question_number = len(question_answer_list)

    if question_number > 0:
        this_qa = question_answer_list[question_number - 1]
        this_entity_text = this_qa['question']['entity_text']
        this_domain = this_qa['question']['domain']
        table_name = 'dbo.all_criteria_v2'

        if 'answer' not in this_qa.keys():
            return working_nct_id_list

        this_answer = this_qa['answer']
        this_include = this_answer['include']

        if this_domain.lower() != 'measurement':
            rangestart = 0
            rangeend = 0
            if 'rangestart' in this_answer.keys():
                rangestart = this_answer['rangestart']

            if 'rangeend' in this_answer.keys():
                rangeend = this_answer['rangeend']

            if this_include == 'INC':
                sql = '''
                        select distinct nct_id_original
                        from %s
                        where (LOWER (concept_name) = LOWER ('%s') and
                            is_exclusion = 0 and
                            concept_group_id is null and 
                            (1 = case
                                when before_days != 0 and (%s > before_days) then 1
                                    else 0
                                end)) OR
                            (lower(concept_name) = lower('%s') and
                                is_exclusion = 1)
                        ''' % (table_name, this_entity_text, rangeend, this_entity_text)
            else:
                sql = '''
                        select distinct nct_id_original
                        from %s
                        where lower(concept_name) = lower('%s') and
                            is_exclusion = 0
                        ''' % (table_name, this_entity_text)
        else:
            if 'measurement_value' in this_answer.keys() and this_include == 'INC':
                measurement_value = this_answer['measurement_value']
                print('meas_value: ' + str(measurement_value))
                if measurement_value.isdigit():
                    sql = '''
                            select distinct nct_id_original
                            from %s
                            where (lower(concept_name) = lower('%s') and
                                %s <= numeric_att_max and
                                %s >= numeric_att_min AND
                                is_exclusion = 1) OR
                                (lower(concept_name) = lower('%s') and
                                (%s > numeric_att_max or
                                %s < numeric_att_min) AND
                                is_exclusion = 0 and 
                                concept_group_id is null)
                            ''' % (table_name, this_entity_text, measurement_value, measurement_value, this_entity_text,
                                   measurement_value, measurement_value)
                else:
                    sql = '''
                            select distinct nct_id_original
                            from %s
                            where lower(concept_name) = lower('%s') and
                                (1= case
                                    when (lower('%s') = 'pos' or lower('%s') = 'positive') and 
                                        ((lower(numeric_source_text) = 'negative' and is_exclusion = 0) or 
                                        (lower(numeric_source_text) like '%%positiv%%' and is_exclusion = 1)) then 1
                                    when (lower('%s') = 'neg' or lower('%s') = 'negative') and 
                                        ((lower(numeric_source_text) = 'negative' and is_exclusion = 1) or 
                                        (lower(numeric_source_text) like '%%positiv%%' and is_exclusion = 0)) then 1
                                    else 0
                                end)
                            ''' % (table_name, this_entity_text, measurement_value, measurement_value, measurement_value, measurement_value)
            else:
                sql = '''
                    select top(0) nct_id_original from %s
                ''' % (table_name)

        conn = general_pool_criteria.connection()
        cur = conn.cursor()
        cur.execute(sql)
        details = cur.fetchall()

        filtered_nct_id = []
        filtered_nct_id = [nct_id[0] for nct_id in details]
        conn.close()
        cur.close()
        for c in range(len(working_nct_id_list)):
            if working_nct_id_list[c][0] in filtered_nct_id:
                working_nct_id_list[c][3] = question_number
        return working_nct_id_list
    else:
        return working_nct_id_list
# print(update_working_nct_id_list(question_answer_list,working_nct_id_list))
