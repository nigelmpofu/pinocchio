from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from peer_review.decorators.adminRequired import admin_required

from ..models import Question, Questionnaire, RoundDetail, QuestionOrder, User, TeamDetail, QuestionGrouping, Label

import json

# Render the questionnaireAdmin template
@admin_required
def questionnaire_admin(request):
    context = {'questions': Question.objects.all(),
               'questionnaires': get_questionnaires(request),
               'questgrouping': QuestionGrouping.objects.all()}
    return render(request, 'peer_review/questionnaireAdmin.html', context)


@admin_required
def questionnaire_preview(request, questionnaire_pk):
    alice = User(title='Miss', initials='A', name='Alice', surname='Test', user_id='Alice')
    bob = User(title='Mr', initials='B', name='Bob', surname='Test', user_id='Bob')
    carol = User(title='Miss', initials='C', name='Carol', surname='Test', user_id='Carol')
    
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_pk)

    #q_orders = get_object_or_404(QuestionOrder, questionnaire=questionnaire)
    q_orders = QuestionOrder.objects.filter(questionnaire=questionnaire)
    q_labels = []
    for ind, qord in enumerate(q_orders):
        if qord.questionGrouping == QuestionGrouping.objects.get(grouping="Label"):
            q_labels.append(Label.objects.filter(questionOrder=qord))

    
    mock_round = RoundDetail(name='Preview Round', questionnaire=questionnaire, description='This is a preview round')
    
    team_name = 'Preview'
    TeamDetail(user=alice, roundDetail=mock_round, teamName=team_name)
    TeamDetail(user=bob, roundDetail=mock_round, teamName=team_name)
    TeamDetail(user=carol, roundDetail=mock_round, teamName=team_name)
    
    q_team = [alice, bob, carol]
    context = {'questionOrders': q_orders, 'questionLabels': q_labels,
               'teamMembers': q_team,
               'questionnaire': questionnaire,
               'currentUser': alice,
               'round': 0,
               'preview': 1}
    return render(request, 'peer_review/questionnaire.html', context)

# Returns the QuestionOrder record that a question is stored in
def get_qord(qordLst, queId):
    rtnInd = -1
    for ind in range(0, len(qordLst)):
        if qordLst[ind].question == Question.objects.get(pk=queId):
            rtnInd = ind
            break

    if rtnInd == -1:
        return None # Error
    else:
        return qordLst[rtnInd]


# Save a questionnaire
@admin_required
def save_questionnaire(request):
    if request.method == 'POST':
        intro = request.POST.get("intro")
        title = request.POST.get("title")
        questions = str(request.POST.get('questions')).split(";#")
        groupings = str(request.POST.get('qgrouping')).split(";#")
        qlabels = json.loads(request.POST.get('question-labels'))
        if 'pk' in request.POST:
            q = get_object_or_404(Questionnaire, pk=request.POST.get("pk"))
            QuestionOrder.objects.filter(questionnaire=q).delete()
            q.intro = intro
            q.label = title
            q.save()
        elif Questionnaire.objects.filter(label=title).exists():
            messages.add_message(request, messages.WARNING, "Error: A question with that title already exists.")
            return HttpResponseRedirect('/questionnaireAdmin')
        else:
            q = Questionnaire.objects.create(intro=intro, label=title)

        questionOrdersLst = []
        for index, question in enumerate(questions):
            if question.isdigit(): 
                qordtmp = QuestionOrder.objects.create(questionnaire=q,
                                             question=get_object_or_404(Question, pk=question),
                                             questionGrouping=QuestionGrouping.objects.get(grouping=groupings[index]),
                                             order=index)
                if qordtmp.questionGrouping == QuestionGrouping.objects.get(grouping="Label"):
                    questionOrdersLst.append(qordtmp)

        
        labells = []
        for indx in range(0, len(qlabels)): 
            tmpjsn = json.dumps(qlabels[int(indx)])
            curjsn = json.loads(str(tmpjsn))
            labels = str(curjsn['questionLabel']).split(";#")
            for lable in labels: 
                qord = get_qord(questionOrdersLst, curjsn['questionId'])
                if qord is not None:
                    Label.objects.create(questionOrder=qord, labelText=lable)
                else:
                    Questionnaire.objects.get(pk=q.pk).delete()
                    messages.add_message(request, messages.WARNING, "Error: Questionnaire could not be created.")
                    return HttpResponseRedirect('/questionnaireAdmin')


        messages.add_message(request, messages.SUCCESS, "Questionnaire saved successfully.")
    return HttpResponseRedirect('/questionnaireAdmin')

