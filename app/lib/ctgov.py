'''
set of function to interact with ClinicalTrials.gov
'''

from app import app, general_pool_criteria
from web import download_web_data
from xml.etree import ElementTree
from pyzipcode import ZipCodeDatabase
from extensions import cache
import oformat as of
import urllib


# global ctgov search
def get_initial_nct(txt):
    txt = of.format_search_terms(txt)
    url = 'http://clinicaltrials.gov/search?cond=%s&displayxml=true' % txt
    return get_initial_nct_from_url(url)


def get_initial_nct_detail(recrs, cond, locn):
    recrs = of.format_search_terms(recrs)
    cond = of.format_search_terms(cond)
    locn = of.format_search_terms(locn)
    url = 'http://clinicaltrials.gov/search?cond=%s&recrs=%s&locn=%s&displayxml=true' % (cond, recrs, locn)
    print(url)
    return get_initial_nct_from_url(url)


def get_initial_nct_patient(cond, locn):
    cond = of.format_search_terms(cond)
    locn = of.format_search_terms(locn)
    # url = 'http://clinicaltrials.gov/search?cond=%s&recrs=recrs&type=intr&locn=%s&displayxml=true' % (cond,locn)
    url = 'http://clinicaltrials.gov/search?cond=%s&type=intr&locn=%s&displayxml=true' % (cond, locn)
    print(url)
    return get_initial_nct_from_url(url)


def get_nct_list_from_zip(input_zip, mile_range=50):
    zcdb = ZipCodeDatabase()
    zip_list = [z.zip for z in zcdb.get_zipcodes_around_radius(input_zip, mile_range)]  # default mile range set at 100

    conn = general_pool_criteria.connection()
    cur = conn.cursor()
    sql = '''
            ;with cte (code, DeclarationItem, Declaration) as
            (
              select nct_id,
                cast(left(zip_codes, charindex('|',zip_codes+'|')-1) as varchar(50)) DeclarationItem,
                     stuff(zip_codes, 1, charindex('|',zip_codes+'|'), '') Declaration
              from dbo.aact_trial_info
              union all
              select code,
                cast(left(Declaration, charindex('|',Declaration+'|')-1) as varchar(50)) DeclarationItem,
                stuff(Declaration, 1, charindex('|',Declaration+'|'), '') Declaration
              from cte
              where Declaration > ''
            ) 
            select code as nct_id, DeclarationItem as zip
            from cte
            order by nct_id asc
            option (maxrecursion 0);
        '''
    cur.execute(sql)
    trial_zips = cur.fetchall()
    conn.close()
    cur.close()

    # compare nearby zip codes to trial zip codes
    nearby_nct_list = []
    for item in trial_zips:
        test_nct = item[0]
        if item[1] is not None:
            test_zip = item[1].split('-')[0]
        else:
            test_zip = 00000
        if test_zip in zip_list:
            nearby_nct_list.append(
                test_nct)  # some zip codes stored with '-xxxx' after primary 5 digit, pyzipcode no like that
    nearby_nct_list = list(set(nearby_nct_list))
    # temp loop to add trial number, to be removed in the future
    temp_return_list = []
    i = 1
    for item in nearby_nct_list:
        temp_return_list.append('%s;%d' % (item, i))
        i += 1
    print(len(temp_return_list))
    return temp_return_list

# function to retrieve trials which have user-submitted keyword
def get_nct_list_from_keywords(keyword_string):
    temp = keyword_string.replace('; ', ';')
    keyword_list = temp.split(';')

    # create dynamic string to handle keyword search in sql
    key_search = ""
    if len(keyword_list) > 0:
        key_search = "where "
        for item in [x.lower() for x in keyword_list]:
            key_search = key_search + "(lower(condition_names) like '%" + item + "%' or "
            key_search = key_search + "lower(intervention_names) like '%" + item + "%' or "
            key_search = key_search + "lower(official_title) like '%" + item + "%' or "
            key_search = key_search + "lower(outcome_measure) like '%" + item + "%') and "
        key_search = key_search[:-5]

    # send query to server
    conn = general_pool_criteria.connection()
    cur = conn.cursor()
    sql = '''
                select nct_id
                from dbo.aact_trial_info
                %s
                order by nct_id asc
                ''' % key_search
    print(sql)
    cur.execute(sql)
    key_trials = cur.fetchall()
    conn.close()
    cur.close()

    # clean up items being returned
    to_return = []
    if len(key_trials) > 0:
        for item in key_trials:
            to_return.append(item[0])
    # else:
    #     to_return.append('Error')

    return to_return


