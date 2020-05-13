function pre_questions_search(){
    var age = $('#pre_questions_age').val();
//    var gender = $('#pre_questions_gender').val();
    var domain = $('#pre_questions_domain').val();
    var exposure = $('#pre_questions_exposure').val();
    var stat = $('#pre_questions_patient_stat').val();
    var preg = $('#pre_questions_patient_preg').val();

    if ($("#user_picked_time").attr('time_string') !== '') {
        var user_picked_time = $("#user_picked_time").attr('time_string');
        // a['rangestart'] = -rangestart.diff(today_time, 'days');
    }
    console.log(age + ' ' + gender + ' ' + domain + ' ' + user_picked_time + ' '+ exposure +' ' + stat + ' ' + preg);

    var result = [];
    $.getJSON($SCRIPT_ROOT + '/_pre_questions',
            {age: age,
                gender : gender,
                domain : domain,
                user_picked_time: user_picked_time,
                exposure: exposure,
                stat:stat,
                preg:preg,
            },
            function (data) {
                result = data;
                console.log(data);
            });
    return result;
}

function search(tsearch) {
    if (tsearch == 'advanced') {
        var form_args = $(adv_search).serializeArray();
        qlabel_value = $('#qlabel').text();
        var qlabel = {
            "name": "qlabel",
            "value": qlabel_value
        };
        form_args.push(qlabel);
        $.blockUI({
            message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
            css: {
                border: 'none',
                '-webkit-border-radius': '40px',
                '-moz-border-radius': '40px',
                opacity: .5,
            },
        });

        $.getJSON($SCRIPT_ROOT + '/_advs_start_question',
            form_args,
            function (data) {
                search_n = data.working_nct_id_list.length;
                tag_name = 'advanced search';
                $('#search_n').html(search_n);
                $('#tag_name').html(tag_name);
                nres = parseInt(search_n);
                if (nres >= 1 && nres <= 25000) {
                    $("#qfilt").show();
                    $('#qfilt').unbind('click');
                    $('#qfilt').bind('click', function () {
                        start_question(tsearch);
                        $('#search_form_container').hide();
                        $('#question_container').show();
                        $('#results_container').show();
                        $('#search_results_container').hide();
                        $('#multiquestions_container').hide();
                        $('#filter_results_container').show();
                        $('#filter_results').hide();
                        $("#qfilt").hide();
                    });
                    find_search_results(data.working_nct_id_list, 1);
                } else {
                    if (nres > 25000) {
                        $("#qfilt").hide();
                        $("#qfilt_warning_1").show();
                        $('#qfilt').unbind('click');

                    }
                    else {
                        $("#qfilt").hide();
                        $("#qfilt_warning_2").show();
                        $('#qfilt').unbind('click');
                    }
                }

            });
    } else {
        $.blockUI({
            message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
            css: {
                border: 'none',
                '-webkit-border-radius': '40px',
                '-moz-border-radius': '40px',
                opacity: .5,
            },
        });
        // var cond = $('#first_focus').val();
        // var recrs = $('#recruit_status').val();
        var locn = $('#location_terms').val();
        var miles = $('#nearby_miles').val();
        var trial_type = $('#trial_type').val();
        var active_restriction = $('#active_trial_restriction').is(':checked');
        var keyword_search = $('#keyword_search_terms').val();
        // if (recrs == 'All') {
        //     recrs = ''
        // }
        $.getJSON($SCRIPT_ROOT + '/_hao_start_question', {
            // cond: cond,
            locn: locn,
            miles: miles,
            trial_type: trial_type,
            active_restriction:active_restriction,
            keyword_search:keyword_search
        }, function (data) {
            search_n = data.working_nct_id_list.length;
            tag_name = $('#first_focus').val();
            $('#search_n').html(search_n);
            $('#search_n_1').html(search_n);
            $('#tag_name').html(tag_name);
            $('#tag_name_1').html(tag_name);
            nres = parseInt(search_n);
            if (nres >= 1 && nres <= 25000) {
                $("#qfilt").show();
                $("#qfilt_warning").hide();
                $('#qfilt').unbind('click');
                $('#qfilt').bind('click', function () {
                    var age = $('#pre_questions_age').val();
                    if (age == '') {
                        alert('Please enter your age and answer the above questions to help us identify trials that are right for you!');
                    } else {
                        filter_n = start_question(tsearch);
                    }
                    // $('#search_form_container').hide();
                    // $('#question_container').show();
                    // $('#results_container').show();
                    // $('#multiquestions_container').hide();
                    // $('#search_results_container').hide();
                    // $('#filter_results_container').show();
                    // $("#qfilt").hide();
                    // alert('Based on your location and the information you provided, you are not currently eligible for any trials in your area. Please feel free to return to the homepage using the \'Home\' button above to adjust any information that you entered or to stay up-to-date as new trials are published!');

                });
                // find_search_results(data.working_nct_id_list, 1);

            } else {
                if (nres > 25000) {
                    $("#qfilt").hide();
                    $("#qfilt_warning_1").show();
                    $('#qfilt').unbind('click');

                }
                else {
                    $("#qfilt").hide();
                    $("#qfilt_warning_2").show();
                    $('#qfilt').unbind('click');
                }
            }

        });
    }
}