# Create JSON object from a label query set
def jsonify_labels(qlst, qids):
    rtn = []
    temprtn = {}
    labls = []
    for elem in qlst:
        for labl in elem:
            labls.append(labl.labelText)
        temprtn['questionId'] = qids.pop().pk
        temprtn['questionLabel'] = labls
        rtn.append(json.dumps(temprtn))
        temprtn = {}
        labls = []
    return str(json.dumps(rtn))


# Render the questionnaireAdmin template with the questionnaires details filled in
@admin_required
def edit_questionnaire(request, questionnaire_pk):
    current_questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_pk)
    q_labels = []
    q_ids = []
    for ind, qord in enumerate(QuestionOrder.objects.filter(questionnaire=current_questionnaire)):
        if qord.questionGrouping == QuestionGrouping.objects.get(grouping="Label"):
            q_labels.append(Label.objects.filter(questionOrder=qord))
            q_ids.append(get_object_or_404(Question, pk=qord.question.pk))

    q_ids.reverse()
    context = {'questions': Question.objects.all(),
               'questionnaires': get_questionnaires(request),
               'questionnaire': current_questionnaire,
               'questionOrders': QuestionOrder.objects.filter(
                   questionnaire=current_questionnaire),
               'questgrouping': QuestionGrouping.objects.all(),
               'inARound': RoundDetail.objects.filter(questionnaire=current_questionnaire).exists(),
               'questionLabels': jsonify_labels(q_labels, q_ids)}
    return render(request, 'peer_review/questionnaireAdmin.html', context)


# Delete a questionnaire
@admin_required
def delete_questionnaire(request):
    if request.method == "POST":
        pks = request.POST['pk'].split(';#')
        for pk in pks:
            if str(pk).isdigit():
                get_object_or_404(Questionnaire, pk=pk).delete()
            else:
                messages.add_message(request, messages.WARNING,
                                     "Error: Something went wrong when deleting the questionnaire")
                return HttpResponseRedirect('/questionnaireAdmin')
        rtnStr = str(len(pks)) + " questionnaire(s)"
        if len(pks) > 1:
            rtnStr = str(len(pks)) + " questionnaires"
        else:
            rtnStr = "Questionnaire"
        messages.add_message(request, messages.SUCCESS, rtnStr + " deleted successfully")
        return HttpResponseRedirect('/questionnaireAdmin')
    else:
        return HttpResponseRedirect('/questionnaireAdmin')


# Return a dict with all the questionnaires, including whether each one is contained in a round
@admin_required
def get_questionnaires(request):
    response = []
    for questionnaire in Questionnaire.objects.all():
        response.append({'title': questionnaire.label,
                         'intro': questionnaire.intro,
                         'pk': questionnaire.pk,
                         'inARound': RoundDetail.objects.filter(questionnaire=questionnaire).exists(),
                         'questionCount': str(QuestionOrder.objects.filter(questionnaire=questionnaire).count())
                         })
    return response

# Checks if a questionnaire with the same title already exists
@admin_required
def check_questionnaire(request):
    if request.method == "POST":
        title = request.POST.get("title")
        if Questionnaire.objects.filter(label=title).exists():
            return JsonResponse({'result': 1})
        else:
            return JsonResponse({'result': 0})