# function to query trial information to build modal
def query_trial_info_for_modal(nct_id):
    conn = general_pool_criteria.connection()
    cur = conn.cursor()
    sql = '''
            select official_title, study_type, primary_purpose, study_description, gender, minimum_age, maximum_age, 
                healthy_volunteers, phase, allocation, intervention_model, observation_model,
                masking, outcome_measure, outcome_description, facilities_and_contacts, intervention_names, central_contacts
            from dbo.aact_trial_info
            where nct_id = '%s'
            ''' % nct_id
    cur.execute(sql)
    trial_data = cur.fetchall()
    conn.close()
    cur.close()

    # clean up items being returned
    to_return = []
    if len(trial_data) == 1:
        to_return.extend(trial_data[0])
    else:
        to_return.append('Error')

    return to_return


# global ctgov search from url
# @cache.memoize(604800)
def get_initial_nct_from_url(url):
    # num. of studies available
    n = get_nct_number('%s&count=0' % url)
    print('num. of studies available ', n)
    if n == 0:
        return []
    # get the list of clinical studies
    xmltree = ElementTree.fromstring(download_web_data('%s&count=%d' % (url, n)))
    lnct = xmltree.findall('clinical_study')
    rnct = []
    i = 1
    for ct in lnct:
        ids = ct.find('nct_id')
        if ids is None:
            continue
        rnct.append('%s;%d' % (ids.text, i))
        i += 1
    print(rnct)
    return rnct


# get result number
def get_nct_number(url):
    xml = download_web_data(url)
    if xml is None:
        return 0
    xmltree = ElementTree.fromstring(xml)
    nnct = xmltree.get('count')
    return int(nnct)


# parse clinical trial details
def parse_xml_nct(ct):
    ids = ct.find('nct_id')
    if ids is None:
        return ids
    ids = ids.text
    rank = ct.find('order')
    if rank is not None:
        rank = rank.text
    title = ct.find('title')
    if title is not None:
        title = title.text
    condition = ct.find('condition_summary')
    if condition is not None:
        condition = condition.text
    return (ids, rank, title, condition)


# ctgov search
def search(txt, npag):
    txt = of.format_search_terms(txt)
    url = 'http://clinicaltrials.gov/search?cond=%s&displayxml=true' % txt
    return retrieve_trials(url, npag)


# ctgov advanced search
def advanced_search(param):
    url = form_advanced_search_url(param)
    return retrieve_trials(url, param.get('npag'))


# get advanced search url
def form_advanced_search_url(param):
    ctg_param = ''
    for r in sorted(param):
        k = urllib.quote(r, '')
        if k == 'qlabel':
            continue
        for v in param.getlist(r):
            ctg_param += "%s=%s&" % (k, urllib.quote(v, ''))
    return 'http://clinicaltrials.gov/ct2/results?%sdisplayxml=True' % ctg_param


# get the list of resulting clinical trials
def retrieve_trials(url, npag):
    # num. of studies available
    n = of.format_nct_number(get_nct_number('%s&count=0' % url))
    # get the list of clinical studies
    xml = download_web_data('%s&pg=%s' % (url, npag))
    if xml is None:
        return (0, [])
    xmltree = ElementTree.fromstring(xml)
    lnct = xmltree.findall('clinical_study')
    nct = []
    for ct in lnct:
        pct = parse_xml_nct(ct)
        if pct[0] is not None:
            cond = of.format_condition(pct[3])
            nct.append((pct[0], pct[1], pct[2], cond))
    return (n, nct)