// show the trial list
function result_content(nct_details_for_this_page) {

    var nct = nct_details_for_this_page;
    var sout = new String();
    for (var k in nct) { // rank
        // sout += '<tr><td class="rank">' + nct[k][1] + '</td>';
        // // title
        // sout += '<td class="title"><a href="http://clinicaltrials.gov/ct2/show/' + nct[k][0] + '" target="_blank">' + nct[k][2] + '</a>';
        // // sout += '<td class="title"><a href="http://haotianyong.appspot.com/cluster_gov?/ct2/show/' + nct[k][0] + '" target="_blank">' + nct[k][2] + '</a>';
        // // condition
        // sout += '<table class="ct_detail"><tr><td id="dtitle"> Condition: </td><td id="dvalue">' + nct[k][3] + '</td></tr></table></tr>';
        sout += '<div class="trial_listing_group item">';
        // sout += '<i class="ui large icon middle aligned">' + nct[k][1] + ' </i><div class="content">'
        // sout += '<a href="http://clinicaltrials.gov/ct2/show/' + nct[k][0] + '" target="_blank" class="header">' + nct[k][2] + '</a>';
        // sout += '<div class="meta"><span>ctgov rank: <div class="">' +   + '</div></span></div>';
        sout += '<a target="_blank" class="trial_listing_header" name="' + nct[k][0] + '">' + nct[k][2] + '</a>';
        sout += '<div class="trial_listing_description"><p> Conditions: <code style="font-family: sans-serif;">' + nct[k][3] + '</code></p></div>';
        sout += '</div></div>';
    }

    return sout
}

// start first question
function start_question(tsearch) {
    result =0;
    if (tsearch == 'advanced') {
        var form_args = $(adv_search).serializeArray();
        qlabel = $('#qlabel').text();
        var qlabel = {
            "name": "qlabel",
            "value": qlabel
        };
        form_args.push(qlabel);
        $
        $.blockUI({
            message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
            css: {
                border: 'none',
                '-webkit-border-radius': '40px',
                '-moz-border-radius': '40px',
                opacity: .5,
            },
        });

        $.getJSON($SCRIPT_ROOT + '/_advs_start_question',
            form_args,
            function (data) {
                search_n = data.working_nct_id_list.length;
                $('#filter_n').html(search_n);
                nres = parseInt(search_n);
                find_results(data.working_nct_id_list, 1);
                q_visualization(data.question_answer_list, data.working_nct_id_list);

            });
    } else {
        $.blockUI({
            message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
            css: {
                border: 'none',
                '-webkit-border-radius': '40px',
                '-moz-border-radius': '40px',
                opacity: .5,
            },
        });
        var cond = $('#first_focus').val();
        var recrs = $('#recruit_status').val();
        var locn = $('#location_terms').val();
        var miles = $('#nearby_miles').val();
        var trial_type = $('#trial_type').val();
        var age = $('#pre_questions_age').val();
        var gender = $('#pre_questions_gender').val();
        var domain = $('#pre_questions_domain').val();
        var exposure = $('#pre_questions_exposure').val();
        var stat = $('#pre_questions_patient_stat').val();
        var preg = $('#pre_questions_patient_preg').val();
        if ($("#user_picked_time").attr('time_string') !== '') {
            var user_picked_time = $("#user_picked_time").attr('time_string');
        }

        if (recrs == 'All') {
            recrs = ''
        }
        $.getJSON($SCRIPT_ROOT + '/_pts_start_question', {
            cond: cond,
            locn: locn,
            miles: miles,
            trial_type: trial_type,
            age: age,
            gender : gender,
            domain : domain,
            user_picked_time: user_picked_time,
            exposure: exposure,
            stat:stat,
            preg:preg,
        }, function (data) {
            result = data.working_nct_id_list.length;
            if (result > 0){
                $('#search_form_container').hide();
                if (result > 1) {
                    $('#question_container').show();
                } else {
                     $('#question_container').hide();
                    document.getElementById("result_trial_count_display").innerHTML = "You are eligible for <code id=\'filter_n\' style='color:#007bff;'></code> trial";
                }
                $('#results_container').show();
                $('#multiquestions_container').hide();
                $('#search_results_container').hide();
                $('#filter_results_container').show();
                $("#qfilt").hide();
                $('#filter_results').show();

                console.log('search_n is', result);
                $('#filter_n').html(result);
                nres = parseInt(result);
                find_results(data.working_nct_id_list, 1);
                q_visualization(data.question_answer_list, data.working_nct_id_list);
            } else{
                // alert('Based on your location and the information you provided, you are not currently eligible for any trials in your area. Please feel free to return to the homepage using the \'Home\' button above to adjust any information that you entered or to stay up-to-date as new trials are published!');
                $("#found_no_modal").modal('show');
            }

        });
    }
    return result;
}

// visualize question_form
function q_visualization(question_answer_list, working_nct_id_list) {
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // generate form TO BE IMPLEMENTED
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    $('#question_tags').empty();
    $("#include option[value='NULL']").attr("selected", "selected");
    qa = question_answer_list[question_answer_list.length - 1]
    q = qa.question
    sout = 'Answer Question';
    sout += '<div class="ui horizontal label">';
    sout += question_answer_list.length.toString();
    sout += '</div>'
    $('#question_number').html(sout);

    console.log(q.domain);
    $("#domain_cond").attr('disabled', true)

    include_has = "<select class='ui fluid dropdown' name  = 'include' id = 'include'  ><option value='NULL' selected>I don't know/I don't want to answer</option><option value='EXC'>No</option><option value='INC'>Yes</option>"
    include_none = "<select class='ui fluid dropdown' ><option disabled = 'disabled'>No</option><option disabled = 'disabled'>I don't know/I don't want to answer</option><option  disabled = 'disabled'>Yes</option>"

    domain_has = ' <select class="ui fluid dropdown" id="domain" name="domain">\
                    <option value= all selected>Any</option>\
                    <option value= condition>Medical History</option>\
                    <option value= measurement>Lab Tests</option>\
                    <option value= drug>Treatment History</option>\
                    <option value= device>Device History</option>\
                    <option value= procedure>Surgical/Procedure History</option>\
                </select>'

    if (q.entity_text != 'NQF') {
	//create a new one to cover the fake one
        $('#include').html(include_has);
	$('#domain').html(domain_has);

        if (q.domain.toLowerCase() == 'condition') {
            x = '<div class="ui pink horizontal label">Medical History</div>'
            sout = 'Have you ever been diagnosed with: ' + q.entity_text + x + '?';
            $('#question_title').html(sout)
        }
        if (q.domain.toLowerCase() == 'drug') {
            x = '<div class="ui purple horizontal label">Treatment History</div>'
            sout = 'Are you currently taking: ' + q.entity_text + x + '?';
            $('#question_title').html(sout)
        }
        if (q.domain.toLowerCase() == 'procedure') {
            x = '<div class="ui brown horizontal label">Surgical/Procedure History</div>'
            sout = 'Have you ever undergone or are you currently using: ' + q.entity_text + x + '?';
            $('#question_title').html(sout)
        }
        if (q.domain.toLowerCase() == 'measurement') {
            x = '<div class="ui blue horizontal label">Lab Tests</div>'
            sout = 'Do you know your most recent: ' + q.entity_text + x + '?';
            $('#question_title').html(sout)
        }
        if (q.domain.toLowerCase() == 'device') {
            x = '<div class="ui olive horizontal label">Devices</div>'
            sout = 'Are you currently using: ' + q.entity_text + x + '?';
            $('#question_title').html(sout);
        }
    } else {
        // no more questions.
        let display_domain = '';
        if (q.domain.toLowerCase() == 'condition') {
            display_domain = 'No more questions about your Medical History. Please change to another domain or review your trial results below';
        } else if (q.domain.toLowerCase() == 'drug') {
            display_domain = 'No more questions about your Treatment History. Please change to another domain or review your trial results below';
        } else if (q.domain.toLowerCase() == 'procedure') {
            display_domain = 'No more questions about your Surgical/Procedure History. Please change to another domain or review your trial results below';
        } else if (q.domain.toLowerCase() == 'measurement') {
            display_domain = 'No more questions about your Lab Tests. Please change to another domain or review your trial results below';
        } else if (q.domain.toLowerCase() == 'device') {
            display_domain = 'No more questions about your Devices. Please change to another domain or review your trial results below';
        } else {
            display_domain = 'No more questions about your history. Please review your trial results below';
        }
        $('#question_title').html(display_domain);
        //make a fake selection box to cover the originial one
	$('#include').html(include_none);
	console.log(q.domain);
	$("#domain").html(domain_has.replace('value= '+q.domain.toLowerCase(), 'value= '+q.domain.toLowerCase()+' disabled'))
    }

	// add confirm.
    $('#confirmbutton').unbind('click');
    $('#confirmbutton').bind('click', function () {
        if ($("#include").val() != 'NULL') {
            qa['answer'] = {};
            a = qa['answer'];
            a['include'] = $("#include").val();
            if ($('#include').val() == 'INC') {
                var title = $('#question_title').children('div').text();
                if (title != 'Lab Tests') {
                    var today = new Date();
                    var dd = today.getDate();
                    var mm = today.getMonth() + 1; //January is 0!
                    var yyyy = today.getFullYear();
                    if (dd < 10) {
                        dd = '0' + dd
                    }
                    if (mm < 10) {
                        mm = '0' + mm
                    }
                    var today_time = mm + '/' + dd + '/' + yyyy;
                    if ($("#rangestart").attr('time_string') !== '') {
                        var rangestart = moment($("#rangestart").attr('time_string'), 'MM/DD/YYYY');
                        a['rangestart'] = -rangestart.diff(today_time, 'days');
                    }

                    if ($("#rangeend").attr('time_string') !== '') {

                        var rangeend = moment($("#rangeend").attr('time_string'), 'MM/DD/YYYY');
                        a['rangeend'] = -rangeend.diff(today_time, 'days');
                    }
                } else {
                    if ($("#measurement_value").val() != '') {
                        a['measurement_value'] = $("#measurement_value").val();
                    }
                }
            }

        }
        domain = $('#domain').val();
        confirm(question_answer_list, working_nct_id_list, domain);
        semantiUIInit();
        $('#domain').dropdown('set selected', domain);
    });
    // add tag.
for (var i = 1; i <= question_answer_list.length; i++) {
    var sout = new String();
    sout += '<a class="item" id="qtag_' + i + '">'
    domain = question_answer_list[i - 1].question.domain;
    if (domain.toLowerCase() == 'condition') {
        sout += '<div class="ui pink horizontal label" style="float:left;">MH</div>';
    }
    if (domain.toLowerCase() == 'drug') {
        sout += '<div class="ui purple horizontal label" style="float:left;">TH</div>';
    }
    if (domain.toLowerCase() == 'procedure') {
        sout += '<div class="ui brown horizontal label" style="float:left;">SH</div>';
    }
    if (domain.toLowerCase() == 'measurement') {
        sout += '<div class="ui blue horizontal label" style="float:left;">LT</div>';
    }
    if (domain.toLowerCase() == 'device') {
        sout += '<div class="ui olive horizontal label" style="float:left;">DH</div>';
    }

    sout += '</div>'
    sout += '<span style="display:block;overflow:hidden;">' + question_answer_list[i - 1].question.entity_text + '</span>';
    sout += '</a>'
        $('#question_tags').append(sout);
    $("#qtag_" + i).unbind('click');
    $("#qtag_" + i).bind('click', { 'idx': i, 'q': question_answer_list, 'w': working_nct_id_list }, function (e) {
        var local_i = e.data.idx;
        var q = e.data.q;
        var w = e.data.w;
        if (local_i > 1) {
            d = q[local_i - 1].question.domain;
            q = q.slice(0, local_i - 1);
        } else {
            d = 'ALL';
            q = [];
        }
        for (var j = 0; j < w.length; j++) {
            if (w[j][3] >= local_i) {
                // change status.
                w[j][3] = 0
            }
        }
        confirm(q, w, d);
    });
}
}



// event binding to confirm button
function confirm(question_answer_list, working_nct_id_list, domain) {
    formData = {
        'question_answer_list': question_answer_list,
        'working_nct_id_list': working_nct_id_list,
        'domain': domain
    };
    $.blockUI({
        message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
        css: {
            border: 'none',
            '-webkit-border-radius': '40px',
            '-moz-border-radius': '40px',
            opacity: .5,
        },
    });
    $.ajax({
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        type: 'POST',
        url: $SCRIPT_ROOT + '/_confirm',
        data: JSON.stringify(formData),
        dataType: "json",
        success: function (data) {
            console.log(data);
            $('#confirmbutton').unbind('click');
            q_visualization(data.question_answer_list, data.working_nct_id_list);
            find_results(data.working_nct_id_list, 1);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
}

function find_search_results(working_nct_id_list, np) {
    formData = {
        'working_nct_id_list': working_nct_id_list,
        'npag': np
    }
    $.blockUI({
        message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
        css: {
            border: 'none',
            '-webkit-border-radius': '40px',
            '-moz-border-radius': '40px',
            opacity: .5,
        },
    });
    $.ajax({
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        type: 'POST',
        url: $SCRIPT_ROOT + '/_find_nct_by_page',
        async: false,
        data: JSON.stringify(formData),
        dataType: "json",
        success: function (data) { // format query
            // sout = '<p class="recap"> Left <span class="drecap">' + data.size_of_active_trials + '</span> clinical trials for: <span id="qlabel" class="drecap">' + data.q + '<span></p>';
            show_search_results(data.working_nct_id_list, data.npag, data.nct_details_for_this_page, data.size_of_active_trials);

        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
}

function show_search_results(working_nct_id_list, npag, nct_details_for_this_page) {
    size_of_active_trials = working_nct_id_list.length
    // sout = '<table id="search_table">';
    sout = result_content(nct_details_for_this_page);
    // page navigation
    // sout += '<tr><td colspan="3"><p id="nav_search">'
    np = parseInt(npag);
    sfirst = (np - 1) * 20 + 1;
    slast = np * 20;
    $('#sfirst').html(sfirst);
    $('#slast').html(slast);
    // previous
    if (np > 1) {
        $('#rprev').unbind('click');
        $('#rprev').bind('click', function () {
            find_search_results(working_nct_id_list, parseInt(npag) - 1);
            $(document).scrollTop(0);
        });
    } else {
        $('#rprev').unbind('click')
    }
    // next
    pmax = Math.ceil(parseInt(size_of_active_trials) / 20);
    if (np + 1 <= pmax) {
        $('#rnext').unbind('click');
        $('#rnext').bind('click', function () {
            find_search_results(working_nct_id_list, parseInt(npag) + 1);

            $(document).scrollTop(0);
        });
    } else {
        $('#rnext').unbind('click')
    }



    $("#search_results").children('.list').html(sout);


}
// find results (similar to search)
// function to search
function find_results(working_nct_id_list, np) {
    formData = {
        'working_nct_id_list': working_nct_id_list,
        'npag': np
    }
    $.blockUI({
        message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
        css: {
            border: 'none',
            '-webkit-border-radius': '40px',
            '-moz-border-radius': '40px',
            opacity: .5,
        },
    });
    $.ajax({
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        type: 'POST',
        url: $SCRIPT_ROOT + '/_find_nct_by_page',
        data: JSON.stringify(formData),
        dataType: "json",
        success: function (data) { // format query
            // sout = '<p class="recap"> Left <span class="drecap">' + data.size_of_active_trials + '</span> clinical trials for: <span id="qlabel" class="drecap">' + data.q + '<span></p>';
            // $('#filter_header_results').html(sout)
            filter_n = data.size_of_active_trials
            $("#filter_n").html(filter_n);
            show_qfilter_results(data.working_nct_id_list, data.npag, data.nct_details_for_this_page, data.size_of_active_trials);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
}

// function to handle modal display for trial information
function generate_trial_info_modal(nct_id) {
    console.log('clicked-on NCT ID: ' + nct_id);

    $.getJSON($SCRIPT_ROOT + '/_retrieve_modal_data', {
            nctid: nct_id
        },
        function (data) {
            official_title=data.official_title;
            study_type = data.study_type;
            primary_purpose = data.primary_purpose;
            study_description = data.study_description;
            gender = data.gender;
            minimum_age = data.minimum_age;
            maximum_age = data.maximum_age;
            healthy_volunteers = data.healthy_volunteers;
            phase = data.phase;
            allocation = data.allocation;
            intervention_model = data.intervention_model;
            observation_model = data.observation_model;
            masking = data.masking;
            outcome_measure = data.outcome_measure;
            outcome_description = data.outcome_description;
            fac_and_con = data.facilities_and_contacts;
            interventions = data.intervention_names;
            central_contact = data.central_contact;
        })

        .done(function () {
            // modifying top of the modal information
            if (official_title != null) {document.getElementById("modal_official_title").innerHTML = official_title};
            if (nct_id != null) {document.getElementById("modal_nct_id").innerHTML = nct_id};
            if (study_type != null) {document.getElementById("modal_study_type").innerHTML = study_type};
            if (primary_purpose != null) {document.getElementById("modal_primary_purpose").innerHTML = primary_purpose};
            if (study_description != null) {document.getElementById("modal_study_description").innerHTML = study_description};
            if (gender != null) {document.getElementById("modal_gender").innerHTML = gender};
            if (minimum_age != null) {document.getElementById("modal_min_age").innerHTML = minimum_age};
            if (maximum_age != null) {document.getElementById("modal_max_age").innerHTML = maximum_age};
            if (healthy_volunteers != null) {document.getElementById("modal_healthy_volunteers").innerHTML = healthy_volunteers};

            // make some small adjustments based on study type
            if (study_type == 'Interventional') {
                if (allocation != null) {document.getElementById("modal_allocation").innerHTML = allocation};
                if (masking != null) {document.getElementById("modal_masking").innerHTML = masking};
                if (interventions != null) {document.getElementById("modal_intervention").innerHTML = interventions};
                document.getElementById("modal_int_obs_model_title").innerHTML = "Intervention Model";
                if (intervention_model != null) {document.getElementById("modal_int_obs_model_description").innerHTML = intervention_model};
            } else {
                document.getElementById("modal_allocation").style.display = "none";
                document.getElementById("modal_masking").style.display = "none";
                document.getElementById("modal_allocation_title").style.display = "none";
                document.getElementById("modal_masking_title").style.display = "none";
                if (study_type == 'Observational') {
                    document.getElementById("modal_intervention_title").style.display = "none";
                    document.getElementById("modal_intervention").style.display = "none";
                    document.getElementById("modal_int_obs_model_title").innerHTML = "Observation Model";
                    if (observation_model != null) {
                        document.getElementById("modal_int_obs_model_description").innerHTML = observation_model
                    };
                } else {
                    document.getElementById("modal_int_obs_model_title").innerHTML = "Expanded Access";
                    document.getElementById("modal_int_obs_model_description").innerHTML = "Expanded Drug Access";
                    if (interventions != null) {document.getElementById("modal_intervention").innerHTML = interventions};
                }
            }
            if (phase != null) {document.getElementById("modal_phase").innerHTML = phase};
            if (outcome_measure != null) {document.getElementById("modal_primary_outcome_measure").innerHTML = outcome_measure};
            if (outcome_description != null) {document.getElementById("modal_primary_outcome_description").innerHTML = outcome_description};

            // managing central contact information
            console.log(central_contact);
            if (central_contact.length == 3) {
                [phone, email] = sort_email_phone(central_contact[1], central_contact[2]);
                document.getElementById("modal_cc_name").innerHTML = 'Contact Name: ' + central_contact[0];
                document.getElementById("modal_cc_phone").innerHTML = 'Contact Phone: ' + phone;
                document.getElementById("modal_cc_email").innerHTML = 'Contact Email: ' + email;
            } else {
                document.getElementById("modal_cc_name").innerHTML = 'Contact Name: ' + central_contact[0];
                document.getElementById("modal_cc_phone").innerHTML = 'Contact Phone: ' + central_contact[1];
            }

            // managing recruiting locations and associated contacts
            for (var i = 0; i < fac_and_con.length; i++) {
                console.log('working on :' + fac_and_con[i]);
                new_div = build_location_div(fac_and_con[i]);
                $(new_div).appendTo('#tabs-lo');
            }

            document.getElementById("modal_ctgov_link").href = "http://clinicaltrials.gov/ct2/show/" + nct_id;

            var modal = document.getElementById("myModal");
            modal.style.display = "block";
        })
}

// function to reset all fields in info modal after closing
function reset_info_modal() {
    // reset text of all items
    document.getElementById("modal_official_title").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_nct_id").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_study_type").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_primary_purpose").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_study_description").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_gender").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_min_age").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_max_age").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_healthy_volunteers").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_intervention").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_phase").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_allocation").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_int_obs_model_description").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_masking").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_primary_outcome_measure").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_primary_outcome_description").innerHTML = 'No information available in ClinicalTrials.gov';
    document.getElementById("modal_cc_name").innerHTML = 'Contact Name: No information available in ClinicalTrials.gov';
    document.getElementById("modal_cc_phone").innerHTML = 'Contact Phone: No information available in ClinicalTrials.gov';
    document.getElementById("modal_cc_email").innerHTML = 'Contact Email: No information available in ClinicalTrials.gov';

    // make sure items that can be toggled are displayed
    document.getElementById("modal_intervention_title").style.display = "block";
    document.getElementById("modal_intervention").style.display = "block";
    document.getElementById("modal_allocation").style.display = "block";
    document.getElementById("modal_masking").style.display = "block";
    document.getElementById("modal_allocation_title").style.display = "block";
    document.getElementById("modal_masking_title").style.display = "block";

    // remove all location blocks
    $('.location_block').remove();
}

// function to build small div for location and contact information
function build_location_div(fac_info) {
    let new_var = '<div class="row location_block" style="padding-left:0;">';
    new_var = new_var + '<strong>' + fac_info[0] + '</strong>';
    new_var = new_var + '<p class="location_item">' + fac_info[1] + ', ' + fac_info[2] + ' ' + fac_info[3] + '</p>';
    if ((fac_info[4] != '' || fac_info[5] != '' || fac_info[6] != '') &&
        (fac_info[4] != null && fac_info[5] != null && fac_info[6] != null)) {
        [phone, email] = sort_email_phone(fac_info[5], fac_info[6]);
        new_var = new_var + '<ul>';
        if (fac_info[4] != '') {new_var = new_var + '<li>Contact Person: ' + fac_info[4] + '</li>'};
        if (fac_info[5] != '') {new_var = new_var + '<li>Phone Number: ' + phone + '</li>'};
        if (fac_info[6] != '') {new_var = new_var + '<li>Email Address: <a href="mailto:' + email + '">' + email + '</a></li>'};
        new_var = new_var + '</ul>';
    }
    new_var = new_var + '</div>';
    return new_var;
}

// function to handle improperly formatted email and phone numbers in CT.gov
function sort_email_phone(phone_orig, email_orig) {
    console.log(phone_orig);
    console.log(email_orig);
    const RE = /^[\d\.\-]+$/;
    phone_orig = phone_orig.replace('+', '');
    if (RE.test(phone_orig) && email_orig.indexOf("@") > -1) {
        return [phone_orig, email_orig];
    } else if (RE.test(email_orig) && phone_orig.indexOf('@') > -1) {
        return [email_orig, phone_orig];
    } else {
        let phone_new = '';
        let email_new = '';
        if (RE.test(phone_orig)) {
            phone_new = phone_orig;
        } else if (RE.test(email_orig)) {
            phone_new = email_orig;
        }
        if (phone_orig.indexOf('@') > -1) {
            email_new = phone_orig;
        } else if (email_orig.indexOf('@') > -1) {
            email_new = email_orig;
        }
        if ((['', 'unknown', 'undefined'].indexOf(phone_orig) >= 0) & phone_new == '') {
            phone_new = 'Please go ClinicalTrials.gov for additional information'
        }
        if ((['', 'unknown', 'undefined'].indexOf(email_orig) >= 0) & email_new == '') {
            email_new = 'Please go ClinicalTrials.gov for additional information'
        }
        return [phone_new, email_new]
    }
}


// function to output the search results
function show_qfilter_results(working_nct_id_list, npag, nct_details_for_this_page, size_of_active_trials) {
    sout = result_content(nct_details_for_this_page);
    // sout += '<tr><td colspan="3"><p id="nav_search">'
    np = parseInt(npag);
    ffirst = (np - 1) * 20 + 1;
    flast = np * 20;
    $('#ffirst').html(ffirst);
    $('#flast').html(flast);
    // previous
    if (np > 1) {
        $('#fprev').unbind('click');
        $('#fprev').bind('click', function () {
            find_results(working_nct_id_list, parseInt(npag) - 1);
            $(document).scrollTop(0);
        });
    } else {
        $('#fprev').unbind('click')
    }
    // next
    pmax = Math.ceil(parseInt(size_of_active_trials) / 20);
    if (np + 1 <= pmax) {
        $('#fnext').unbind('click');
        $('#fnext').bind('click', function () {
            find_results(working_nct_id_list, parseInt(npag) + 1);
            $(document).scrollTop(0);
        });
    } else {
        $('#fnext').unbind('click')
    }

    $("#filter_results").children('.list').html(sout);
}

function semantiUIInit() {
    $('#rangeend').attr('readonly', false);
    $('#rangestart').attr('readonly', false);
    $('#user_picked_time').attr('readonly', false);
    $('#rangeend').attr('time_string', '');
    $('#rangestart').attr('time_string', '');
    $('#user_picked_time').attr('time_string', '');
    $('.ui.dropdown').dropdown('restore defaults');
    $('#rangestart').calendar({
        type: 'date',
        today: true,
        endCalendar: $('#rangeend'),
        onChange: function (date) {
            if (date !== undefined) {
                var year = date.getFullYear();
                var month = date.getMonth() + 1;
                var day = date.getDate();
                if (month < 10) {
                    month = '0' + month;
                }
                if (day < 10) {
                    day = '0' + day;
                }
                time = month + '/' + day + '/' + year;
                $(this).attr('time_string', time);
                // everything combined
                console.log(time);
            }

        }
    });
    $('#rangeend').calendar({
        type: 'date',
        today: true,
        startCalendar: $('#rangestart'),
        onChange: function (date) {
            if (date !== undefined) {
                var year = date.getFullYear();
                var month = date.getMonth() + 1;
                var day = date.getDate();
                if (month < 10) {
                    month = '0' + month;
                }
                if (day < 10) {
                    day = '0' + day;
                }
                time = month + '/' + day + '/' + year;
                $(this).attr('time_string', time);
                // everything combined
                console.log(time);
            }
        }
    });
    $('#user_picked_time').calendar({
        type: 'date',
        today: true,
        onChange: function (date) {
            if (date !== undefined) {
                var year = date.getFullYear();
                var month = date.getMonth() + 1;
                var day = date.getDate();
                if (month < 10) {
                    month = '0' + month;
                }
                if (day < 10) {
                    day = '0' + day;
                }
                time = month + '/' + day + '/' + year;
                $(this).attr('time_string', time);
                // everything combined
                console.log(time);
            }

        }
    });
    $('.ui.calendar').calendar('clear');
    $('#measurement_value').val('');
    $('#value_input_container').hide();
    // $('.ui.form')
    //     .form({
    //         fields: {
    //             term: 'empty'
    //         }
    //     });
    // $('.ui.form').form({
    //     fields : {
    //         term : 'empty'
    //     }
    // });
    $('.ui.search')
        .search({
            minCharacters: 3,
            showNoResults: false,
            apiSettings: {
                onResponse: function (ctResponse) {
                    var
                        response = {
                            results: []
                        };
                    // translate GitHub API response to work with search
                    $.each(ctResponse, function (index, item) {
                        var
                            maxResults = 8;
                        if (index >= maxResults) {
                            return false;
                        }
                        // create new language category

                        // add result to category
                        response.results.push({
                            title: item

                        });
                    });
                    return response;
                },
                url: 'https://cors.io/?https://clinicaltrials.gov/ct2/rpc/extend/cond?cond={query}'
            },
            onSelect: function (result) {
                $('#first_focus').val(result.title);
                $('#search_button').focus();
            }

        });

}
// document
$(document).ready(function () {
    semantiUIInit();

    // Managing modal on home page displaying data storage information
    var enter_button = document.getElementById("enter_button");
    var homepage_modal = document.getElementById("initial_zero_modal");

    // if ($.cookie('pop') == null) {
    //      homepage_modal.style.display = "block";
    //      $.cookie('pop', '1');
    //  }

    // homepage_modal.style.display = "block";

    enter_button.onclick = function() {
      homepage_modal.style.display = "none";
    }

    // Creating click function for advanced search parameters
    $(".collapseHeader").click(function () {
        $collapseHeader = $(this);
        //getting the next element
        $collapseContent = $collapseHeader.next();
        //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
        $collapseContent.slideToggle(500, function () {});

    });

    $("#include").change(function () {
        var title = $('#question_title').children('div').text()
        if (title == 'Lab Tests') {
            // This is a measurement
            $('#time_container').hide();
            if ($('#include').val() == 'INC') {
                $('#value_input_container').show();

            } else {
                $('#value_input_container').hide();
            }
        } else {
            $('#value_input_container').hide();
            if ($('#include').val() == 'INC') {
                $('#time_container').show();

            } else {
                $('#time_container').hide();
            }
        }
    });

    // search
    $('#search_button').bind('click',
        function () {
            $.blockUI({
                message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
                css: {
                    border: 'none',
                    '-webkit-border-radius': '40px',
                    '-moz-border-radius': '40px',
                    opacity: .5,
                },
            });

            // input_term = $('#first_focus').val();
            let input_locn = $('#location_terms').val();
            let input_range = $('#nearby_miles').val();
            let trial_type = $('#trial_type').val();
            let active_restriction = $('#active_trial_restriction').is(':checked');
            let keyword_search = $('#keyword_search_terms').val();
            console.log('input location: ' + input_locn);
            console.log('input mile range: ' + input_range);
            console.log('input keyword: ' + keyword_search);

            var vz = false;
            $.getJSON($SCRIPT_ROOT + '/_check_homepage_parameters', {
                    locn: input_locn,
                    miles: input_range,
                    keyword: keyword_search,
                    trial_type: trial_type,
                    active_restriction: active_restriction
                },
                function (data) {
                    vz = data.valid_zip;
                    zct = data.nearby_length;
                    kct = data.keyword_length;
                    tct = data.type_length;
                    wct = data.working_nct_length;
                })

                .done(function() {
                    console.log('is zip valid: ' + vz);
                    console.log('nearby length: ' + zct);
                    console.log('klength: ' + kct);
                    console.log('tlength: ' + tct);
                    console.log('wlength: ' + wct);
                    if (wct > 0) {
                        search("regular");
                        $('#filter_results_container').hide();
                        $('#question_container').hide();
                        $('#hm_blurb_container').hide();
                        $('#logo_div').hide();
                        $('#acknow_div').hide();
                        $('#ctgov_data_div').hide();
                        $('#results_container').show();
                        $('#multiquestions_container').show();
                        $('#search_form_container').hide();
                        $('#dash_board').hide();
                        $('#search_results_container').show();
                        $(document).scrollTop(0);
                    } else {
                        let err_string = '';
                        if (vz == false) {
                            err_string = 'Please enter a valid zip code and mile range (must be a number) and search again!';
                        } else if (kct == 0) {
                            err_string = 'No trials found fitting your search parameters, possibly because of your keyword ' +
                                'search. Please check your keyword(s) for typos or consider expanding your search radius ' +
                                'and try again!';
                        } else if (tct == 0) {
                            err_string = 'No trials found fitting your search parameters. Please check the trial type you ' +
                                'selected and try again!';
                        } else if (zct == 0) {
                            err_string = 'No trials found within ' + input_range + ' miles of your zip code. Please expand your ' +
                                'mile range or update your zip code and search again!';
                        } else {
                            err_string = 'No trials found fitting your search parameters. Please consider updating your ' +
                                'search parameters or expanding your search radius and try again!';
                        }
                        document.getElementById("initial_zero_message").innerHTML = err_string;
                        document.getElementById("initial_zero_modal").style.display = 'block';
                    }


                    // if (vz == false) {
                    //     alert('Please enter a valid Zip Code and Mile Range (must be a number) to begin searching for clinical trials in your area!');
                    // } else if (klist[0] == 'Error') {
                    //     alert('No trials returned for entered keyword(s), please update your search!');
                    // } else {
                    //     search("regular");
                    //     $('#filter_results_container').hide();
                    //     $('#question_container').hide();
                    //     $('#hm_blurb_container').hide();
                    //     $('#logo_div').hide();
                    //     $('#acknow_div').hide();
                    //     $('#ctgov_data_div').hide();
                    //     $('#results_container').show();
                    //     $('#multiquestions_container').show();
                    //     $('#search_form_container').hide();
                    //     $('#dash_board').hide();
                    //     $('#search_results_container').show();
                    //     $(document).scrollTop(0);
                    // }
                });

        });

    $('#first_focus').keypress(
        function (e) {
            if (e.keyCode == 13) {
                $('.results .transition .visible').hide();
                input_term = $('#first_focus').val()
                if (!input_term | input_term === '') {
                    alert('Please enter a term!');
                } else {
                    search("regular");
                    $('#filter_results_container').hide();
                    $('#question_container').hide();
                    $('#results_container').show();
                    $('#search_form_container').hide();
                    $('#dash_board').hide();
                    $('#search_results_container').show();
                    $(document).scrollTop(0);
                }
                return false
            }
        });

    // // advanced search
    // $('#advsearch_button').click(function () {
    //     var input = $('#search_text').val();
    //     $('#search_form_container').hide();
    //     $('#question_container').hide();
    //     $('#results_container').hide();
    //     $('#search_results_container').hide();
    //     $('#filter_results_container').hide();
    //     $('#adv_search_container').show();
    //
    //
    // });

    // $('#search_advs').click(function () {
    //     search("advanced");
    //     $('#adv_search_container').hide();
    //     $('#search_form_container').show();
    //     $('#question_container').hide();
    //     $('#results_container').show();
    //     $('#search_results_container').show();
    //     $('#filter_results_container').hide();
    //     $(document).scrollTop(0);
    //     $('#dash_board').hide();
    //
    // });

    $('#search_text').keypress(
        function (e) {
            if (e.keyCode == 13) {
                return false
            }
        });

    // // close advanced search form and return
    // $('#back_button').click(function () {
    //     $('#adv_search_container').hide();
    //     $('#question_container').hide();
    //     $('#results_container').hide();
    //     $('#search_results_container').hide();
    //     $('#filter_results_container').hide();
    //     $('#search_form_container').show();
    // });

    $("#close_question").click(function () {
        console.log('catching click on close question')
        let modal = document.getElementById("close_modal_qform");
        modal.style.display = "block";
    });
    $("#close_modal").modal({
        closable: true
    });
    $("#found_no_modal").modal({
        closable: true
    });
    $("#show_trials").click(function () {
        if ($(this).attr('show') == 'yes') {
            $('#filter_results').show();
            $(this).text('Hide Eligible Trials')
            $(this).attr('show', 'no');
        } else {
            $('#filter_results').hide();
            $(this).text('Show Eligible Trials')
            $(this).attr('show', 'yes');
        }

    });
    // $('#show_trials').click(function(){
    //     $('#filter_results').show();
    // });

    // close question container
    $('#confirm_close_question').bind('click',
        // window.location.href = 'newPage.html';
        function () {
            window.location.href = '/';
            // $("#close_modal_qform").modal('hide');
        });

    $('#reject_close_question').bind('click',
        // window.location.href = 'newPage.html';
        function () {
        let modal = document.getElementById("close_modal_qform");
        modal.style.display = "none";
        });

    $('#confirm_close_modal').bind('click',
        // window.location.href = 'newPage.html';
        function () {
            window.location.href = '/';
            // $("#found_no_modal").modal('hide');
        });

    $('#pre_questions_domain').on('change', function() {
      if ( this.value == 'yes')
      {
        $("#pre_time_container").show();
      }
      else
      {
        $("#pre_time_container").hide();
      }
    });

    // function () {
    //     $('#question_tags').empty();
    //     $("#question_form").empty();
    //     $('#question_number').empty();
    //     $('#question_title').empty();
    //     $("#answered_questions").empty();
    //     $("#qa_title").prop("checked", false);
    //     $("#qa_title_checkbox").hide();
    //     $("#answered_questions_container").hide();


    //     $('#question_container').hide();
    //     $('#results_container').show();
    //     $('#search_results_container').show();
    //     $('#filter_results_container').hide();
    //     $('#search_form_container').show();
    //     semantiUIInit(); // refresh table.

    //     $.blockUI({
    //         message: '<div class="ui segment"><div class="ui active dimmer">Loading...<div class="ui text loader"></div></div></div>',
    //         css: {
    //             border: 'none',
    //             '-webkit-border-radius': '40px',
    //             '-moz-border-radius': '40px',
    //             opacity: .5,
    //         },
    //     });
    //     $.getJSON($SCRIPT_ROOT + '/_clean', function (data) {
    //         $(document).scrollTop(0);
    //     });
    // });

    // Generating variables and scripts for trial information modal - on_click function defined above
    var modal = document.getElementById("myModal");
    var span = document.getElementsByClassName("close")[0];

    $(document).on("click", "a.trial_listing_header" , function() {
        input_nct = $(this).attr('name');
        console.log('registered click: ' + input_nct)
        generate_trial_info_modal(input_nct);
        return false;
    });

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      modal.style.display = "none";
      // $('#tabs-lo').empty();
      // $('.location_block').remove();
        reset_info_modal();
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
        // $('#tabs-lo').empty();
        // $('.location_block').remove();
          reset_info_modal();
      }
    }

    //handling tabs - from jQuery website
    $( function() {
        $( "#tabs" ).tabs();

      });

    $("#close_question").click(function () {
        alert('button worked');
    });
});
$(document).ajaxStop($.unblockUI);
