from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from .models import pmmasterlist, equiplist, controlformlist, pmmasterlist_temp, \
    pmsheetdb, pm_sch, pmchecksheet, pm_reference, pm_manual, userinfo, workorder, approval_information, \
    spare_parts_list, spare_in, spare_out, parts_pm
from django.contrib import messages
import datetime as date
from django.core.mail import send_mail, EmailMessage
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Sum
import re
#import pyzbar.pyzbar as pyzbar ##바코드 리더기
#import cv2 ##바코드 리더기
#import barcode ##바코드 생성기
#from barcode.writer import ImageWriter ##바코드 생성기

# Create your views here.

##############################################################################################################
#################################################로그인페이지###################################################
##############################################################################################################

def login(request):
    return render(request, 'login.html') #templates 내 html연결

def auditrail_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        return render(request, 'auditrail_main.html') #templates 내 html연결

def logout_page(request):
    return render(request, 'logout_page.html') #templates 내 html연결

def login_again(request):
    return render(request, 'login_again.html') #templates 내 html연결

def information_main(request):
    return render(request, 'information_main.html') #templates 내 html연결

def main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        userpassword = request.POST.get('pw')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        try:
            users = userinfo.objects.get(userid=loginid)
            username = users.username
            userteam = users.userteam
            password = users.password
            auth = users.auth1
            user_div = users.user_division
            users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        except:
            users={"loginid":loginid}
        try:
            login_info = userinfo.objects.get(userid=loginid) #아이디 일치여부 확인
            if login_info.password == userpassword: #비밀번호 일치여부 확인
#####메인테이블 창 만들기####
                #####1)PM창 카운트 계산하기####
                today = date.datetime.today()
                today_search = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
                month_search = "20" + today.strftime('%y') + "-" + today.strftime('%m')
                try:
                    today_info = pm_sch.objects.filter(plandate=today_search).values('team').annotate(Count('team'))
                except:
                    today_info =""
                try:
                    completed = pm_sch.objects.filter(date=month_search, status="Complete")
                    completed = completed.values('status')
                    df_completed = pd.DataFrame.from_records(completed)
                    completed_len = len(df_completed.index)
                except:
                    completed_len = 0
                try:
                    reviewed = pm_sch.objects.filter(date=month_search, status="Reviewed")
                    reviewed = reviewed.values('status')
                    df_reviewed = pd.DataFrame.from_records(reviewed)
                    reviewed_len = len(df_reviewed.index)
                except:
                    reviewed_len = 0
                try:
                    performed = pm_sch.objects.filter(date=month_search, status="Performed")
                    performed = performed.values('status')
                    df_performed = pd.DataFrame.from_records(performed)
                    performed_len = len(df_performed.index)
                except:
                    performed_len = 0
                try:
                    fixed_date = pm_sch.objects.filter(date=month_search, status="Fixed Date")
                    fixed_date = fixed_date.values('status')
                    df_fixed_date = pd.DataFrame.from_records(fixed_date)
                    fixed_date_len = len(df_fixed_date.index)
                except:
                    fixed_date_len = 0
                total_len = int(completed_len) + int(reviewed_len) + int(performed_len) + int(fixed_date_len)
                pm_cont = {"total_len": total_len, "completed_len": completed_len, "reviewed_len": reviewed_len,
                           "performed_len": performed_len, "fixed_date_len": fixed_date_len, "today_info": today_info}
                pm_cont.update(users)
            #####2)PM문서창 카운트 계산하기####
                try: ###ra
                    ra_completed = equiplist.objects.filter(status="Complete")
                    ra_completed = ra_completed.values('status')
                    df_ra_completed = pd.DataFrame.from_records(ra_completed)
                    ra_completed_len = len(df_ra_completed.index)
                except:
                    ra_completed_len = 0
                try:
                    ra_prepared = equiplist.objects.filter(status="Prepared")
                    ra_prepared = ra_prepared.values('status')
                    df_ra_prepared = pd.DataFrame.from_records(ra_prepared)
                    ra_prepared_len = len(df_ra_prepared.index)
                except:
                    ra_prepared_len = 0
                try:
                    new = pm_sch.objects.filter(date=month_search, status="New")
                    new = new.values('status')
                    df_new = pd.DataFrame.from_records(new)
                    ra_new_len = len(df_new.index)
                except:
                    ra_new_len = 0
                ra_total_len = int(ra_completed_len) + int(ra_prepared_len) + int(ra_new_len)
                pm_ra_cont = {"ra_total_len": ra_total_len, "ra_completed_len": ra_completed_len,
                              "ra_prepared_len": ra_prepared_len,
                              "ra_new_len": ra_new_len}
                pm_ra_cont.update(pm_cont)
                try: ###control form
                    cf_completed = controlformlist.objects.filter(status="Complete", recent_y="Y")
                    cf_completed = cf_completed.values('status')
                    df_cf_completed = pd.DataFrame.from_records(cf_completed)
                    cf_completed_len = len(df_cf_completed.index)
                except:
                    cf_completed_len = 0
                try:
                    cf_reviewed = controlformlist.objects.filter(status="Reviewed", recent_y="A")
                    cf_reviewed = cf_reviewed.values('status')
                    df_cf_reviewed = pd.DataFrame.from_records(cf_reviewed)
                    cf_reviewed_len = len(df_cf_reviewed.index)
                except:
                    cf_reviewed_len = 0
                try:
                    cf_prepared = controlformlist.objects.filter(status="Prepared", recent_y="A")
                    cf_prepared = cf_prepared.values('status')
                    df_cf_prepared = pd.DataFrame.from_records(cf_prepared)
                    cf_prepared_len = len(df_cf_prepared.index)
                except:
                    cf_prepared_len = 0
                try:
                    cf_reject = controlformlist.objects.filter(status="Reject", recent_y="Y")
                    cf_reject = cf_reject.values('status')
                    df_cf_reject = pd.DataFrame.from_records(cf_reject)
                    cf_reject_len = len(df_cf_reject.index)
                except:
                    cf_reject_len = 0
                try:
                    cf_new = controlformlist.objects.filter(status="New", recent_y="Y")
                    cf_new = cf_new.values('status')
                    df_cf_new = pd.DataFrame.from_records(cf_new)
                    cf_new_len = len(df_cf_new.index)
                except:
                    cf_new_len = 0
                try:
                    cf_review = controlformlist.objects.filter(status="Review", recent_y="Y")
                    cf_review = cf_review.values('status')
                    df_cf_review = pd.DataFrame.from_records(cf_review)
                    cf_review_len = len(df_cf_review.index)
                except:
                    cf_new_len = 0
                cf_total_len = int(cf_completed_len) + int(cf_reject_len) + int(cf_new_len) + int(cf_prepared_len) + int(cf_reviewed_len) + int(cf_review_len)
                pm_cf_cont = {"cf_total_len": cf_total_len, "cf_completed_len": cf_completed_len,
                              "cf_reject_len": cf_reject_len,"cf_prepared_len":cf_prepared_len,"cf_reviewed_len":cf_reviewed_len,
                              "cf_new_len": cf_new_len}
                pm_cf_cont.update(pm_ra_cont)
            ####3)BM문서창 카운트 계산하기####
                today = date.datetime.today()##오늘 결과
                today_search = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
                try:
                    bm_today_info = workorder.objects.filter(date=today_search).values('team').annotate(Count('team'))
                except:
                    bm_today_info =""
                try:
                    bm_finish_info = workorder.objects.filter(action_date=today_search).values('team').annotate(Count('team'))
                except:
                    bm_finish_info = ""
                bm_today_cont = {"bm_today_info":bm_today_info,"bm_finish_info":bm_finish_info}
                bm_today_cont.update(pm_cf_cont)
                try:##bm 현재 status
                    wr_approve = workorder.objects.filter(status="Approved", workorder_y_n="N")
                    wr_approve = wr_approve.values('status')
                    df_wr_approve = pd.DataFrame.from_records(wr_approve)
                    wr_approve_len = len(df_wr_approve.index)
                except:
                    wr_approve_len = 0
                try:
                    wr_receive = workorder.objects.filter(status="Received", workorder_y_n="N")
                    wr_receive = wr_receive.values('status')
                    df_wr_receive = pd.DataFrame.from_records(wr_receive)
                    wr_receive_len = len(df_wr_receive.index)
                except:
                    wr_receive_len = 0
                try:
                    wr_review = workorder.objects.filter(status="Reviewed", workorder_y_n="N")
                    wr_review = wr_review.values('status')
                    df_wr_review = pd.DataFrame.from_records(wr_review)
                    wr_review_len = len(df_wr_review.index)
                except:
                    wr_review_len = 0
                try:
                    wr_request = workorder.objects.filter(status="Request", workorder_y_n="N")
                    wr_request = wr_request.values('status')
                    df_wr_request = pd.DataFrame.from_records(wr_request)
                    wr_request_len = len(df_wr_request.index)
                except:
                    wr_request_len = 0
                try:
                    wr_team = workorder.objects.filter(status="Team_approved", workorder_y_n="N")
                    wr_team = wr_team.values('status')
                    df_wr_team = pd.DataFrame.from_records(wr_team)
                    wr_team_len = len(df_wr_team.index)
                except:
                    wr_team_len = 0
                try:
                    wr_total = workorder.objects.filter(workorder_y_n="N")
                    wr_total = wr_total.values('status')
                    df_wr_total = pd.DataFrame.from_records(wr_total)
                    wr_total_len = len(df_wr_total.index)
                except:
                    wr_total_len = 0
                not_receive = int(wr_request_len) + int(wr_team_len)
                receive = int(wr_receive_len) + int(wr_review_len)
                request_cont = {"wr_approve_len":wr_approve_len,"wr_receive_len":wr_receive_len,"wr_review_len":wr_review_len,
                                "wr_team_len":wr_team_len,"wr_total_len":wr_total_len,"wr_request_len":wr_request_len,
                                "receive":receive,"not_receive":not_receive}
                request_cont.update(bm_today_cont)
                try:  ##bm 현재 status
                    wo_approve = workorder.objects.filter(workorder_y_n="C")
                    wo_approve = wo_approve.values('status')
                    df_wo_approve = pd.DataFrame.from_records(wo_approve)
                    wo_approve_len = len(df_wo_approve.index)
                except:
                    wo_approve_len = 0
                try:
                    wo_repair = workorder.objects.filter(status="Repaired", workorder_y_n="Y")
                    wo_repair = wo_repair.values('status')
                    df_wo_repair = pd.DataFrame.from_records(wo_repair)
                    wo_repair_len = len(df_wo_repair.index)
                except:
                    wo_repair_len = 0
                try:
                    wo_review = workorder.objects.filter(status="Reviewed", workorder_y_n="Y")
                    wo_review = wo_review.values('status')
                    df_wo_review = pd.DataFrame.from_records(wo_review)
                    wo_review_len = len(df_wo_review.index)
                except:
                    wo_review_len = 0
                try:
                    wo_check = workorder.objects.filter(status="Checked", workorder_y_n="Y")
                    wo_check = wo_check.values('status')
                    df_wo_check = pd.DataFrame.from_records(wo_check)
                    wo_check_len = len(df_wo_check.index)
                except:
                    wo_check_len = 0
                try:
                    wo_total = workorder.objects.filter(Q(workorder_y_n="Y") | Q(workorder_y_n="C"))
                    wo_total = wo_total.values('status')
                    df_wo_total = pd.DataFrame.from_records(wo_total)
                    wo_total_len = len(df_wo_total.index)
                except:
                    wo_total_len = 0
                repaired = int(wo_repair_len) + int(wo_review_len) + int(wo_check_len)
                wo_not_len = int(wo_total_len) - int(wo_repair_len) - int(wo_approve_len) - int(wo_review_len) - int(wo_check_len)
                order_cont = {"wo_not_len": wo_not_len, "wo_repair_len": wo_repair_len, "wo_approve_len": wo_approve_len,
                                "wo_total_len": wo_total_len,"repaired":repaired,"wo_review_len":wo_review_len,
                              "wo_check_len":wo_check_len}
                order_cont.update(request_cont)
                context = {"loginid": loginid}
                context.update(order_cont)
                return render(request, 'main.html', context)  # templates 내 html연결
            else:
                messages.error(request, "The password does not match.")  # 경고
                return render(request, 'login.html')  # templates 내 html연결
        except:
            messages.error(request, "There is no such ID information.")  # 경고
            return render(request, 'login.html')  # templates 내 html연결

#######################
####PM Check Sheet ####
#######################
def pmchecksheet_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        pmmasterlists = pmmasterlist.objects.all().order_by('team','controlno') #db
    ####테이블 감추기 신호####
        table_signal = "table_signal"
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
#################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y", status__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y", team__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y", pmsheetno__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y", name__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) =="None":
                searchtext=""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y", status__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y", team__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y", pmsheetno__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y", name__icontains=searchtext).order_by('team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) =="None":
                searchtext=""
        context = {"pmmasterlists":pmmasterlists,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch, "table_signal":table_signal,
                   "calendarsearch":calendarsearch,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmchecksheet_main.html', context) #templates 내 html연결

def pmchecksheet_write(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####PM CHECK SHEET DB로 보내기#####
        pmchecksheet_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        check = [pmchecksheet_check.pmchecksheet_y_n][0]
        if check == "N":
        #####pm_sch db에 있는 항목 보내기#####
            pmchecksheet_date_insert = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            date_insert = [pmchecksheet_date_insert.date][0]
            pmcode_insert = [pmchecksheet_date_insert.pmcode][0]
        #####pmmasterlist db에 있는 항목 보내기#####
            pmchecksheet_insert = pmmasterlist.objects.filter(sheetno=pmsheetno, pm_y_n="Y", amd="A")  # 컨트롤넘버 일치되는 값 찾기
            pmchecksheet_insert = pmchecksheet_insert.values('itemcode')
            df_pmchecksheet_insert = pd.DataFrame.from_records(pmchecksheet_insert)
            df_pmchecksheet_insert_len = len(df_pmchecksheet_insert.index)  # itemcode 하나씩 넘기기
            for j in range(df_pmchecksheet_insert_len):
                itemcode_insert = df_pmchecksheet_insert.iat[j, 0]
                pmchecksheet_get = pmmasterlist.objects.get(itemcode = itemcode_insert, pm_y_n="Y")
                pmchecksheet(
                    team=pmchecksheet_get.team,
                    controlno=pmchecksheet_get.controlno,
                    pmsheetno=pmsheetno,
                    date=date_insert,
                    pmcode=pmcode_insert,
                    itemcode=pmchecksheet_get.itemcode,
                    item=pmchecksheet_get.item,
                    check=pmchecksheet_get.check,
                ).save()
    #####pm_sch db에 반영완료 체크하기#####
            pmchecksheet_y_n_insert = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            pmchecksheet_y_n_insert.pmchecksheet_y_n = "Y"
            pmchecksheet_y_n_insert.save()
    #####승인요청여부 확인하기#####
        comp_signal_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        comp_signal_check = comp_signal_check.status
        if comp_signal_check != "Fixed Date":
            comp_signal = "Y"
        else:
            comp_signal = "N"
#################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo=equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,"url_comp":url_comp,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode": pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info, "comp_signal":comp_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
    return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_checkresult(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        checkresult = request.POST.get('checkresultreturn')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.result_temp = checkresult
        pmchecksheet_write.save()
#################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode = pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode":pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_actiondetail(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        actiondetail = request.POST.get('actiondetailreturn')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
        pass_y = request.POST.get('pass_y')  # html 날짜 값을 받는다
        fail_y = request.POST.get('fail_y')  # html 날짜 값을 받는다
        fail_n = request.POST.get('fail_n')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        password = users.password
        userteam = users.userteam
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.actiondetail_temp = actiondetail
        pmchecksheet_write.pass_y_temp = pass_y
        pmchecksheet_write.fail_y_temp = fail_y
        pmchecksheet_write.fail_n_temp = fail_n
        pmchecksheet_write.save()
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode = pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode":pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_checkboxform(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        pass_y = request.POST.get('pass_y')  # html 날짜 값을 받는다
        fail_y = request.POST.get('fail_y')  # html 날짜 값을 받는다
        fail_n = request.POST.get('fail_n')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.pass_y_temp = pass_y
        pmchecksheet_write.fail_y_temp = fail_y
        pmchecksheet_write.fail_n_temp = fail_n
        pmchecksheet_write.save()
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode = pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode": pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_remark(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        remarkreturn = request.POST.get('remarkreturn')  # html 날짜 값을 받는다
        remark_na = request.POST.get('remark_na')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####리마크 입력시에 입력#####
        pmchecksheet_remark = pm_sch.objects.get(pmcode=pmcode)
        pmchecksheet_remark.remark_temp = remarkreturn
        pmchecksheet_remark.remark_na_temp = remark_na
        pmchecksheet_remark.save()
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode = pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode":pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_remark_na(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####리마크 입력시에 입력#####
        pmchecksheet_remark = pm_sch.objects.get(pmcode=pmcode)
        pmchecksheet_remark.remark_temp = "N/A"
        pmchecksheet_remark.remark_na_temp = "checked"
        pmchecksheet_remark.save()
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode = pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                   "pmcode":pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결

def pmchecksheet_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####완료 시그널 주기#####
        pm_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if pm_comp.status == "Complete":
            comp_signal = "Y"
        else:
            comp_signal = "N"
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach == "N/A":
            url_comp = "N"
        elif str(url_comp.attach) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
#################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmmasterlist.objects.filter(sheetno = pmsheetno, pm_y_n="Y", amd="A")
        pmchecksheet_result = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,"url_comp":url_comp,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "pmchecksheet_result":pmchecksheet_result,
                    "comp_signal":comp_signal,"calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext
                    , "spare_list": spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_main.html', context) #templates 내 html연결

def pmcheck_workrequest_up(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        capa = request.POST.get('capa')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        requestor = request.POST.get('requestor')  # html 날짜 값을 받는다
        equipteam = request.POST.get('team')  # html에서 해당 값을 받는다
        description = request.POST.get('description')  # html 날짜 값을 받는다
        date = request.POST.get('date')  # html 날짜 값을 받는다
        equipname = request.POST.get('equipname')  # html 날짜 값을 받는다
        roomname = request.POST.get('roomname')  # html에서 해당 값을 받는다
        roomno = request.POST.get('roomno')  # html 날짜 값을 받는다
        description_info = request.POST.get('description_info')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
 #################파일업로드하기##################
        if "upload_file" in request.FILES:
                # 파일 업로드 하기!!!
           upload_file = request.FILES["upload_file"]
           fs = FileSystemStorage()
           name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
                    # 파일 읽어오기!!!
           url = fs.url(name)
        else:
            file_name = "-"
    #####첨부파일 시그널 주기#####
        url_comp = "Y"
        context = {"loginid":loginid,"equipname":equipname,"equipteam":equipteam,"capa":capa,
                    "description":description,"description_info":description_info,
                    "controlno":controlno,"roomno":roomno,"roomname":roomname,"url_comp":url_comp,
                     "url":url,"requestor":requestor,"date":date}
        context.update(users)
        return render(request, 'pmchecksheet_workrequest.html', context) #templates 내 html연결

def pmcheck_workrequest_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        capa = request.POST.get('capa')  # html 날짜 값을 받는다
        pmcode= request.POST.get('pmcode')  # html에서 해당 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        requestor = request.POST.get('requestor')  # html 날짜 값을 받는다
        equipteam = request.POST.get('team')  # html에서 해당 값을 받는다
        description = request.POST.get('description')  # html 날짜 값을 받는다
        request_date = request.POST.get('date')  # html 날짜 값을 받는다
        equipname = request.POST.get('equipname')  # html 날짜 값을 받는다
        roomname = request.POST.get('roomname')  # html에서 해당 값을 받는다
        roomno = request.POST.get('roomno')  # html 날짜 값을 받는다
        description_info = request.POST.get('description_info')  # html 날짜 값을 받는다
        url = request.POST.get('url')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam}
    ##workodrerno생성
        today = date.datetime.today()
        date_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        workorder_date = today.strftime('%y') + today.strftime('%m') + today.strftime('%d')
        workorder_count = workorder.objects.filter(date=date_check)
        workorder_count = workorder_count.values('date')
        df_workorder_count = pd.DataFrame.from_records(workorder_count)
        df_workorder_count_len = len(df_workorder_count.index)  # itemcode 하나씩 넘기기
        workorderno_no = int(df_workorder_count_len) + 1
        workorderno = workorder_date + "/" + equipteam + "/" + str(workorderno_no)
    ##미입력칸 확인하기##
        if description !="":
            if description_info !="":
            ##체크시트에 workorder no저장하기##
                workorderno_save = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
                workorderno_save.workrequest_temp = workorderno
                workorderno_save.save()
            ##db저장하기##
                workorder(
                    type="PM",
                    capa=capa,
                    requestor=username,
                    team=equipteam,
                    controlno=controlno,
                    description=description,
                    date=request_date,
                    status="Request",
                    equipname=equipname,
                    roomname=roomname,
                    roomno=roomno,
                    workorderno=workorderno,
                    description_info=description_info,
                    r_attach=url,
                    req_date="N/A",
                    req_reason="N/A"
                ).save()
                ##해당팀장에 메일보내기##

                context = {"loginid": loginid, "equipname": equipname, "equipteam": equipteam, "capa": capa,
                            "description": description, "description_info": description_info,
                            "controlno": controlno, "roomno": roomno, "roomname": roomname,
                            "url": url, "requestor": requestor, "request_date": request_date}
                context.update(users)
                return render(request, 'pmchecksheet_workrequest_comp.html', context)  # templates 내 html연결
    ##입력칸 미 입력 시##
        if url == "":
            url_comp = "N"
        else:
            url_comp = "Y"
        messages.error(request, "There are entries not entered.")
        context = {"loginid": loginid, "equipname": equipname, "equipteam": equipteam, "capa": capa,
               "description": description, "description_info": description_info,"url_comp":url_comp,
               "controlno": controlno, "roomno": roomno, "roomname": roomname,
               "url": url, "requestor": requestor, "date": date}
        context.update(users)
        return render(request, 'pmchecksheet_workrequest.html', context)  # templates 내 html연결

def pmchecksheet_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####체크박스 수량 일치확인#####
        total_count = pmchecksheet.objects.filter(pmcode=pmcode)
        total_count = total_count.values('item')
        df_total_count = pd.DataFrame.from_records(total_count)
        total_len = len(df_total_count.index)
        pmcheckitem_count = pmchecksheet.objects.filter(pmcode=pmcode)
        pmcheckitem_count = pmcheckitem_count.values()
        df_pmcheckitem_count = pd.DataFrame.from_records(pmcheckitem_count)
        df_pass_y_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['pass_y_temp'] == "checked"]
        pass_y_len = len(df_pass_y_count.index)
        df_fail_y_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['fail_y_temp'] == "checked"]
        fail_y_len = len(df_fail_y_count.index)
        df_fail_n_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['fail_n_temp'] == "checked"]
        fail_n_len = len(df_fail_n_count.index)
        if int(total_len) != int(pass_y_len) + int(fail_y_len) + int(fail_n_len):
            messages.error(request, "There are entries not entered.")  # 경고
            #################검색어 반영##################
            selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
            searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
            if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
                try:
                    if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 status__icontains=searchtext).order_by('team',
                                                                                                        'plandate')  # db 동기화
                    elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 team__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 pmsheetno__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                    elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 name__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    else:
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                              'plandate')  # db 동기화
                except:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기
                if str(searchtext) == "None":
                    searchtext = ""
            else:
                try:
                    if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 status__icontains=searchtext).order_by('team',
                                                                                                        'plandate')  # db 동기화
                    elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 team__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 pmsheetno__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                    elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 name__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    else:
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                 sch_clear="Y").order_by(
                            'team', 'plandate')  # db 동기화
                except:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                             sch_clear="Y").order_by('team',
                                                                                     'plandate')  # db 동기
                if str(searchtext) == "None":
                    searchtext = ""
            spare_list = spare_out.objects.filter(used_y_n=pmcode)
            equipinfo = equiplist.objects.filter(controlno=controlno)
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
            pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
            pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
            plandate = pm_plandate.plandate
            actiondate = pm_plandate.actiondate
            remark_get = pm_plandate.remark_temp
            context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,"url_comp":url_comp,
                       "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
            context.update(users)
            return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결
    #####fail_y 입력 시 repair입력 여부 확인#####
        for k in range(total_len):
            fail_y_ckeck = df_pmcheckitem_count.iat[k,18]
            if fail_y_ckeck == "checked":
                fail_y_ckeck = df_pmcheckitem_count.iat[k,20]
                if fail_y_ckeck == "":
                    messages.error(request, "Repair Detail has not been entered.")  # 경고
                    #################검색어 반영##################
                    selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
                    searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
                    if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
                        try:
                            if selecttext == "status":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         status__icontains=searchtext).order_by('team',
                                                                                                                'plandate')  # db 동기화
                            elif selecttext == "team":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         team__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            elif selecttext == "control_no":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         pmsheetno__icontains=searchtext).order_by(
                                    'team',
                                    'plandate')  # db 동기화
                            elif selecttext == "equipname":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         name__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            else:
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by(
                                    'team',
                                    'plandate')  # db 동기화
                        except:
                            pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by(
                                'team',
                                'plandate')  # db 동기
                        if str(searchtext) == "None":
                            searchtext = ""
                    else:
                        try:
                            if selecttext == "status":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         status__icontains=searchtext).order_by('team',
                                                                                                                'plandate')  # db 동기화
                            elif selecttext == "team":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         team__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            elif selecttext == "control_no":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         pmsheetno__icontains=searchtext).order_by(
                                    'team',
                                    'plandate')  # db 동기화
                            elif selecttext == "equipname":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         name__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            else:
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y").order_by(
                                    'team', 'plandate')  # db 동기화
                        except:
                            pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                     sch_clear="Y").order_by('team',
                                                                                             'plandate')  # db 동기
                        if str(searchtext) == "None":
                            searchtext = ""
                    spare_list = spare_out.objects.filter(used_y_n=pmcode)
                    equipinfo = equiplist.objects.filter(controlno=controlno)
                    equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
                    pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
                    pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
                    pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
                    plandate = pm_plandate.plandate
                    actiondate = pm_plandate.actiondate
                    remark_get = pm_plandate.remark_temp
                    context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                               "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                               "actiondate": actiondate,"url_comp":url_comp,
                               "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                               "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
                    context.update(users)
                    return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결
    #####fail_n 입력 시 workrequest입력 여부 확인#####
        for m in range(total_len):
            fail_y_ckeck = df_pmcheckitem_count.iat[m,19]
            if fail_y_ckeck == "checked":
                fail_y_ckeck = df_pmcheckitem_count.iat[m,22]
                if fail_y_ckeck == "":
                    messages.error(request, "Work Request has not been received.")  # 경고
                    #################검색어 반영##################
                    selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
                    searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
                    if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
                        try:
                            if selecttext == "status":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         status__icontains=searchtext).order_by('team',
                                                                                                                'plandate')  # db 동기화
                            elif selecttext == "team":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         team__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            elif selecttext == "control_no":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         pmsheetno__icontains=searchtext).order_by(
                                    'team',
                                    'plandate')  # db 동기화
                            elif selecttext == "equipname":
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                         name__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            else:
                                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by(
                                    'team',
                                    'plandate')  # db 동기화
                        except:
                            pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by(
                                'team',
                                'plandate')  # db 동기
                        if str(searchtext) == "None":
                            searchtext = ""
                    else:
                        try:
                            if selecttext == "status":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         status__icontains=searchtext).order_by('team',
                                                                                                                'plandate')  # db 동기화
                            elif selecttext == "team":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         team__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            elif selecttext == "control_no":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         pmsheetno__icontains=searchtext).order_by(
                                    'team',
                                    'plandate')  # db 동기화
                            elif selecttext == "equipname":
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y",
                                                                         name__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                            else:
                                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                         sch_clear="Y").order_by(
                                    'team', 'plandate')  # db 동기화
                        except:
                            pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                     sch_clear="Y").order_by('team',
                                                                                             'plandate')  # db 동기
                        if str(searchtext) == "None":
                            searchtext = ""
                    spare_list = spare_out.objects.filter(used_y_n=pmcode)
                    equipinfo = equiplist.objects.filter(controlno=controlno)
                    equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
                    pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
                    pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
                    pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
                    plandate = pm_plandate.plandate
                    actiondate = pm_plandate.actiondate
                    remark_get = pm_plandate.remark_temp
                    context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                               "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                               "actiondate": actiondate,"url_comp":url_comp,
                               "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                               "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
                    context.update(users)
                    return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결
    #####Remark 미입력 확인#####
        remark_check = pm_sch.objects.get(pmcode=pmcode)
        if remark_check.remark_temp == "":
           if remark_check.remark_na_temp =="":
               messages.error(request, "Remark was not entered.")  # 경고
               #################검색어 반영##################
               selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
               searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
               if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
                   try:
                       if selecttext == "status":
                           pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                    status__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                       elif selecttext == "team":
                           pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                    team__icontains=searchtext).order_by('team',
                                                                                                         'plandate')  # db 동기화
                       elif selecttext == "control_no":
                           pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                    pmsheetno__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                       elif selecttext == "equipname":
                           pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                    name__icontains=searchtext).order_by('team',
                                                                                                         'plandate')  # db 동기화
                       else:
                           pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                 'plandate')  # db 동기화
                   except:
                       pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                             'plandate')  # db 동기
                   if str(searchtext) == "None":
                       searchtext = ""
               else:
                   try:
                       if selecttext == "status":
                           pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                    status__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                       elif selecttext == "team":
                           pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                    team__icontains=searchtext).order_by('team',
                                                                                                         'plandate')  # db 동기화
                       elif selecttext == "control_no":
                           pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                    pmsheetno__icontains=searchtext).order_by('team',
                                                                                                              'plandate')  # db 동기화
                       elif selecttext == "equipname":
                           pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                    name__icontains=searchtext).order_by('team',
                                                                                                         'plandate')  # db 동기화
                       else:
                           pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                    sch_clear="Y").order_by(
                               'team', 'plandate')  # db 동기화
                   except:
                       pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                sch_clear="Y").order_by('team',
                                                                                        'plandate')  # db 동기
                   if str(searchtext) == "None":
                       searchtext = ""
               spare_list = spare_out.objects.filter(used_y_n=pmcode)
               equipinfo = equiplist.objects.filter(controlno=controlno)
               equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
               pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
               pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
               pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
               plandate = pm_plandate.plandate
               actiondate = pm_plandate.actiondate
               remark_get = pm_plandate.remark_temp
               context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                          "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                          "actiondate": actiondate,"url_comp":url_comp,
                          "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                          "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
               context.update(users)
               return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결
    #####입력날짜 받기#####
        today = date.datetime.today()
        submit_date = "20" + today.strftime('%y') + "-" + today.strftime('%m')+ "-" + today.strftime('%d')
    #####엑션데이터 저장하기#####
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pm_plandate.actiondate_temp = submit_date
        pm_plandate.status = "Performed"
        pm_plandate.p_name = username
        pm_plandate.p_date = submit_date
        pm_plandate.save()
    #####입력완료창으로 변경#####
        comp_signal ="Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "pmchecksheet_info": pmchecksheet_info, "comp_signal":comp_signal,"url_comp":url_comp,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결

def pmchecksheet_return(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####첨부파일 시그널 주기#####
            url_comp = "N"
    #####결재 확인하기#####
        status_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        status_check = status_check.status
        if status_check != "Performed":
            #####승인요청여부 확인하기#####
            comp_signal = "Y"
            #################검색어 반영##################
            selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
            searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
            if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
                try:
                    if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 status__icontains=searchtext).order_by('team',
                                                                                                        'plandate')  # db 동기화
                    elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 team__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 pmsheetno__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                    elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                                 name__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    else:
                        pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                              'plandate')  # db 동기화
                except:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기
                if str(searchtext) == "None":
                    searchtext = ""
            else:
                try:
                    if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 status__icontains=searchtext).order_by('team',
                                                                                                        'plandate')  # db 동기화
                    elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 team__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 pmsheetno__icontains=searchtext).order_by('team',
                                                                                                           'plandate')  # db 동기화
                    elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                                 name__icontains=searchtext).order_by('team',
                                                                                                      'plandate')  # db 동기화
                    else:
                        pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                                 sch_clear="Y").order_by(
                            'team', 'plandate')  # db 동기화
                except:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                             sch_clear="Y").order_by('team',
                                                                                     'plandate')  # db 동기
                if str(searchtext) == "None":
                    searchtext = ""
            #####에러메세지 보내기#####
            messages.error(request, "PM Check Sheet that have been approved cannot be returned.")  # 경고
            #####equip info 정보 보내기#####
            spare_list = spare_out.objects.filter(used_y_n=pmcode)
            equipinfo = equiplist.objects.filter(controlno=controlno)
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
            pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
            pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
            plandate = pm_plandate.plandate
            actiondate = pm_plandate.actiondate
            remark_get = pm_plandate.remark_temp
            context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                       "actiondate": actiondate,"url_comp":url_comp,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                       "comp_signal": comp_signal, "calendarsearch": calendarsearch, "selecttext": selecttext
                        , "searchtext": searchtext,"spare_list":spare_list}
            context.update(users)
            return render(request, 'pmchecksheet_write.html', context)  # templates 내 html연결
    #####승인요청여부 확인하기#####
        comp_signal = "N"
    #####pm_sch status 변경하기#####
        status_change = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        status_change.status = "Fixed Date"
        status_change.p_name = ""
        status_change.p_date = ""
        status_change.save()
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                                     'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo=equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,"url_comp":url_comp,
                   "pmcode": pmcode, "remark_get":remark_get,"pmchecksheet_info":pmchecksheet_info, "comp_signal":comp_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context) #templates 내 html연결


def pmchecksheet_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get("controlno")
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        pmcode = request.POST.get("pmcode")
        calendarsearch = request.POST.get('calendarsearch')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                          'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(date=calendarsearch, sch_clear="Y").order_by('team',
                                                                                                      'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             status__icontains=searchtext).order_by('team',
                                                                                                    'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             team__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             pmsheetno__icontains=searchtext).order_by('team',
                                                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y",
                                                             name__icontains=searchtext).order_by('team',
                                                                                                  'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch,
                                                             sch_clear="Y").order_by(
                        'team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(team=userteam, date=calendarsearch, sch_clear="Y").order_by(
                    'team',
                    'plandate')  # db 동기
            if str(searchtext) == "None":
                searchtext = ""
    #################파일업로드하기##################
        if "upload_file" in request.FILES:
                # 파일 업로드 하기!!!
           upload_file = request.FILES["upload_file"]
           fs = FileSystemStorage()
           name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
                    # 파일 읽어오기!!!
           url = fs.url(name)
        else:
            file_name = "-"
    #################파일업로드url저장하기##################
        try:
            attach_change = pm_sch.objects.get(pmcode=pmcode)  #
            attach_change.attach_temp = url
            attach_change.save()
        except:
            pass
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_sch": pmchecksheet_sch,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                       "actiondate": actiondate,'url_comp': url_comp,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                       "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmchecksheet_write.html', context)

def pmchecksheet_workrequest(request):
    return render(request, 'pmchecksheet_workrequest.html') #templates 내 html연결

def used_parts_link(request):
    spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code','team')  # db 동기화
    context = {"spareparts_release":spareparts_release}
    return render(request, 'used_parts_link.html', context) #templates 내 html연결

def used_parts_link_click(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html 선택조건의 값을 받는다
        used_part = request.POST.get('used_part')  # html 입력 값을 받는다
        out_code = request.POST.get('out_code')  # html 선택조건의 값을 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 선택조건의 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####값 저장하기###
        if used_part =="Y":
            used_part_input = spare_out.objects.get(no=no)
            used_part_input.used_y_n_temp = pmcode
            used_part_input.check_y_n_temp = "checked"
            used_part_input.save()
        elif used_part =="N":
            used_part_input = spare_out.objects.get(no=no)
            used_part_input.used_y_n_temp = ""
            used_part_input.check_y_n_temp = ""
            used_part_input.save()
        context = {"spareparts_release": spareparts_release}
        context.update(users)
        return render(request, 'used_parts_link.html', context)  # templates 내 html연결

def used_parts_link_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        pmcode = request.POST.get('pmcode')  # html 선택조건의 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 선택조건의 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####사용자재 링크저장하기###
        used_submit = spare_out.objects.filter(used_y_n_temp=pmcode)
        used_submit = used_submit.values('no')  # sql문 dataframe으로 변경
        df_used_submit = pd.DataFrame.from_records(used_submit)
        df_used_submit_len = len(df_used_submit.index)  # 일정 숫자로 변환
        for k in range(df_used_submit_len):
            used_no = df_used_submit.iat[k, 0]
            used_no_save = spare_out.objects.get(no=used_no)
            used_no_save.used_y_n = used_no_save.used_y_n_temp
            used_no_save.check_y_n = used_no_save.check_y_n_temp
            used_no_save.save()
    ####사용자재 Y 입력하기###
        used_check = pmchecksheet.objects.get(pmcode=pmcode, itemcode=itemcode)
        used_check.usedpart_temp="Y"
        used_check.save()
        close_signal ="Y"
        context = {"spareparts_release": spareparts_release,"close_signal":close_signal}
        return render(request, 'used_parts_link.html', context)  # templates 내 html연결

def used_parts_link_minus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                          'team')  # db 동기화
        ####값 저장하기###
        qy_get = spare_out.objects.get(no=no)
        qy_cal = int(qy_get.used_qy) - 1
        if qy_cal > 0:
            qy_get.used_qy = qy_cal
            qy_get.save()
        context = {"spareparts_release": spareparts_release}
        return render(request, 'used_parts_link.html', context)  # templates 내 html연결

def used_parts_link_plus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####값 저장하기###
        qy_get = spare_out.objects.get(no=no)
        qy_cal = int(qy_get.used_qy) + 1
        if qy_cal <= int(qy_get.qy):
            qy_get.used_qy = qy_cal
            qy_get.save()
        context = {"spareparts_release": spareparts_release}
        return render(request, 'used_parts_link.html', context)  # templates 내 html연결

################################
####PM CONTROL FORM Approval####
################################
def pmcheckapproval_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        pmmasterlists = pmmasterlist.objects.all().order_by('team','controlno') #db
    ####테이블 감추기 신호####
        table_signal = "table_signal"
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                            'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(
                                date=calendarsearch, sch_clear="Y", status="Reviewed",pmsheetno__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                else:
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Performed").order_by('team','plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                            'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                elif selecttext == "control_no":
                        pmchecksheet_sch = pm_sch.objects.filter(
                                date=calendarsearch, sch_clear="Y", status="Reviewed",pmsheetno__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                elif selecttext == "equipname":
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                            'team','plandate')  # db 동기화
                else:
                        pmchecksheet_sch = pm_sch.objects.filter(
                            date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team','plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
                searchtext = ""
        context = {"pmmasterlists":pmmasterlists,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch, "table_signal":table_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

def pmcheckapproval_check(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####Reviewed 신호주기#####
        reviwed_signal = pm_sch.objects.get(pmcode=pmcode)
        reviwed_signal = str(reviwed_signal.r_name_temp)
        if reviwed_signal == "":
            review_signal = "N"
        elif reviwed_signal == "None":
            review_signal = "N"
        else:
            review_signal = "Y"
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "review_signal":review_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,
                    "url_comp":url_comp,"spare_list":spare_list}
    context.update(users)
    return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

def pmcheckapproval_review_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Reviewed", division="PM Check Sheet")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            review_signal = "N"
        else:
        #####Reviewed 업데이트#####
            today = date.datetime.today()
            review_today = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" +today.strftime('%d')
            reviwed_signal = pm_sch.objects.get(pmcode=pmcode)
            reviwed_signal.r_name_temp = username
            reviwed_signal.r_date_temp = review_today
            reviwed_signal.status = "Reviewed"
            reviwed_signal.save()
            reviwed_signal = str(reviwed_signal.r_name_temp)
            if reviwed_signal == "":
                review_signal = "N"
            elif reviwed_signal == "None":
                review_signal = "N"
            else:
                review_signal = "Y"
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "review_signal":review_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,
                   "url_comp": url_comp,"spare_list":spare_list}
    context.update(users)
    return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

def pmcheckapproval_review_reject(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Reviewed", division="PM Check Sheet")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            review_signal = "N"
        else:
        #####status변경하기 업데이트#####
            today = date.datetime.today()
            review_today = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" +today.strftime('%d')
            reviwed_signal = pm_sch.objects.get(pmcode=pmcode)
            reviwed_signal.p_name = ""
            reviwed_signal.p_date = ""
            reviwed_signal.status = "Fixed Date"
            reviwed_signal.save()
            review_signal = ""
            #reviwed_signal = str(reviwed_signal.r_name_temp)
            #if reviwed_signal == "":
            #    review_signal = "N"
            #elif reviwed_signal == "None":
            #    review_signal = "N"
            #else:
            #    review_signal = "Y"
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####반려사유 메일 보내기#####


    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "review_signal":review_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,
                   "url_comp": url_comp,"spare_list":spare_list}
    context.update(users)
    return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

def pmcheckapproval_approve_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Checked", division="PM Check Sheet")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            review_signal = "Y"
            approval_signal = "N"
        else:
        #####approved pm_sch업데이트#####
            today = date.datetime.today()
            approve_today = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" +today.strftime('%d')
            reviwed_signal = pm_sch.objects.get(pmcode=pmcode)
            reviwed_signal.actiondate = reviwed_signal.actiondate_temp
            reviwed_signal.remark = reviwed_signal.remark_temp
            reviwed_signal.remark_na = reviwed_signal.remark_na_temp
            reviwed_signal.r_name = reviwed_signal.r_name_temp
            reviwed_signal.r_date = reviwed_signal.r_date_temp
            reviwed_signal.attach = reviwed_signal.attach_temp
            reviwed_signal.a_name = username
            reviwed_signal.a_date = approve_today
            reviwed_signal.status = "Complete"
            reviwed_signal.save()
    ####결재 중 삭제 시 try로 치환하기####
        try:
            #####다음 계획일 계산하기#####
                pmsheetnos = reviwed_signal.pmsheetno
                frequency = pmsheetdb.objects.get(pmsheetno=pmsheetnos)
                frequency= frequency.freq
                frequency = frequency[:3]
                f_m_y = frequency[2:]
                if f_m_y == "o" or f_m_y == "e": #주기숫자 구분 반환
                    f_num = frequency[:1]
                else:
                    f_num = frequency[:2]
            #####이번달 반환####
                now_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
                now_plandate = now_plandate.plandate[:7]
                now_plandate_y = now_plandate[:4]
                now_plandate_m = now_plandate[5:]
                now_plandate = date.datetime(int(now_plandate_y), int(now_plandate_m), 1)
            #####다음 계획 치환####
                if f_m_y == "o" or f_m_y == "M":
                    next_plan = now_plandate + relativedelta(months=int(f_num))
                    next_plandate = "20" + next_plan.strftime('%y') + "-" + next_plan.strftime('%m')
                else:
                    next_plan = now_plandate + relativedelta(years=int(f_num))
                    next_plandate = "20" + next_plan.strftime('%y') + "-" + next_plan.strftime('%m')
            #####신규 pm_sch업데이트#####
                new_plan = pm_sch.objects.get(pmcode=pmcode)
                pmsheetno = new_plan.pmsheetno
                pmsheetdb_pm_sch = pmsheetdb.objects.get(pmsheetno_temp=pmsheetno)  # pmsheetno_temp 일치되는 값 찾기
                pmsheetdb_controlno = pmsheetdb_pm_sch.controlno  # 컨트롤넘버 값 치환
                controlformlist_controlno = controlformlist.objects.get(controlno=pmsheetdb_controlno,
                                                                        recent_y="Y")  # 컨트롤넘버 일치되는 값 찾기
                equiplist_controlno = equiplist.objects.get(controlno=pmsheetdb_controlno)  # 컨트롤넘버 일치되는 값 찾기
                pm_sch(
                    team=controlformlist_controlno.team,  # 팀명
                    pmsheetno=pmsheetdb_pm_sch.pmsheetno_temp,  # 설비명
                    pmcode=pmsheetdb_pm_sch.pmsheetno_temp + "/" + next_plandate,  # pmcode
                    revno=controlformlist_controlno.revno,  # 시리얼넘버
                    revdate=controlformlist_controlno.revdate,  # 설비명
                    controlno=controlformlist_controlno.controlno,  # 컨트롤넘버
                    name=controlformlist_controlno.name,  # 모델명
                    roomno=equiplist_controlno.roomno,  # 시리얼넘버
                    roomname=equiplist_controlno.roomname,  # 모델명
                    date=next_plandate,  # 시리얼넘버
                ).save()
        except:
            pass
    #####pm check sheet업데이트#####
        pm_upload = pmchecksheet.objects.filter(pmcode=pmcode)
        pmcode_upload = pm_upload.values('pmcode')  # sql문 dataframe으로 변경
        df_pmcode_upload = pd.DataFrame.from_records(pmcode_upload)
        df_pmcode_upload_len = len(df_pmcode_upload.index)  # 일정 숫자로 변환
        for k in range(df_pmcode_upload_len):
            pmcode_upload = df_pmcode_upload.iat[k, 0]
            pm_upload_save = pmchecksheet.objects.get(pmcode=pmcode_upload)
            pm_upload_save.result = pm_upload_save.result_temp
            pm_upload_save.pass_y = pm_upload_save.pass_y_temp
            pm_upload_save.fail_y = pm_upload_save.fail_y_temp
            pm_upload_save.fail_n = pm_upload_save.fail_n_temp
            pm_upload_save.actiondetail = pm_upload_save.actiondetail_temp
            pm_upload_save.workrequest = pm_upload_save.workrequest_temp
            pm_upload_save.usedpart = pm_upload_save.usedpart_temp
            pm_upload_save.save()
        #####reviwed/approval_signal#####
        reviewed_chk = pm_sch.objects.get(pmcode=pmcode)
        reviewed_signal = str(reviewed_chk.r_name_temp)
        if reviewed_signal == "":
            review_signal = "N"
        elif reviewed_signal == "None":
            review_signal = "N"
        else:
            review_signal = "Y"
        approval_signal = "Y"
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "review_signal":review_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,
                   "approval_signal":approval_signal, "url_comp":url_comp,"spare_list":spare_list}
    context.update(users)
    return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

def pmcheckapproval_approve_reject(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Checked", division="PM Check Sheet")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            review_signal = "Y"
        else:
        #####status변경하기 업데이트#####
            reviwed_signal = pm_sch.objects.get(pmcode=pmcode)
            reviwed_signal.p_name = ""
            reviwed_signal.p_date = ""
            reviwed_signal.r_name_temp = ""
            reviwed_signal.r_date_temp = ""
            reviwed_signal.status = "Fixed Date"
            reviwed_signal.save()
            review_signal = ""
            #reviwed_signal = str(reviwed_signal.r_name_temp)
            #if reviwed_signal == "":
            #    review_signal = "N"
            #elif reviwed_signal == "None":
            #    review_signal = "N"
            #else:
            #    review_signal = "Y"
    #################검색어 반영##################
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Check Sheet", description="Checked")
        SO_M = auth_check.code_no
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if auth == SO_S:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Performed").order_by('team', 'plandate')  # db 동기화
        elif auth == SO_M:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", status__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", team__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", pmsheetno__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed", name__icontains=searchtext).order_by(
                        'team', 'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    date=calendarsearch, sch_clear="Y", status="Reviewed").order_by('team', 'plandate')  # db 동기화
        else:
            try:
                if selecttext == "status":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", status__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            status__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "team":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", team__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            team__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                elif selecttext == "control_no":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", pmsheetno__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            pmsheetno__icontains=searchtext)).order_by('team',
                                                                       'plandate')  # db 동기화
                elif selecttext == "equipname":
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed", name__icontains=searchtext) | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed",
                            name__icontains=searchtext)).order_by(
                        'team',
                        'plandate')  # db 동기화
                else:
                    pmchecksheet_sch = pm_sch.objects.filter(
                        Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                            date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                             'plandate')  # db 동기화
            except:
                pmchecksheet_sch = pm_sch.objects.filter(
                    Q(date=calendarsearch, sch_clear="Y", status="Performed") | Q(
                        date=calendarsearch, sch_clear="Y", status="Reviewed")).order_by('team',
                                                                                         'plandate')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####반려사유 메일 보내기#####


    #####equip info 정보 보내기#####
        approval_signal = "N"
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode) #plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate_temp
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets":pmchecksheets,"loginid":loginid, "pmchecksheet_sch":pmchecksheet_sch,
                   "equipinfo":equipinfo,"equipinforev":equipinforev, "plandate":plandate, "actiondate":actiondate,
                    "remark_get": remark_get,"pmchecksheet_info":pmchecksheet_info, "review_signal":review_signal,
                   "calendarsearch": calendarsearch, "selecttext": selecttext, "searchtext": searchtext,
                   "approval_signal":approval_signal, "url_comp":url_comp,"spare_list":spare_list}
    context.update(users)
    return render(request, 'pmcheckapproval_main.html', context) #templates 내 html연결

#######################
####PM CONTROL FORM####
#######################
def pmcontrolform_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext,
                                                                  recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        context = {"controlformlists":controlformlists,"loginid":loginid,"selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_main.html', context) #templates 내 html연결

def pmcontrolform_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext, recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by('team', 'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
                searchtext = ""
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####리비젼셀렉트기능 추가#####
        rev_no_str = controlformlist.objects.get(controlno = controlno, recent_y="Y")
        rev_no_str = rev_no_str.revno
        rev_no_int = int(rev_no_str)
        rev_no_count = [rev_no_int]
        while rev_no_int > 1:
            rev_no_int = rev_no_int - 1
            rev_no_count.append(rev_no_int)
        rev_no_count = rev_no_count
    #####equip info 정보 보내기#####
        rev_no_1 = request.POST.get('rev_no_1')  # html rev_no1(최신)의 값을 받는다
        rev_no_2 = request.POST.get('rev_no_2')  # html rev_no2(셀렉트)의 값을 받는다
        if str(rev_no_2) == "None":
            rev_no = rev_no_1  # html rev_no1(최신)의 값을 받는다
            equipinforev = controlformlist.objects.filter(controlno=controlno, revno=rev_no, recent_y="Y")
        else:
            rev_no = rev_no_2  # html rev_no2(셀렉트)의 값을 받는다
            equipinforev = controlformlist.objects.filter(controlno=controlno, revno=rev_no)
        equipinfo = equiplist.objects.filter(controlno = controlno)
        controlformdb = pmmasterlist.objects.filter(controlno=controlno, revno=rev_no).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno, filter_check="Y").order_by('freq_temp')
        context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                   "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet_temp":pmsheet,
                   "rev_no_count":rev_no_count, "rev_no":rev_no, "selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_view.html', context)  # templates 내 html연결

def pmcontrolform_write(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb_temp = pmmasterlist_temp.objects.filter(controlno=controlno).order_by('freq')
        pmsheet_temp = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext,
                                                                  recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
    #####signal 정보 보내기#####
        pmreference = pm_reference.objects.all()
        signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        signal = [signalinfo.status][0]
        context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
                   "equipinforev": equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet_temp":pmsheet_temp,
                   "signal":signal, "pmreference":pmreference,"selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결

def pmcontrolform_change_new(request):
    pmreference = pm_reference.objects.all()
    frequency = ""
    context = {"pmreference": pmreference,"frequency":frequency}
    return render(request, 'pmcontrolform_change_new.html', context)  # templates 내 html연결

def pmcontrolform_change_division(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        division = request.POST.get('division')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        if division == "Manual":
                frequency = ""
                freq_no = ""
                freq_my = ""
        elif division == "Standard":
                freq_get = equiplist.objects.get(controlno=controlno)
                frequency = freq_get.ra + "Month"
                freq_no = freq_get.ra
                freq_my = "Month"
        else:
                freq_get = pm_reference.objects.get(description=division)
                freq_no = freq_get.freq_m_y
                freq_my = freq_get.m_y
                frequency = freq_no + freq_my
        pmreference = pm_reference.objects.all()
        division_get = division
        context = {"pmreference": pmreference,"loginid":loginid, "frequency":frequency,"division_get":division_get,
                   "freq_no":freq_no,"freq_my":freq_my}
        context.update(users)
        return render(request, 'pmcontrolform_change_new.html', context)  # templates 내 html연결

def pmcontrolform_write_new(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equiptable = equiplist.objects.get(controlno=controlno)
        equiptablerev = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        pmreference = pm_reference.objects.all()
    #####주기 미입력확인#####
        division = request.POST.get('division')  # html에서 해당 값을 받는다
        freq_no = request.POST.get('freq_no')  # html에서 해당 값을 받는다
        freq_my = request.POST.get('freq_my')  # html에서 해당 값을 받는다
        frequency = request.POST.get('frequency')
        if division == "Manual":
            if (freq_no == "None") or (freq_my == "None"):
                messages.error(request, "입력안했다~")  # 경고
                #####signal 정보 보내기#####
                division_get = division
                context = {"pmreference": pmreference, "loginid": loginid, "frequency": frequency,
                           "division_get": division_get,
                           "freq_no": freq_no, "freq_my": freq_my}
                context.update(users)
                return render(request, 'pmcontrolform_change_new.html', context)  # templates 내 html연결
    #####데이터 가공하기#####
        ######sheet No. 만들기#####
        freq_no=request.POST.get('freq_no')
        freq_my=request.POST.get('freq_my')
        if int(freq_no) == 12:
            sheetno = str(controlno) + "-1Y"
        else:
            if freq_my == "Month":
                freq_my = "M"
            else:
                freq_my = "Y"
            sheetno = str(controlno) + "-" + str(freq_no) + freq_my
    ######주기만들기#####
        freq_no=request.POST.get('freq_no')
        freq_my=request.POST.get('freq_my')
        freq = str(freq_no) + str(freq_my)
    ######itemno 만들기#####
        itemno_make = pmmasterlist_temp.objects.filter(sheetno = sheetno).values('sheetno')
        df = pd.DataFrame.from_records(itemno_make)
        itemno = len(df.index) + 1
    ######itemcode 만들기#####
        itemcode = sheetno + str(itemno)
    ######시트시작일 만들기#####
        try:
            chk = pmsheetdb.objects.get(pmsheetno_temp=sheetno)
        except:
            pmsheetdb(
                controlno=controlno,
                pmsheetno_temp = sheetno, #신규Sheet No. 임시입력
                freq_temp= freq, #신규주기 임시입력
                startdate_temp= "New", #시작일자 입력
            ).save()
    #####새로운 값 저장하기#####
        pmmasterlist_temp(  # 컨트롤폼에 신규등록하기
            team=equiptable.team,  # 팀명
            controlno=controlno,  # 컨트롤넘버
            name=equiptable.name,  # 설비명
            model=equiptable.model,  # 모델명
            serial=equiptable.serial,  # 시리얼넘버
            maker=equiptable.maker,  # 제조사
            roomname=equiptable.roomname,  # 룸명
            roomno=equiptable.roomno,  # 룸넘버
            revno=equiptablerev.revno,  # 리비젼넘버
            date=equiptablerev.revdate,  # 리비젼날짜
            freq=freq,  # 주기
            ra=equiptable.ra,  # ra결과
            sheetno=sheetno,  # 시트넘버
            amd="A",  # a/m/d
            itemno= itemno,  # 순번
            item=request.POST.get('item'),  # 점검내용
            check=request.POST.get('check'),  # 점검기준
            startdate= "New",  # 시트시작일
            change=request.POST.get('change'),  # 변경사유
            itemcode=itemcode,  # 점검내용 구분좌
            division=request.POST.get('division'),
        ).save()
    #####signal 정보 보내기#####
        #####완료 시그널 주기#####
        comp_signal = "Y"
        division_get = division
        context = {"pmreference": pmreference, "loginid": loginid, "frequency": frequency,
                   "division_get": division_get,"comp_signal":comp_signal,
                   "freq_no": freq_no, "freq_my": freq_my}
        context.update(users)
        return render(request, 'pmcontrolform_change_new.html', context)  # templates 내 html연결

def pmcontrolform_change_link(request):
    return render(request, 'pmcontrolform_change_link.html')  # templates 내 html연결

def pmcontrolform_change_controlno(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
 ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
 ##컨트롤넘버 정보 불러오기##
        try:
            equip_info = equiplist.objects.get(controlno=controlno)
            team_get = equip_info.team
            equip_get = equip_info.name
            controlno_get = controlno
            pm_list = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
            view_signal="Y"
            context = {"team_get": team_get, "loginid": loginid, "pm_list": pm_list,"controlno_get":controlno_get,
                       "equip_get":equip_get,"view_signal":view_signal}
            context.update(users)
        except:
            messages.error(request, "No such equipment exist.")  # 경고
            context = {"loginid": loginid}
        return render(request, 'pmcontrolform_change_link.html', context)  # templates 내 html연결

def pmcontrolform_change_link_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno_get = request.POST.get('controlno_get')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equiptable = equiplist.objects.get(controlno=controlno)
        equiptablerev = controlformlist.objects.get(controlno=controlno, recent_y="Y")
    ###새로운 컨트롤폼 여부확인하기###
        new_check = pmmasterlist_temp.objects.filter(controlno=controlno)
        new_check = new_check.values('controlno')
        df_new_check = pd.DataFrame.from_records(new_check)
        df_new_check_len = len(df_new_check.index)  # itemcode 하나씩 넘기기
        if int(df_new_check_len) > 0:
            messages.error(request, "PM Maintenance Item already exists.")  # 경고
        else:
    ##컨트롤넘버 DB불러오기##
            db_call = pmmasterlist.objects.filter(controlno=controlno_get, amd="A", pm_y_n="Y")
            db_call = db_call.values('itemcode')
            df_db_call = pd.DataFrame.from_records(db_call)
            df_db_call_len = len(df_db_call.index)  # itemcode 하나씩 넘기기
            for j in range(df_db_call_len):
                itemcode_call = df_db_call.iat[j, 0]
                item_call = pmmasterlist.objects.get(controlno=controlno_get, amd="A", pm_y_n="Y", itemcode=itemcode_call)
                ra_call = equiplist.objects.get(controlno=controlno)
                if str(item_call.division) != "Standard":
                    ###sheet_no만들기###
                    if (str(item_call.freq[:2]) == "10") or (str(item_call.freq[:2]) == "11") or (str(item_call.freq[:2]) == "12"):
                        sheet_no = str(controlno) + "-" + str(item_call.freq[:3])
                    else:
                        sheet_no = str(controlno) + "-" + str(item_call.freq[:2])
                    try:
                        item_no_call = pmmasterlist_temp.objects.filter(controlno=controlno, sheetno=sheet_no)
                        item_no_call = item_no_call.values('sheetno')
                        df_item_no_call = pd.DataFrame.from_records(item_no_call)
                        item_no = len(df_item_no_call.index)  # itemcode 하나씩 넘기기
                        item_no = int(item_no) + 1
                    except:
                        item_no = 1
                #####새로운 값 저장하기#####
                    pmmasterlist_temp(  # 컨트롤폼에 신규등록하기
                        team=equiptable.team,  # 팀명
                        controlno=controlno,  # 컨트롤넘버
                        name=equiptable.name,  # 설비명
                        model=equiptable.model,  # 모델명
                        serial=equiptable.serial,  # 시리얼넘버
                        maker=equiptable.maker,  # 제조사
                        roomname=equiptable.roomname,  # 룸명
                        roomno=equiptable.roomno,  # 룸넘버
                        revno=equiptablerev.revno,  # 리비젼넘버
                        date=equiptablerev.revdate,  # 리비젼날짜
                        freq=item_call.freq,  # 주기
                        ra=ra_call.ra,  # ra결과
                        sheetno=sheet_no,  # 시트넘버
                        amd="A",  # a/m/d
                        itemno=item_no,  # 순번
                        item=item_call.item,  # 점검내용
                        check=item_call.check,  # 점검기준
                        startdate="New",  # 시트시작일
                        change="신규등록",  # 변경사유
                        itemcode=str(sheet_no) + str(item_no),  # 점검내용 구분좌
                        division=item_call.division,
                    ).save()
                ####PM_SCH 저장하기###
                    try:
                        pm_sch_check = pmsheetdb.objects.get(pmsheetno=sheet_no)
                    except:
                        pmsheetdb(
                            controlno=controlno,
                            pmsheetno_temp=sheet_no,  # 신규Sheet No. 임시입력
                            freq_temp=item_call.freq,  # 신규주기 임시입력
                            startdate_temp="New",  # 시작일자 입력
                        ).save()
                else:
                    ###주기만들기###
                    frequency = str(ra_call.ra) + "Month"
                    ###sheet_no만들기###
                    sheet_no = str(controlno) + "-" + str(ra_call.ra) + "M"
                    print(sheet_no)
                    try:
                        item_no_call = pmmasterlist_temp.objects.filter(controlno=controlno, sheetno=sheet_no)
                        item_no_call = item_no_call.values('sheetno')
                        df_item_no_call = pd.DataFrame.from_records(item_no_call)
                        item_no = len(df_item_no_call.index)  # itemcode 하나씩 넘기기
                        item_no = int(item_no) + 1
                    except:
                        item_no = 1
                    #####새로운 값 저장하기#####
                    pmmasterlist_temp(  # 컨트롤폼에 신규등록하기
                        team=equiptable.team,  # 팀명
                        controlno=controlno,  # 컨트롤넘버
                        name=equiptable.name,  # 설비명
                        model=equiptable.model,  # 모델명
                        serial=equiptable.serial,  # 시리얼넘버
                        maker=equiptable.maker,  # 제조사
                        roomname=equiptable.roomname,  # 룸명
                        roomno=equiptable.roomno,  # 룸넘버
                        revno=equiptablerev.revno,  # 리비젼넘버
                        date=equiptablerev.revdate,  # 리비젼날짜
                        freq=frequency,  # 주기
                        ra=ra_call.ra,  # ra결과
                        sheetno=sheet_no,  # 시트넘버
                        amd="A",  # a/m/d
                        itemno=item_no,  # 순번
                        item=item_call.item,  # 점검내용
                        check=item_call.check,  # 점검기준
                        startdate="New",  # 시트시작일
                        change="신규등록",  # 변경사유
                        itemcode=str(sheet_no) + str(item_no) ,  # 점검내용 구분좌
                        division=item_call.division,
                    ).save()
                    ####PM_SCH 저장하기###
                    try:
                        pm_sch_check = pmsheetdb.objects.get(pmsheetno=sheet_no)
                    except:
                        pmsheetdb(
                            controlno=controlno,
                            pmsheetno_temp=sheet_no,  # 신규Sheet No. 임시입력
                            freq_temp=item_call.freq,  # 신규주기 임시입력
                            startdate_temp="New",  # 시작일자 입력
                        ).save()
        equip_info = equiplist.objects.get(controlno=controlno_get)
        team_get = equip_info.team
        equip_get = equip_info.name
        pm_list = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
        view_signal = "Y"
        context = {"team_get": team_get, "loginid": loginid, "pm_list": pm_list, "controlno_get": controlno_get,
                    "equip_get": equip_get, "view_signal": view_signal}
        return render(request, 'pmcontrolform_change_link.html', context)  # templates 내 html연결


def pmcontrolform_write_delete(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        itemcode_delete = request.POST.get('itemcode_delete')  # html에서 해당 값을 받는다
        delete_reason = request.POST.get('delete_reason')  # html에서 해당 값을 받는다
        amd_change = request.POST.get('amd_change')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####기존입력값인지 확인하기#####
        startdate_check = pmmasterlist_temp.objects.get(itemcode=itemcode_delete)
        if startdate_check.startdate != "New":
            itemcode_amd = pmmasterlist_temp.objects.get(itemcode = itemcode_delete)
            if amd_change == "A":
                itemcode_amd.amd = "D"
                itemcode_amd.change = delete_reason
                itemcode_amd.startdate = "Delete"
                itemcode_amd.save()
            else:
                messages.error(request, "Deleted items cannot be changed.")  # 경고
        else:
    #####신규 등록일 시 삭제하기#####
            itemcode_amd= pmmasterlist_temp.objects.get(itemcode=itemcode_delete)
            itemcode_amd.delete()
    #####PM Sheet DB 불필요한 사항 삭제하기#####
        pmsheetdb_delete = pmsheetdb.objects.filter(controlno = controlno)
        pmsheetno_temp_delete = pmsheetdb_delete.values('pmsheetno_temp')  # sql문 dataframe으로 변경
        df_pmsheetno_temp_delete = pd.DataFrame.from_records(pmsheetno_temp_delete)
        df_pmsheetno_temp_delete_len = len(df_pmsheetno_temp_delete.index)  # 담당자 인원수 확인
        for k in range(df_pmsheetno_temp_delete_len):
            pmsheetno_temp_delete = df_pmsheetno_temp_delete.iat[k,0]
            pmsheeno_temp = pmmasterlist_temp.objects.filter(sheetno=pmsheetno_temp_delete, amd="A")
            pmsheeno_temp = pmsheeno_temp.values('controlno')  # sql문 dataframe으로 변경
            df_pmsheeno_temp = pd.DataFrame.from_records(pmsheeno_temp)
            df_pmsheeno_temp_len = len(df_pmsheeno_temp.index)  # 담당자 인원수 확인
            if int(df_pmsheeno_temp_len) == 0:
                pmsheeno_delete = pmsheetdb.objects.get(pmsheetno_temp=pmsheetno_temp_delete)
                pmsheeno_delete.delete()
            #####PM sch DB 미완료 아이템 삭제하기#####
                pmcode_del = pm_sch.objects.filter(Q(pmsheetno=pmsheetno_temp_delete, status="Not fixed") |
                                                   Q(pmsheetno=pmsheetno_temp_delete, status="Fixed Date"))
                pmcode_del = pmcode_del.values('pmcode')  # sql문 dataframe으로 변경
                df_pmcode_del = pd.DataFrame.from_records(pmcode_del)
                df_pmcode_del_len = len(df_pmcode_del.index)  # 담당자 인원수 확인
                for m in range(df_pmcode_del_len):
                    pmcode_delete = df_pmcode_del.iat[m, 0]
                    pmcode_delete = pm_sch.objects.get(pmcode=pmcode_delete)
                    pmcode_delete.delete()
        #####signal 정보 보내기#####
        signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        signal = [signalinfo.status][0]
    #####equip info 정보 보내기#####
        controlformdb_temp = pmmasterlist_temp.objects.filter(controlno=controlno).order_by('freq')
        pmsheet_temp = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext,
                                                                  recent_y="Y").order_by('team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmreference = pm_reference.objects.all()
        context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
                   "equipinforev": equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet_temp":pmsheet_temp, "signal":signal,
                   "pmreference":pmreference,"selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결

def pmsheet_startdate(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
    #####기본 창 정보 보내기#####
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb_temp = pmmasterlist_temp.objects.filter(controlno=controlno).order_by('freq')
        pmsheet_temp = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        startdate = str(request.POST.get('startdate'))
        pmreference = pm_reference.objects.all()
    #####신규날짜 받기#####
        if (startdate == "None") or (startdate == ""):
            pmsheetno_temp = request.POST.get('pmsheetno_temp')
            calendartext = request.POST.get('calendartext')
            today = date.datetime.today()
            today_date = "20" + today.strftime('%y') +"-" + today.strftime('%m')
            if calendartext >= today_date:
                pmsheetno_table = pmsheetdb.objects.get(pmsheetno_temp=pmsheetno_temp)
                pmsheetno_table.startdate_temp = calendartext
                pmsheetno_table.save()
            else:
                messages.error(request, "The start date cannot be smaller than this month.")  # 경고
        else:
            messages.error(request, "Already fixed date is not able to change.")  # 경고

    #####signal 정보 보내기#####
        signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        signal = [signalinfo.status][0]
    context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
               "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet_temp": pmsheet_temp, "signal":signal,
               "pmreference": pmreference,"selecttext": selecttext, "searchtext": searchtext}
    context.update(users)
    return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결

def pmcontrolform_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
    #####기본 창 정보 보내기#####
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb_temp = pmmasterlist_temp.objects.filter(controlno=controlno).order_by('freq')
        pmsheet_temp = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmreference = pm_reference.objects.all()
    #####아무것도 안입력되어도 클릭됨#####
        a_count = pmmasterlist_temp.objects.filter(controlno=controlno, amd="A")
        a_count =a_count.values('amd')  # sql문 dataframe으로 변경
        df_a_count = pd.DataFrame.from_records(a_count)
        df_a_count_len = len(df_a_count.index)  # 담당자 인원수 확인
        d_count = pmmasterlist_temp.objects.filter(controlno=controlno, amd="D")
        d_count = d_count.values('amd')  # sql문 dataframe으로 변경
        df_d_count = pd.DataFrame.from_records(d_count)
        df_d_count_len = len(df_d_count.index)  # 담당자 인원수 확인
        a_count_2 = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
        a_count_2 = a_count_2.values('amd')  # sql문 dataframe으로 변경
        df_a_count_2 = pd.DataFrame.from_records(a_count_2)
        df_a_count_2_len = len(df_a_count_2.index)  # 담당자 인원수 확인
        d_count_2 = pmmasterlist.objects.filter(controlno=controlno, amd="D", pm_y_n="Y")
        d_count_2 = d_count_2.values('amd')  # sql문 dataframe으로 변경
        df_d_count_2 = pd.DataFrame.from_records(d_count_2)
        df_d_count_2_len = len(df_d_count_2.index)  # 담당자 인원수 확인
        if df_a_count_len == df_a_count_2_len:
            if df_d_count_len == df_d_count_2_len:
                signal = "New"
                messages.error(request, "Nothing has changed. ")  # 경고
                context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists,
                           "equipinfo": equipinfo,
                           "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno,
                           "pmsheet_temp": pmsheet_temp, "signal": signal,"pmreference":pmreference,
                           "selecttext": selecttext, "searchtext": searchtext}
                context.update(users)
                return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결
    #####미입력 확인 인터락#####
        new_count = pmsheetdb.objects.filter(controlno=controlno, startdate_temp="New")
        new_count = new_count.values('startdate_temp')  # sql문 dataframe으로 변경
        df = pd.DataFrame.from_records(new_count)
        dflen = len(df.index)  # 담당자 인원수 확인
        if dflen > 0 :
            signal = "New"
            messages.error(request, "Please enter the Start Date of New PM Sheet No.")  # 경고
            context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
               "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet_temp": pmsheet_temp, "signal":signal,
               "pmreference":pmreference,"selecttext": selecttext, "searchtext": searchtext}
            context.update(users)
            return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결
        else:
    #####Prerared 정보 신규 등록하기#####
            today = date.datetime.today()
            p_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
            p_name = username
            controlformlist_info = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            controlformlist_info.status = "Prepared"
            controlformlist_info.save()
            controlformlist(
                controlno=controlformlist_info.controlno,
                team=controlformlist_info.team,
                name=controlformlist_info.name,
                status="Prepared",
                revno= int(controlformlist_info.revno),
                p_name = username,
                p_date = p_date,
                recent_y="A",
            ).save()
    #####signal 정보 보내기#####
            signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            signal = [signalinfo.status][0]
            context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
                        "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet_temp": pmsheet_temp,
                        "p_name":p_name, "p_date":p_date, "signal":signal, "pmreference":pmreference,
                       "selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결

def pmcontrolform_return(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
    #####기본 창 정보 보내기#####
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb_temp = pmmasterlist_temp.objects.filter(controlno=controlno).order_by('freq')
        pmsheet_temp = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ####검색어 반영####
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                controlformlists = controlformlist.objects.filter(status__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "team":
                controlformlists = controlformlist.objects.filter(team__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            elif selecttext == "controlno":
                controlformlists = controlformlist.objects.filter(controlno__icontains=searchtext, recent_y="Y").order_by(
                    'team', 'controlno')  # db 동기화
            elif selecttext == "equipname":
                controlformlists = controlformlist.objects.filter(name__icontains=searchtext, recent_y="Y").order_by('team',
                                                                                                                     'controlno')  # db 동기화
            else:
                controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        except:
            controlformlists = controlformlist.objects.filter(recent_y="Y").order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmreference = pm_reference.objects.all()
        today = date.datetime.today()
        p_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        p_name = username
    #####결재 중일 시 클릭불가#####
        return_check = controlformlist.objects.get(controlno=controlno, recent_y="A")
        if return_check.status != "Prepared":
            messages.error(request, "PM Control Form that have been approved cannot be returned.")  # 경고
            #####signal 정보 보내기#####
            signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            signal = [signalinfo.status][0]
            context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists,
                       "equipinfo": equipinfo,
                       "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno,
                       "pmsheet_temp": pmsheet_temp,
                       "p_name": p_name, "p_date": p_date, "signal": signal, "pmreference": pmreference,
                       "selecttext": selecttext, "searchtext": searchtext}
            context.update(users)
            return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결
    #####정보 되돌리기#####
        controlformlist_info = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        controlformlist_info.status = "Review"
        controlformlist_info.save()
        controlformlist_delete = controlformlist.objects.get(controlno=controlno, recent_y="A")
        controlformlist_delete.delete()
    #####signal 정보 보내기#####
        signalinfo = controlformlist.objects.get(controlno=controlno, recent_y="Y")
        signal = [signalinfo.status][0]
        context = {"controlformdb": controlformdb_temp, "controlformlists": controlformlists, "equipinfo": equipinfo,
                        "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet_temp": pmsheet_temp,
                        "p_name":p_name, "p_date":p_date, "signal":signal, "pmreference":pmreference,
                       "selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmcontrolform_write.html', context)  # templates 내 html연결

####################
####PM RA####
####################

def pmra_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                                    'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                                         'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                                    'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                                    'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
        context = {"equiplists":equiplists,"loginid":loginid,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_main.html', context) #templates 내 html연결

def pmra_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        pmok_check = equiplist.objects.get(controlno=controlno)
        pmok = pmok_check.pmok
        context = { "equiplists": equiplists, "equipinfo": equipinfo,"loginid":loginid,"pmok":pmok,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_view.html', context) #templates 내 html연결

def pmra_write(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
    ####if값으로 결재창에 따라 변경하기####
        equipinfos = equiplist.objects.get(controlno=controlno)
        statusvalue = equipinfos.status
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####p_signal#####
        p_signal = equiplist.objects.get(controlno=controlno)
        if p_signal.status == "Prepared":
            p_signal = "OY"
        else:
            p_signal = "NN"
    ####Prepared까지 눌렀을 때####
        if statusvalue == "Prepared":
            score_f = equipinfos.score_f_temp
            score_y = equipinfos.score_y_temp
            score_result = equipinfos.pmscore_temp
            pmreason = equipinfos.pmresult_temp
            pmok = equipinfos.pmok_temp
            ra_result = equipinfos.ra_temp
            p_name = equipinfos.p_name_temp
            p_date = equipinfos.p_date_temp
            context = { "equiplists": equiplists, "equipinfo": equipinfo, "score_f":score_f, "score_y":score_y, "score_result":score_result,
                        "pmreason": pmreason, "pmok": pmok, "ra_result":ra_result,"loginid":loginid, "p_name":p_name, "p_date":p_date,
                        "p_signal":p_signal,"selecttext":selecttext,"searchtext":searchtext}
            context.update(users)
            return render(request, 'pmra_write.html', context)  # templates 내 html연결
    #####CONTEXT#####
        p_signal = "NN"
        context = { "equiplists": equiplists, "equipinfo": equipinfo,"loginid":loginid, "p_signal":p_signal,
                    "selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_write.html', context) #templates 내 html연결

def pm_write_standard(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####pmra status확인하기#####
        status_check = equiplist.objects.get(controlno=controlno)
        if status_check.status =="Complete":
            messages.error(request, "The approved document cannot be changed.")  # 등록완료
            #####CONTEXT#####
            p_signal = "NN"
            context = {"equiplists": equiplists, "equipinfo": equipinfo, "loginid": loginid, "p_signal": p_signal,
                       "selecttext": selecttext, "searchtext": searchtext}
            context.update(users)
            return render(request, 'pmra_write.html', context)  # templates 내 html연결
    #####pmstandard result 정보 보내기#####
        pmreason = request.POST.get('pmreason')  # html controlform의 값을 받는다
        if pmreason == "None":
            pmok = "N"
        else:
            pmok = "Y"
    #####CONTEXT#####
        p_signal = "NN"
        context = {"equiplists": equiplists, "equipinfo": equipinfo, "pmreason":pmreason, "pmok":pmok,"loginid":loginid,
                    "p_signal":p_signal,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_write.html', context) #templates 내 html연결

def pmwritescore(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        pmok = request.POST.get('pmok')  # html PM진행유무의 값을 받는다
        pmreason = request.POST.get('pmreason')  # html PM진행사유의 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        setupdate = equiplist.objects.get(controlno=controlno)
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####pmscore result 정보 보내기#####
        score_f = request.POST.get('score_f')  # html score_f의 값을 받는다
        y = setupdate.setupdate
        today = date.datetime.today()
        y_1 = "20" + today.strftime('%y')
        score = int(y_1) - int(y)
        if score < 6:
            score_y = 1
        elif score < 11:
            score_y = 2
        elif score < 16:
            score_y = 3
        else:
            score_y = 4
        score_result = int(score_f) + int(score_y)
        if score_result == 2:
            ra_result = 12
        elif score_result == 3:
            ra_result = 6
        elif score_result < 6:
            ra_result = 3
        else:
            ra_result = 1
        p_signal = "YN"
    #####CONTEXT#####
        context = { "equiplists": equiplists, "equipinfo": equipinfo, "score_f":score_f, "score_y":score_y, "score_result":score_result,
                    "pmreason": pmreason, "pmok": pmok, "ra_result":ra_result,"loginid":loginid,"p_signal":p_signal,
                    "selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_write.html', context) #templates 내 html연결

def pmra_write_prepared(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        pmreason = request.POST.get('pmreason')  # html PM진행사유의 값을 받는다
        pmok = request.POST.get('pmok')  # html PM진행유무의 값을 받는다
        score_y = request.POST.get('score_y')  # html score_y의 값을 받는다
        score_f = request.POST.get('score_f')  # html score_f의 값을 받는다
        score_result = request.POST.get('score_result')  # html score 결과을 받는다
        ra_result = request.POST.get('ra_result')  # html ra 주기결과값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
    #####작성자 정보 보내기#####
        p_name = username
        today = date.datetime.today()
        p_date = "20" + today.strftime('%y') + "-"+ today.strftime('%m') + "-" + today.strftime('%d')
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####데이터 저장#####
        equip_data = equiplist.objects.get(controlno=controlno)  # 컨트롤넘버 일치되는 값 찾기
        equip_data.pmresult_temp = pmreason
        equip_data.pmok_temp = pmok
        equip_data.score_y_temp = score_y
        equip_data.score_f_temp = score_f
        equip_data.pmscore_temp = score_result
        equip_data.ra_temp = ra_result
        equip_data.p_name_temp = p_name
        equip_data.p_date_temp = p_date
        equip_data.status = "Prepared"
        equip_data.save()
    #####데이터 저장#####
        messages.error(request, "Assessment registered successfully.")  # 등록완료
        p_signal = "ON"
    #####CONTEXT#####
        context = { "equiplists": equiplists, "equipinfo": equipinfo, "score_f":score_f, "score_y":score_y, "score_result":score_result,
                    "pmreason": pmreason, "pmok": pmok, "ra_result":ra_result,"loginid":loginid, "p_name":p_name, "p_date":p_date,
                    "p_signal":p_signal,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_write.html', context)  # templates 내 html연결

def pmra_write_approved(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        pmreason = request.POST.get('pmreason')  # html PM진행사유의 값을 받는다
        pmok = request.POST.get('pmok')  # html PM진행유무의 값을 받는다
        score_y = request.POST.get('score_y')  # html score_y의 값을 받는다
        score_f = request.POST.get('score_f')  # html score_f의 값을 받는다
        score_result = request.POST.get('score_result')  # html score 결과을 받는다
        ra_result = request.POST.get('ra_result')  # html ra 주기결과값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        p_name = request.POST.get('p_name')  # html ra 주기결과값을 받는다
        p_date = request.POST.get('p_date')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##검색어 설정##
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if selecttext == "team":
            equiplists = equiplist.objects.filter(team__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "controlno":
            equiplists = equiplist.objects.filter(controlno__icontains=searchtext).order_by('team',
                                                                                            'controlno')  # db 동기화
        elif selecttext == "equipname":
            equiplists = equiplist.objects.filter(name__icontains=searchtext).order_by('team',
                                                                                       'controlno')  # db 동기화
        elif selecttext == "status":
            equiplists = equiplist.objects.filter(status__icontains=searchtext).order_by('team',
                                                                                         'controlno')  # db 동기화
        else:
            equiplists = equiplist.objects.all().order_by('team', 'controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
    #####권한확인#####
        auth_check = approval_information.objects.get(description="Approved", division="PM Period")
        if auth != auth_check.code_no:
    #####equip info 정보 보내기#####
            equipinfo = equiplist.objects.filter(controlno=controlno)
    #####권한 오류 메세지#####
            messages.error(request, "You do not have permission to approve.")
            p_signal = "OY"
            #####CONTEXT#####
            context = {"equiplists": equiplists, "equipinfo": equipinfo, "score_f": score_f, "score_y": score_y,
                       "score_result": score_result,
                       "pmreason": pmreason, "pmok": pmok, "ra_result": ra_result, "loginid": loginid, "p_name": p_name,
                       "p_date": p_date, "p_signal": p_signal,"selecttext":selecttext,"searchtext":searchtext}
            context.update(users)
            return render(request, 'pmra_write.html', context)  # templates 내 html연결
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
    #####작성자 정보 보내기#####
        a_name = username
        today = date.datetime.today()
        a_date = "20" + today.strftime('%y') + "-"+ today.strftime('%m') + "-" + today.strftime('%d')
    #####데이터 저장#####
        equip_data = equiplist.objects.get(controlno=controlno)  # 컨트롤넘버 일치되는 값 찾기
        equip_data.pmresult = pmreason
        equip_data.pmok = pmok
        equip_data.score_y = score_y
        equip_data.score_f = score_f
        equip_data.pmscore = score_result
        equip_data.ra = ra_result
        equip_data.p_name = p_name
        equip_data.p_date = p_date
        equip_data.a_name = a_name
        equip_data.a_date = a_date
        equip_data.status = "Complete"
        equip_data.save()
    #####status변경#####
        try:
            ra_status= controlformlist.objects.get(controlno=controlno, recent_y="Y")
            ra_status.status="Review" #기존버전 RECENT값 Y로 바꾸기
            ra_status.save()
        except:
            if [equip_data.pmok][0] == "Y":
    #####데이터 컨트롤 폼으로 내보내기#####
                controlformlist(  # 컨트롤폼에 신규등록하기
                    controlno = controlno,  # 컨트롤넘버
                    team = equip_data.team, # 팀명
                    name = equip_data.name, # 설비명
                    revno = "0",
                    recent_y="Y",
                ).save()
        #####등록완료 메세지#####
        messages.error(request, "Approval has been completed.")  # 등록완료
        p_signal="OO"
    #####CONTEXT#####
        context = { "equiplists": equiplists, "equipinfo": equipinfo, "score_f":score_f, "score_y":score_y, "score_result":score_result,
                    "pmreason": pmreason, "pmok": pmok, "ra_result":ra_result,"loginid":loginid, "p_name":p_name, "p_date":p_date
                    , "a_name":a_name, "a_date":a_date,"p_signal":p_signal,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmra_write.html', context)  # templates 내 html연결

####################
####PM EQUIP SCH####
####################

def pmequipsch_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        pmmasterlists = pmmasterlist.objects.all().order_by('team', 'controlno')  # db
    ####테이블 감추기 신호####
        table_signal = "table_signal"
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "team":
                    equipmentlist = equiplist.objects.filter(team__icontains=searchtext, pmok = "Y").order_by('team', 'name')  # db 동기화
                elif selecttext == "control_no":
                    equipmentlist = equiplist.objects.filter(controlno__icontains=searchtext, pmok = "Y").order_by('team','name')  # db 동기화
                elif selecttext == "equipname":
                    equipmentlist = equiplist.objects.filter(name__icontains=searchtext, pmok = "Y").order_by('team', 'name')  # db 동기화
                else:
                    equipmentlist = equiplist.objects.filter(pmok = "Y").order_by('team','name')  # db 동기화
            except:
                    equipmentlist = equiplist.objects.filter(pmok="Y").order_by('team', 'name')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "team":
                    equipmentlist = equiplist.objects.filter(team=userteam, team__icontains=searchtext, pmok = "Y").order_by('team', 'name')  # db 동기화
                elif selecttext == "control_no":
                    equipmentlist = equiplist.objects.filter(team=userteam, controlno__icontains=searchtext, pmok = "Y").order_by('team','name')  # db 동기화
                elif selecttext == "equipname":
                    equipmentlist = equiplist.objects.filter(team=userteam, name__icontains=searchtext, pmok = "Y").order_by('team', 'name')  # db 동기화
                else:
                    equipmentlist = equiplist.objects.filter(team=userteam, pmok = "Y").order_by('team','name')  # db 동기화
            except:
                    equipmentlist = equiplist.objects.filter(team=userteam, pmok="Y").order_by('team', 'name')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        context = {"pmmasterlists": pmmasterlists, "loginid": loginid, "equipmentlist": equipmentlist,
                   "table_signal": table_signal, "selecttext": selecttext, "searchtext": searchtext}
        context.update(users)
        return render(request, 'pmequipsch_main.html', context)  # templates 내 html연결

def pmequipsch_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####완료 시그널 주기#####
        comp_signal = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if (user_div == "Engineer") or (user_div == "SO Manager") or (user_div == "QA Manager"):
            try:
                if selecttext == "team":
                    equipmentlist = equiplist.objects.filter(team__icontains=searchtext, pmok="Y").order_by('team',
                                                                                                            'name')  # db 동기화
                elif selecttext == "control_no":
                    equipmentlist = equiplist.objects.filter(controlno__icontains=searchtext, pmok="Y").order_by('team',
                                                                                                                 'name')  # db 동기화
                elif selecttext == "equipname":
                    equipmentlist = equiplist.objects.filter(name__icontains=searchtext, pmok="Y").order_by('team',
                                                                                                            'name')  # db 동기화
                else:
                    equipmentlist = equiplist.objects.filter(pmok="Y").order_by('team', 'name')  # db 동기화
            except:
                equipmentlist = equiplist.objects.filter(pmok="Y").order_by('team', 'name')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "team":
                    equipmentlist = equiplist.objects.filter(team=userteam, team__icontains=searchtext, pmok="Y").order_by(
                        'team', 'name')  # db 동기화
                elif selecttext == "control_no":
                    equipmentlist = equiplist.objects.filter(team=userteam, controlno__icontains=searchtext,
                                                             pmok="Y").order_by('team', 'name')  # db 동기화
                elif selecttext == "equipname":
                    equipmentlist = equiplist.objects.filter(team=userteam, name__icontains=searchtext, pmok="Y").order_by(
                        'team', 'name')  # db 동기화
                else:
                    equipmentlist = equiplist.objects.filter(team=userteam, pmok="Y").order_by('team', 'name')  # db 동기화
            except:
                equipmentlist = equiplist.objects.filter(team=userteam, pmok="Y").order_by('team', 'name')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="Y")
        pmsch_info = pm_sch.objects.filter(controlno=controlno).order_by('date','pmsheetno')
        context = {"equipmentlist":equipmentlist,"loginid":loginid,"equipinfo":equipinfo,"equipinforev":equipinforev,
                    "comp_signal":comp_signal, "selecttext": selecttext, "searchtext": searchtext,
                   "pmsch_info":pmsch_info}
        context.update(users)
        return render(request, 'pmequipsch_main.html', context) #templates 내 html연결

def pm_fullscreen(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        pmcode = request.POST.get('pmcode')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        #####완료 시그널 주기#####
        pm_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if pm_comp.status == "Performed" or pm_comp.status == "Reviewed"  or pm_comp.status == "Complete" :
            comp_signal = "Y"
        else:
            comp_signal = "N"
        #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode)
        pmchecksheet_result = pmchecksheet.objects.filter(pmcode=pmcode)
        pmchecksheet_before = pmmasterlist.objects.filter(sheetno = pmsheetno, pm_y_n="Y")
        context = {"loginid": loginid,"equipinfo": equipinfo, "equipinforev": equipinforev,
                   "pmchecksheet_result":pmchecksheet_result,"comp_signal":comp_signal,
                   "pmchecksheet_before":pmchecksheet_before,
                   "pmcode": pmcode,"pmchecksheet_info": pmchecksheet_info}
        context.update(users)
        return render(request, 'pm_fullscreen.html', context) #templates 내 html연결

####################
####PM MONTHLY #####
####################

def pmmonthly_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####검색값 디폴드값 설정#####
        today = date.datetime.today()
        calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####입력정보값 테이블에서 불러오기#####
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid}
        context.update(users)
        return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

def pmmonthly_search(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        calendarsearch = request.POST.get('calendarsearch')  # html 검색일자를 받는다
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
    #####일정 숫자 카운트#####
        table_count = pmmonthly_sch.values('pmsheetno')  # sql문 dataframe으로 변경
        df = pd.DataFrame.from_records(table_count)
        tablelen = len(df.index)  # 일정 숫자로 변환
        context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch,
                   "tablelen":tablelen}
        context.update(users)
        return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

def pmmonthly_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####입력정보값 테이블에서 불러오기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmtable = pmmasterlist.objects.filter(sheetno=pmsheetno, pm_y_n="Y", amd="A").order_by('freq')  # db 동기화
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
    #####일정 숫자 카운트#####
        table_count = pmmonthly_sch.values('pmsheetno')  # sql문 dataframe으로 변경
        df = pd.DataFrame.from_records(table_count)
        tablelen = len(df.index)  # 일정 숫자로 변환
        context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch,
                   "pmtable":pmtable, "equipinfo":equipinfo, "equipinforev":equipinforev, "tablelen":tablelen}
        context.update(users)
        return render(request, 'pmmonthly_view.html', context) #templates 내 html연결

def pmmonthly_plandate(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')   # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        plandate = request.POST.get('plandate')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####데이터 임시저장#####
        pm_sch_save = pm_sch.objects.get(pmcode=pmcode)  # 컨트롤넘버 일치되는 값 찾기
        pm_sch_save.plandate_temp = plandate
        pm_sch_save.save()
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
    #####입력정보값 테이블에서 불러오기#####
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmtable = pmmasterlist.objects.filter(sheetno=pmsheetno, pm_y_n="Y", amd="A").order_by('freq')  # db 동기화
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
        context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch,
                   "pmtable":pmtable, "equipinfo":equipinfo, "equipinforev":equipinforev}
        context.update(users)
        return render(request, 'pmmonthly_view.html', context) #templates 내 html연결

def pmmonthly_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendarsearch = request.POST.get('calendarsearch')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####검색월 디폴트값#####
        if (str(calendarsearch) == "None") or (str(calendarsearch) == ""):
            today = date.datetime.today()
            calendarsearch = "20" + today.strftime('%y') + "-" + today.strftime('%m')
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화

    #####전월 미완료 아이템 있으면 클릭불가#####
        calendar_y = calendarsearch[:4]
        calendar_m = calendarsearch[5:]
        today = date.datetime(int(calendar_y), int(calendar_m), 1)
        before_one_month = today - relativedelta(months=1)
        calendar_chk =  "20" + before_one_month.strftime('%y') + "-" + before_one_month.strftime('%m')
        complete_check_sch = pm_sch.objects.filter(date=calendar_chk) # db 동기화
        complete_check = complete_check_sch.values('status')  # sql문 dataframe으로 변경
        df_complete_check = pd.DataFrame.from_records(complete_check)
        df_complete_check_len = len(df_complete_check.index)  # 일정 숫자로 변환
        for k in range(df_complete_check_len):
            pm_plandate_temp = df_complete_check.iat[k, 0]
            if pm_plandate_temp != "Complete":
                messages.error(request, "Previous month PM was not completed.")  # 미완료 메세지
                context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch}
                context.update(users)
                return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

    #####날짜 미입력한항목 검토하기#####
        pm_count = pmmonthly_sch.values('plandate_temp')  # sql문 dataframe으로 변경
        df = pd.DataFrame.from_records(pm_count)
        pm_count_len = len(df.index)  # 일정 숫자로 변환
        for i in range(pm_count_len):
            pm_plandate_temp = df.iat[i, 0]
            if str(pm_plandate_temp) == "":
                messages.error(request, "Plan date entry is not complete.")  # 미완료 메세지
                pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
                context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch}
                context.update(users)
                return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

    #####날짜 잘못 입력한항목 검토하기#####
        pm_count = pmmonthly_sch.values('plandate_temp')  # sql문 dataframe으로 변경
        df = pd.DataFrame.from_records(pm_count)
        pm_count_len = len(df.index)  # 일정 숫자로 변환
        for i in range(pm_count_len):
            pm_plandate_temp = df.iat[i, 0]
            calendar_y = pm_plandate_temp[:4]
            calendar_m = pm_plandate_temp[5:7]
            date_check = calendar_y + "-" + calendar_m
            if date_check != calendarsearch:
                messages.error(request, "The date was entered incorrectly.")  # 미완료 메세지
                pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
                context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch}
                context.update(users)
                return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

    #####임시 날짜지정값 확정하기#####
        pmmonthly_sch_fixed = pm_sch.objects.filter(date=calendarsearch, status="Not Fixed")  # db 동기화
        pm_plandate_trans = pmmonthly_sch_fixed.values('pmcode')  # sql문 dataframe으로 변경
        df_complete = pd.DataFrame.from_records(pm_plandate_trans)
        pm_complete_len = len(df_complete.index)  # 일정 숫자로 변환
        for j in range(pm_complete_len):
            pmcode = df_complete.iat[j, 0]
            pm_sch_insert = pm_sch.objects.get(pmcode=pmcode)  # 컨트롤넘버 일치되는 값 찾기
            pm_sch_insert.plandate = pm_sch_insert.plandate_temp
            pm_sch_insert.status = "Fixed Date"
            pm_sch_insert.sch_clear = "Y"
            pm_sch_insert.save()
        messages.error(request, "Plan date entry has been completed.")  # 완료 메세지

    #####각팀 슈퍼바이져한테 메일보내기#####

    #####입력정보값 테이블에서 불러오기#####
        pmmonthly_sch = pm_sch.objects.filter(date=calendarsearch).order_by('team', 'roomno')  # db 동기화
        context = {"pmmonthly_sch": pmmonthly_sch, "loginid": loginid, "calendarsearch":calendarsearch}
        context.update(users)
        return render(request, 'pmmonthly_main.html', context) #templates 내 html연결

##################
####PMCALENDAR####
##################

def pmcalendar_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ####calendar_default값#####
        today = date.datetime.today()
        calendar_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        calendar_day = today.strftime('%d')
        calendar_month = today.strftime('%m')
    #####월 영어로 바꾸기####
        if int(calendar_month) == 1:
            calendar_month = "January"
        elif int(calendar_month) == 2:
            calendar_month = "February"
        elif int(calendar_month) == 3:
            calendar_month = "March"
        elif int(calendar_month) == 4:
            calendar_month = "April"
        elif int(calendar_month) == 5:
            calendar_month = "May"
        elif int(calendar_month) == 6:
            calendar_month = "June"
        elif int(calendar_month) == 7:
            calendar_month = "July"
        elif int(calendar_month) == 8:
            calendar_month = "August"
        elif int(calendar_month) == 9:
            calendar_month = "September"
        elif int(calendar_month) == 10:
            calendar_month = "October"
        elif int(calendar_month) == 11:
            calendar_month = "November"
        else:
            calendar_month = "December"
    #####equip info 정보 보내기#####
        pmchecksheet_info = pm_sch.objects.filter(plandate=calendar_date)
        context = {"loginid": loginid, "calendar_date": calendar_date, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_month":calendar_month, "calendar_day":calendar_day}
        context.update(users)
        return render(request, 'pmcalendar_main.html', context) #templates 내 html연결

def pmcalendar_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_day = request.POST.get('calendar_day')  # html에서 해당 값을 받는다
        calendar_month = request.POST.get('calendar_month')  # html에서 해당 값을 받는다
        calendar_year = request.POST.get('calendar_year')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        if str(calendar_day) == "":
            context = {"loginid":loginid}
            context.update(users)
            return render(request, 'pmcalendar_view.html', context) #templates 내 html연결
    #####기본정보값 보내기####
        if int(calendar_day) < 10:
            calendar_day = "0" + str(calendar_day)
        if int(calendar_month) < 10:
            calendar_month = "0" + str(calendar_month)
        calendar_date = str(calendar_year) + "-" +str(calendar_month) + "-" +str(calendar_day)
    #####테이블 카운트 계산하기####
        df_team_info = pm_sch.objects.filter(plandate=calendar_date).values('team').annotate(Count('team'))
    #####월 영어로 바꾸기####
        if int(calendar_month) == 1:
            calendar_month = "January"
        elif int(calendar_month) == 2:
            calendar_month = "February"
        elif int(calendar_month) == 3:
            calendar_month = "March"
        elif int(calendar_month) == 4:
            calendar_month = "April"
        elif int(calendar_month) == 5:
            calendar_month = "May"
        elif int(calendar_month) == 6:
            calendar_month = "June"
        elif int(calendar_month) == 7:
            calendar_month = "July"
        elif int(calendar_month)  == 8:
            calendar_month = "August"
        elif int(calendar_month)  == 9:
            calendar_month = "September"
        elif int(calendar_month) == 10:
            calendar_month = "October"
        elif int(calendar_month)  == 11:
            calendar_month = "November"
        else :
            calendar_month = "December"
    #####equip info 정보 보내기#####
        pmchecksheet_info = pm_sch.objects.filter(plandate=calendar_date)
        context = {"loginid":loginid, "calendar_date":calendar_date,"pmchecksheet_info":pmchecksheet_info,
                   "calendar_month":calendar_month, "calendar_day":calendar_day,"df_team_info":df_team_info}
        context.update(users)
        return render(request, 'pmcalendar_view.html', context) #templates 내 html연결

def pmcalendar_write(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html에서 해당 값을 받는다
        pmsheetno = request.POST.get('pmsheetno')  # html에서 해당 값을 받는다
        pmcode = request.POST.get('pmcode')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        table_signal = request.POST.get('table_signal')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####PM CHECK SHEET DB로 보내기#####
        pmchecksheet_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        check = [pmchecksheet_check.pmchecksheet_y_n][0]
        if check == "N":
    #####pm_sch db에 있는 항목 보내기#####
            pmchecksheet_date_insert = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            date_insert = [pmchecksheet_date_insert.date][0]
            pmcode_insert = [pmchecksheet_date_insert.pmcode][0]
    #####pmmasterlist db에 있는 항목 보내기#####
            pmchecksheet_insert = pmmasterlist.objects.filter(sheetno=pmsheetno, pm_y_n="Y", amd="A")  # 컨트롤넘버 일치되는 값 찾기
            pmchecksheet_insert = pmchecksheet_insert.values('itemcode')
            df_pmchecksheet_insert = pd.DataFrame.from_records(pmchecksheet_insert)
            df_pmchecksheet_insert_len = len(df_pmchecksheet_insert.index)  # itemcode 하나씩 넘기기
            for j in range(df_pmchecksheet_insert_len):
                itemcode_insert = df_pmchecksheet_insert.iat[j, 0]
                pmchecksheet_get = pmmasterlist.objects.get(itemcode=itemcode_insert, pm_y_n="Y")
                pmchecksheet(
                    team=pmchecksheet_get.team,
                    controlno=pmchecksheet_get.controlno,
                    pmsheetno=pmsheetno,
                    date=date_insert,
                    pmcode=pmcode_insert,
                    itemcode=pmchecksheet_get.itemcode,
                    item=pmchecksheet_get.item,
                    check=pmchecksheet_get.check,
                ).save()
    #####pm_sch db에 반영완료 체크하기#####
        pmchecksheet_y_n_insert = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_y_n_insert.pmchecksheet_y_n = "Y"
        pmchecksheet_y_n_insert.save()
    #####승인요청여부 확인하기#####
        comp_signal_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        comp_signal_check = comp_signal_check.status
        if comp_signal_check != "Fixed Date":
            comp_signal = "Y"
        else:
            comp_signal = "N"
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
             url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        pmchecksheet_info = pm_sch.objects.filter(plandate=calendar_date, pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"loginid":loginid, "calendar_date":calendar_date,"pmchecksheet_info":pmchecksheet_info,
                   "equipinforev":equipinforev,"equipinfo":equipinfo, "plandate":plandate,"actiondate":actiondate,
                   "remark_get":remark_get,"pmchecksheets":pmchecksheets,"comp_signal":comp_signal,
                   "pmchecksheet_list":pmchecksheet_list,"pmcode":pmcode,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"table_signal":table_signal,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context) #templates 내 html연결


def pmcalendar_checkresult(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        checkresult = request.POST.get('checkresultreturn')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.result_temp = checkresult
        pmchecksheet_write.save()
        #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
        #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date,"pmchecksheet_list":pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결


def pmcalendar_actiondetail(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        actiondetail = request.POST.get('actiondetailreturn')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
        pass_y = request.POST.get('pass_y')  # html 날짜 값을 받는다
        fail_y = request.POST.get('fail_y')  # html 날짜 값을 받는다
        fail_n = request.POST.get('fail_n')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.actiondetail_temp = actiondetail
        pmchecksheet_write.pass_y_temp = pass_y
        pmchecksheet_write.fail_y_temp = fail_y
        pmchecksheet_write.fail_n_temp = fail_n
        pmchecksheet_write.save()
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_checkboxform(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        pass_y = request.POST.get('pass_y')  # html 날짜 값을 받는다
        fail_y = request.POST.get('fail_y')  # html 날짜 값을 받는다
        fail_n = request.POST.get('fail_n')  # html 날짜 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####체크시트 결과값 입시에 입력#####
        pmchecksheet_write = pmchecksheet.objects.get(itemcode=itemcode, pmcode=pmcode)
        pmchecksheet_write.pass_y_temp = pass_y
        pmchecksheet_write.fail_y_temp = fail_y
        pmchecksheet_write.fail_n_temp = fail_n
        pmchecksheet_write.save()
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_remark(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
        remarkreturn = request.POST.get('remarkreturn')  # html 날짜 값을 받는다
        remark_na = request.POST.get('remark_na')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####리마크 입력시에 입력#####
        pmchecksheet_remark = pm_sch.objects.get(pmcode=pmcode)
        pmchecksheet_remark.remark_temp = remarkreturn
        pmchecksheet_remark.remark_na_temp = remark_na
        pmchecksheet_remark.save()
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_remark_na(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####리마크 입력시에 입력#####
        pmchecksheet_remark = pm_sch.objects.get(pmcode=pmcode)
        pmchecksheet_remark.remark_temp = "N/A"
        pmchecksheet_remark.remark_na_temp = "checked"
        pmchecksheet_remark.save()
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####체크박스 수량 일치확인#####
        total_count = pmchecksheet.objects.filter(pmcode=pmcode)
        total_count = total_count.values('item')
        df_total_count = pd.DataFrame.from_records(total_count)
        total_len = len(df_total_count.index)
        pmcheckitem_count = pmchecksheet.objects.filter(pmcode=pmcode)
        pmcheckitem_count = pmcheckitem_count.values()
        df_pmcheckitem_count = pd.DataFrame.from_records(pmcheckitem_count)
        df_pass_y_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['pass_y_temp'] == "checked"]
        pass_y_len = len(df_pass_y_count.index)
        df_fail_y_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['fail_y_temp'] == "checked"]
        fail_y_len = len(df_fail_y_count.index)
        df_fail_n_count = df_pmcheckitem_count.loc[df_pmcheckitem_count['fail_n_temp'] == "checked"]
        fail_n_len = len(df_fail_n_count.index)
        if int(total_len) != int(pass_y_len) + int(fail_y_len) + int(fail_n_len):
            messages.error(request, "There are entries not entered.")  # 경고
            #####equip info 정보 보내기#####
            spare_list = spare_out.objects.filter(used_y_n=pmcode)
            equipinfo = equiplist.objects.filter(controlno=controlno)
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
            pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
            pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
            plandate = pm_plandate.plandate
            actiondate = pm_plandate.actiondate
            remark_get = pm_plandate.remark_temp
            context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                       "actiondate": actiondate,"spare_list":spare_list,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                       "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp,"selecttext":selecttext,
                   "searchtext":searchtext}
            context.update(users)
            return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결
    #####fail_y 입력 시 repair입력 여부 확인#####
        for k in range(total_len):
            fail_y_ckeck = df_pmcheckitem_count.iat[k,18]
            if fail_y_ckeck == "checked":
                fail_y_ckeck = df_pmcheckitem_count.iat[k,20]
                if fail_y_ckeck == "":
                    messages.error(request, "Repair Detail has not been entered.")  # 경고
                    #####equip info 정보 보내기#####
                    spare_list = spare_out.objects.filter(used_y_n=pmcode)
                    equipinfo = equiplist.objects.filter(controlno=controlno)
                    equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
                    pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
                    pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
                    pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
                    plandate = pm_plandate.plandate
                    actiondate = pm_plandate.actiondate
                    remark_get = pm_plandate.remark_temp
                    context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                               "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                               "actiondate": actiondate,"spare_list":spare_list,
                               "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                               "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp
                                ,"selecttext": selecttext,"searchtext": searchtext}
                    context.update(users)
                    return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결
    #####fail_n 입력 시 workrequest입력 여부 확인#####
        for m in range(total_len):
            fail_y_ckeck = df_pmcheckitem_count.iat[m,19]
            if fail_y_ckeck == "checked":
                fail_y_ckeck = df_pmcheckitem_count.iat[m,22]
                if fail_y_ckeck == "":
                    messages.error(request, "Work Request has not been received.")  # 경고
                    #####equip info 정보 보내기#####
                    spare_list = spare_out.objects.filter(used_y_n=pmcode)
                    equipinfo = equiplist.objects.filter(controlno=controlno)
                    equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
                    pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
                    pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
                    pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
                    plandate = pm_plandate.plandate
                    actiondate = pm_plandate.actiondate
                    remark_get = pm_plandate.remark_temp
                    context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                               "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                               "actiondate": actiondate,"spare_list":spare_list,
                               "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                               "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp
                                ,"selecttext": selecttext, "searchtext": searchtext}
                    context.update(users)
                    return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결
    #####Remark 미입력 확인#####
        remark_check = pm_sch.objects.get(pmcode=pmcode)
        if remark_check.remark_temp == "":
           if remark_check.remark_na_temp =="":
               messages.error(request, "Remark was not entered.")  # 경고
               #####equip info 정보 보내기#####
               spare_list = spare_out.objects.filter(used_y_n=pmcode)
               equipinfo = equiplist.objects.filter(controlno=controlno)
               equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
               pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
               pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
               pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
               plandate = pm_plandate.plandate
               actiondate = pm_plandate.actiondate
               remark_get = pm_plandate.remark_temp
               context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                          "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                          "actiondate": actiondate,
                          "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                          "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"url_comp":url_comp
                          , "selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
               context.update(users)
               return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결
    #####입력날짜 받기#####
        today = date.datetime.today()
        submit_date = "20" + today.strftime('%y') + "-" + today.strftime('%m')+ "-" + today.strftime('%d')
    #####엑션데이터 저장하기#####
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pm_plandate.actiondate_temp = submit_date
        pm_plandate.status = "Performed"
        pm_plandate.p_name = username
        pm_plandate.p_date = submit_date
        pm_plandate.save()
    #####입력완료창으로 변경#####
        comp_signal = "Y"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"comp_signal":comp_signal,
                   "url_comp":url_comp,"selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_return(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
    #####입력정보값 받기#####
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        calendar_date = request.POST.get('calendar_date')  # html 날짜 값을 받는다
        controlno = request.POST.get('controlno')  # html 날짜 값을 받는다
        pmcode = request.POST.get('pmcode')  # html 날짜 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #####첨부파일 시그널 주기#####
        url_comp = "N"
    #####결재 확인하기#####
        status_check = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        status_check = status_check.status
        if status_check != "Performed":
            #####승인요청여부 확인하기#####
            comp_signal = "Y"
            messages.error(request, "PM Check Sheet that have been approved cannot be returned.")  # 경고
            #####equip info 정보 보내기#####
            spare_list = spare_out.objects.filter(used_y_n=pmcode)
            equipinfo = equiplist.objects.filter(controlno=controlno)
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
            pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
            pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
            pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
            plandate = pm_plandate.plandate
            actiondate = pm_plandate.actiondate
            remark_get = pm_plandate.remark_temp
            context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                       "actiondate": actiondate,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                       "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"spare_list":spare_list,
                       "comp_signal": comp_signal,"url_comp":url_comp,"selecttext": selecttext, "searchtext": searchtext}
            context.update(users)
            return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결
    #####승인요청여부 확인하기#####
        comp_signal = "N"
    #####pm_sch status 변경하기#####
        status_change = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        status_change.status = "Fixed Date"
        status_change.actiondate_temp = "Not Checked"
        status_change.p_name = ""
        status_change.p_date = ""
        status_change.save()
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid,
                   "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate, "actiondate": actiondate,
                   "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                   "calendar_date": calendar_date, "pmchecksheet_list": pmchecksheet_list,"comp_signal":comp_signal
                    ,"url_comp": url_comp,"selecttext": selecttext, "searchtext": searchtext,"spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)  # templates 내 html연결

def pmcalendar_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get("controlno")
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        pmcode = request.POST.get("pmcode")
        calendar_date = request.POST.get('calendar_date')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "status":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, status__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "team":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, team__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "control_no":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date, controlno__icontains=searchtext).order_by(
                    'team')
            elif selecttext == "equipname":
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date,name__icontains=searchtext).order_by('team')
            else:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        except:
                pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date).order_by('team')
        if str(searchtext) == "None":
                searchtext = ""
    #################파일업로드하기##################
        if "upload_file" in request.FILES:
                # 파일 업로드 하기!!!
           upload_file = request.FILES["upload_file"]
           fs = FileSystemStorage()
           name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
                    # 파일 읽어오기!!!
           url = fs.url(name)
        else:
            file_name = "-"
    #################파일업로드url저장하기##################
        attach_change = pm_sch.objects.get(pmcode=pmcode)  #
        attach_change.attach_temp = url
        attach_change.save()
    #####첨부파일 시그널 주기#####
        url_comp = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        if url_comp.attach_temp == "N/A":
            url_comp = "N"
        elif str(url_comp.attach_temp) == "None":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####승인요청여부 확인하기#####
            comp_signal = "N"
    #####equip info 정보 보내기#####
        spare_list = spare_out.objects.filter(used_y_n=pmcode)
        equipinfo = equiplist.objects.filter(controlno=controlno)
        equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        pmchecksheets = pmchecksheet.objects.filter(pmcode=pmcode)
        pm_plandate = pm_sch.objects.get(pmcode=pmcode)  # plandate 보내기
        pmchecksheet_info = pm_sch.objects.filter(pmcode=pmcode, plandate=calendar_date)
        pmchecksheet_list = pm_sch.objects.filter(plandate=calendar_date)
        plandate = pm_plandate.plandate
        actiondate = pm_plandate.actiondate
        remark_get = pm_plandate.remark_temp
        context = {"pmchecksheets": pmchecksheets, "loginid": loginid, "pmchecksheet_list": pmchecksheet_list,
                       "equipinfo": equipinfo, "equipinforev": equipinforev, "plandate": plandate,
                       "actiondate": actiondate,'url_comp': url_comp,"comp_signal":comp_signal,
                       "pmcode": pmcode, "remark_get": remark_get, "pmchecksheet_info": pmchecksheet_info,
                       "calendar_date": calendar_date,"selecttext": selecttext, "searchtext": searchtext,
                        "spare_list":spare_list}
        context.update(users)
        return render(request, 'pmcalendar_write.html', context)

######################
####PM MASTER LIST####
######################

def pmmasterlist_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        if selecttext == "team":
            pmmasterlists = pmmasterlist.objects.filter(team__icontains=searchtext, pm_y_n="Y").order_by('team','sheetno') #db 동기화
        elif selecttext == "controlno":
            pmmasterlists = pmmasterlist.objects.filter(controlno__icontains=searchtext, pm_y_n="Y").order_by('team','sheetno') #db 동기화
        elif selecttext == "equipname":
            pmmasterlists = pmmasterlist.objects.filter(name__icontains=searchtext, pm_y_n="Y").order_by('team','sheetno') #db 동기화
        elif selecttext == "item":
            pmmasterlists = pmmasterlist.objects.filter(item__icontains=searchtext, pm_y_n="Y").order_by('team','sheetno') #db 동기화
        elif selecttext == "pmsheetno":
            pmmasterlists = pmmasterlist.objects.filter(sheetno__icontains=searchtext, pm_y_n="Y").order_by('team','sheetno') #db 동기화
        else:
            pmmasterlists = pmmasterlist.objects.filter(pm_y_n="Y").order_by('team','sheetno') #db 동기화
        context = {"pmmasterlists":pmmasterlists, "loginid":loginid}
        context.update(users)
        return render(request, 'pmmasterlist_main.html', context) #templates 내 html연결

####PM CONTROL FORM Approval####
def pmapproval_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                  'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    ####테이블 감추기 신호####
        table_signal = "table_signal"
        context = {"controlformlists":controlformlists,"loginid":loginid, "table_signal":table_signal}
        context.update(users)
        return render(request, 'pmapproval_main.html', context) #templates 내 html연결

def pmapproval_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb = pmmasterlist_temp.objects.filter(controlno = controlno).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="A")
    #####Reviewd 칸 status 변경하기#####
        r_name_date = controlformlist.objects.get(controlno = controlno, recent_y="A")
        r_name_signal = str(r_name_date.r_name_temp)
        r_date_signal = r_name_date.r_date_temp
        context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                   "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet":pmsheet,
                   "r_name_signal": r_name_signal, "r_date_signal": r_date_signal}
        context.update(users)
        return render(request, 'pmapproval_main.html', context)  # templates 내 html연결

def pmapproval_check_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb = pmmasterlist_temp.objects.filter(controlno = controlno).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    #####equip info 정보 보내기#####
        equipinfo = equiplist.objects.filter(controlno = controlno)
        equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="A")
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Reviewed", division="PM Control Form")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            r_name_date = controlformlist.objects.get(controlno=controlno, recent_y="A")
            r_name_signal = str(r_name_date.r_name_temp)
            r_date_signal = r_name_date.r_date_temp
            context = {"controlformdb": controlformdb, "controlformlists": controlformlists, "equipinfo": equipinfo,
                       "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet": pmsheet,
                       "r_name_signal": r_name_signal, "r_date_signal": r_date_signal}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결
        else:
    #####Reviewed 업데이트#####
        #####r_name / r_date 받기#####
            r_name = username
            today = date.datetime.today()
            r_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        #####값저장하기#####
            status_return = controlformlist.objects.get(controlno=controlno, recent_y="A")  # 컨트롤넘버 일치되는 값 찾기
            status_return.status = "Reviewed"
            status_return.r_name_temp = r_name
            status_return.r_date_temp = r_date
            status_return.save()
        #####Reviewd 칸 status 변경하기#####
            r_name_signal = status_return.r_name_temp
            r_date_signal = status_return.r_date_temp
            context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                       "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet":pmsheet,
                       "r_name_signal":r_name_signal,"r_date_signal":r_date_signal}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결

def pmapproval_check_reject(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb = pmmasterlist_temp.objects.filter(controlno = controlno).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Reviewed", division="PM Control Form")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            r_name_date = controlformlist.objects.get(controlno=controlno, recent_y="A")
            r_name_signal = str(r_name_date.r_name_temp)
            r_date_signal = r_name_date.r_date_temp
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="A")
            equipinfo = equiplist.objects.filter(controlno=controlno)
            context = {"controlformdb": controlformdb, "controlformlists": controlformlists, "equipinfo": equipinfo,
                       "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet": pmsheet,
                       "r_name_signal": r_name_signal, "r_date_signal": r_date_signal}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결
        else:
    #####equip info 정보 보내기#####
            equipinfo = equiplist.objects.filter(controlno = controlno)
            equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="A")
    #####반려하여 값 뒤로 빼기#####
            status_return = controlformlist.objects.get(controlno=controlno, recent_y="A")  # 컨트롤넘버 일치되는 값 찾기
            status_return.status = "Reject"
            status_return.p_name =""
            status_return.p_date =""
            status_return.save()
            context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                       "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet":pmsheet}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결

def pmapproval_approved_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb = pmmasterlist_temp.objects.filter(controlno = controlno).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Approved", division="PM Control Form")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            r_name_date = controlformlist.objects.get(controlno=controlno, recent_y="A")
            r_name_signal = str(r_name_date.r_name_temp)
            r_date_signal = r_name_date.r_date_temp
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="A")
            equipinfo = equiplist.objects.filter(controlno=controlno)
            context = {"controlformdb": controlformdb, "controlformlists": controlformlists, "equipinfo": equipinfo,
                       "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet": pmsheet,
                       "r_name_signal": r_name_signal, "r_date_signal": r_date_signal}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결
        else:
        #####equip info 정보 보내기#####
            equipinfo = equiplist.objects.filter(controlno=controlno)
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="Y")
        #####a_name / a_date 받기#####
            a_name = username
            today = date.datetime.today()
            a_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        #####값저장하기#####
            #####초기값 삭제
            status_delete = controlformlist.objects.get(controlno=controlno, recent_y="Y")  # 컨트롤넘버 일치되는 값 찾기
            status_delete.status = "Complete"
            status_delete.recent_y = "N"
            status_delete.save()
        #####업데이트
            status_return = controlformlist.objects.get(controlno=controlno, recent_y="A")  # 컨트롤넘버 일치되는 값 찾기
            status_return.status = "Complete"
            status_return.r_name = status_return.r_name_temp
            status_return.r_date = status_return.r_date_temp
            status_return.r_name_temp = ""
            status_return.r_date_temp = ""
            status_return.a_name = a_name
            status_return.a_date = a_date
            status_return.revno = int(status_return.revno) + 1
            status_return.revdate = a_date
            status_return.recent_y = "Y"
            status_return.save()
        #####itemcode 변경일 최신화#####
            pmmasterlist_date = pmmasterlist_temp.objects.filter(startdate="New", controlno=controlno)  # 컨트롤넘버 일치되는 값 찾기
            startdate_send = pmmasterlist_date.values('itemcode')
            df_date = pd.DataFrame.from_records(startdate_send)
            df_date_len = len(df_date.index)  #itemcode 하나씩 넘기기
            for j in range(df_date_len):
                startdate_change = df_date.iat[j, 0]
                startdate_change = pmmasterlist_temp.objects.get(itemcode=startdate_change)
                startdate_change.startdate = a_date
                startdate_change.save()
        #####임시값 pmmasterlist_temp rev값 업데이트하기#####
            pmmasterlist_send = pmmasterlist_temp.objects.filter(controlno=controlno)  # 컨트롤넘버 일치되는 값 찾기
            itemcode_send = pmmasterlist_send.values('itemcode')
            df = pd.DataFrame.from_records(itemcode_send)
            dflen = len(df.index)  #itemcode 하나씩 넘기기
            for l in range(dflen):
                itemcode = df.iat[l, 0]
                pmmasterlist_rev = pmmasterlist_temp.objects.get(itemcode=itemcode)  # 컨트롤넘버 일치되는 값 찾기
                pmmasterlist_rev.revno = int(pmmasterlist_rev.revno) + 1
                pmmasterlist_rev.date = a_date
                pmmasterlist_rev.save()
        #####과거 버전 PM_Y_N 값 변경하기#####
            pmmasterlist_pm_y_n = pmmasterlist.objects.filter(controlno=controlno, pm_y_n="Y")  # 컨트롤넘버 일치되는 값 찾기
            pm_y_n_send = pmmasterlist_pm_y_n.values('itemcode')
            df_pm_y_n_send = pd.DataFrame.from_records(pm_y_n_send)
            df_pm_y_n_send_len = len(df_pm_y_n_send.index)  #itemcode 하나씩 넘기기
            for m in range(df_pm_y_n_send_len):
                itemcode = df_pm_y_n_send.iat[m, 0]
                pm_y_n_pm = pmmasterlist.objects.get(itemcode=itemcode, pm_y_n="Y")  # 컨트롤넘버 일치되는 값 찾기
                pm_y_n_pm.pm_y_n = "N"
                pm_y_n_pm.save()
        #####임시값 본값에 보내기_pmmasterlist#####
            pmmasterlist_send = pmmasterlist_temp.objects.filter(controlno=controlno)  # 컨트롤넘버 일치되는 값 찾기
            itemcode_send = pmmasterlist_send.values('itemcode')
            df = pd.DataFrame.from_records(itemcode_send)
            dflen = len(df.index)  #itemcode 하나씩 넘기기
            for k in range(dflen):
                itemcode = df.iat[k, 0]
                pmmasterlist_insert = pmmasterlist_temp.objects.get(itemcode=itemcode)  # 컨트롤넘버 일치되는 값 찾기
                pmmasterlist(  # 컨트롤폼에 신규등록하기
                    team=pmmasterlist_insert.team,  # 팀명
                    controlno=pmmasterlist_insert.controlno,  # 컨트롤넘버
                    name=pmmasterlist_insert.name,  # 설비명
                    model=pmmasterlist_insert.model,  # 모델명
                    serial=pmmasterlist_insert.serial,  # 시리얼넘버
                    maker=pmmasterlist_insert.maker,  # 제조사
                    roomname=pmmasterlist_insert.roomname,  # 룸명
                    roomno=pmmasterlist_insert.roomno,  # 룸넘버
                    revno=status_return.revno,  # 리비젼넘버
                    date=a_date,  # 리비젼날짜
                    freq=pmmasterlist_insert.freq,  # 주기
                    ra=pmmasterlist_insert.ra,  # ra결과
                    sheetno=pmmasterlist_insert.sheetno,  # 시트넘버
                    amd=pmmasterlist_insert.amd,  # a/m/d
                    itemno=pmmasterlist_insert.itemno,  # 순번
                    item=pmmasterlist_insert.item,  # 점검내용
                    check=pmmasterlist_insert.check,  # 점검기준
                    startdate=pmmasterlist_insert.startdate,  # 시트시작일
                    change=pmmasterlist_insert.change,  # 변경사유
                    itemcode=pmmasterlist_insert.itemcode,  # 점검내용 구분좌
                    division=pmmasterlist_insert.division,
                    pm_y_n="Y",
                ).save()
        #####pm_sch로 데이터 보내기#####
            pmsheetdb_chk = pmsheetdb.objects.filter(controlno=controlno, startdate="")  # 컨트롤넘버 일치되는 값 찾기
            pmsheetdb_chk = pmsheetdb_chk.values('pmsheetno_temp')
            df_pmsheetdb_chk = pd.DataFrame.from_records(pmsheetdb_chk)
            df_pmsheetdb_chk_len = len(df_pmsheetdb_chk.index)  #itemcode 하나씩 넘기기
            for m in range(df_pmsheetdb_chk_len):
                pmsheetno_chk = df_pmsheetdb_chk.iat[m, 0]
                pmsheetdb_pm_sch= pmsheetdb.objects.get(pmsheetno_temp=pmsheetno_chk)  # pmsheetno_temp 일치되는 값 찾기
                pmsheetdb_controlno = pmsheetdb_pm_sch.controlno # 컨트롤넘버 값 치환
                controlformlist_controlno = controlformlist.objects.get(controlno=pmsheetdb_controlno, recent_y="Y")  # 컨트롤넘버 일치되는 값 찾기
                equiplist_controlno = equiplist.objects.get(controlno=pmsheetdb_controlno)  # 컨트롤넘버 일치되는 값 찾기
                pm_sch(  # pm_sch에 신규등록하기
                        team=controlformlist_controlno.team,  # 팀명
                        pmsheetno=pmsheetdb_pm_sch.pmsheetno_temp,  # 설비명
                        pmcode=pmsheetdb_pm_sch.pmsheetno_temp+ "/" + pmsheetdb_pm_sch.startdate_temp,  # pmcode
                        revno=controlformlist_controlno.revno,  # 시리얼넘버
                        revdate=controlformlist_controlno.revdate,  # 설비명
                        controlno=controlformlist_controlno.controlno,  # 컨트롤넘버
                        name=controlformlist_controlno.name,  # 모델명
                        roomno=equiplist_controlno.roomno,  # 시리얼넘버
                        roomname=equiplist_controlno.roomname,  # 모델명
                        date=pmsheetdb_pm_sch.startdate_temp,  # 시리얼넘버
                    ).save()
        #####임시값 본값에 보내기_pmsheetdb#####
            pmsheetdb_send = pmsheetdb.objects.filter(controlno=controlno, startdate="")  # 컨트롤넘버 일치되는 값 찾기
            pmsheetdb_send = pmsheetdb_send.values('pmsheetno_temp')
            df_pmsheetdb = pd.DataFrame.from_records(pmsheetdb_send)
            df_pmsheetdb_len = len(df_pmsheetdb.index)  #itemcode 하나씩 넘기기
            for i in range(df_pmsheetdb_len):
                pmsheetno_temp = df_pmsheetdb.iat[i, 0]
                pmsheetdb_insert = pmsheetdb.objects.get(pmsheetno_temp=pmsheetno_temp)  # 컨트롤넘버 일치되는 값 찾기
                pmsheetdb_insert.pmsheetno=[pmsheetdb_insert.pmsheetno_temp][0]
                pmsheetdb_insert.startdate=[pmsheetdb_insert.startdate_temp][0]
                pmsheetdb_insert.freq=[pmsheetdb_insert.freq_temp][0]
                pmsheetdb_insert.filter_check="Y"
                pmsheetdb_insert.save()
        #####Reviewed 칸 status 변경하기#####
            r_name_date = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            r_name_signal = r_name_date.r_name
            r_date_signal = r_name_date.r_date
        #####rev no. 미완료 항목 전부 업데이트하기#####
            revno_revdate = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            revno_trans = [revno_revdate.revno][0]
            revdate_trans = [revno_revdate.revdate][0]
            revno_update = pm_sch.objects.filter(Q(status="Fixed Date", controlno=controlno) | Q(status="Not Fixed", controlno=controlno))
            revno_update = revno_update.values('pmcode')
            df_revno_update = pd.DataFrame.from_records(revno_update)
            df_revno_update_len = len(df_revno_update.index)  #itemcode 하나씩 넘기기
            for n in range(df_revno_update_len):
                pmcode_check = df_revno_update.iat[n, 0]
                revno_update = pm_sch.objects.get(Q(pmcode=pmcode_check,status="Fixed Date") | Q(pmcode=pmcode_check,status="Not Fixed"))  # 컨트롤넘버 일치되는 값 찾기
                revno_update.revno = revno_trans
                revno_update.revdate = revdate_trans
                revno_update.save()
            context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                       "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet":pmsheet,
                       "r_name_signal":r_name_signal,"r_date_signal":r_date_signal,"a_name":a_name,"a_date":a_date}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결

def pmapproval_approved_reject(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlformdb = pmmasterlist_temp.objects.filter(controlno = controlno).order_by('freq')
        pmsheet = pmsheetdb.objects.filter(controlno=controlno).order_by('freq_temp')
        r_name = request.POST.get('r_name')  # html에서 해당 값을 받는다
        r_date = request.POST.get('r_date')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####권한에 따라 정보 보내기#####
        auth_check = approval_information.objects.get(division="PM Control Form", description="Reviewed")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="PM Control Form", description="Approved")
        QA_M = auth_check.code_no
        if auth == SO_M:
            controlformlists = controlformlist.objects.filter(status="Prepared", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        elif auth == QA_M:
            controlformlists = controlformlist.objects.filter(status="Reviewed", recent_y="A").order_by('team',
                                                                                                        'controlno')  # db 동기화
        else:
            controlformlists = controlformlist.objects.filter(
                Q(status="Prepared", recent_y="A") | Q(status="Reviewed", recent_y="A")).order_by('team',
                                                                                                  'controlno')  # db
    #####승인권한 확인#####
        auth_check = approval_information.objects.get(description="Approved", division="PM Control Form")
        if auth != auth_check.code_no:
            messages.error(request, "You do not have permission to approve.")
            r_name_date = controlformlist.objects.get(controlno=controlno, recent_y="A")
            r_name_signal = str(r_name_date.r_name_temp)
            r_date_signal = r_name_date.r_date_temp
            equipinforev = controlformlist.objects.filter(controlno=controlno, recent_y="A")
            equipinfo = equiplist.objects.filter(controlno=controlno)
            context = {"controlformdb": controlformdb, "controlformlists": controlformlists, "equipinfo": equipinfo,
                       "equipinforev": equipinforev, "loginid": loginid, "controlno": controlno, "pmsheet": pmsheet,
                       "r_name_signal": r_name_signal, "r_date_signal": r_date_signal}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결
        else:
        #####equip info 정보 보내기#####
            equipinfo = equiplist.objects.filter(controlno = controlno)
            equipinforev = controlformlist.objects.filter(controlno = controlno, recent_y="A")
        #####반려하여 값 뒤로 빼기#####
            status_return = controlformlist.objects.get(controlno=controlno, recent_y="A")  # 컨트롤넘버 일치되는 값 찾기
            status_return.status = "Reject"
            status_return.p_name = ""
            status_return.p_date = ""
            status_return.r_name_temp = ""
            status_return.r_date_temp = ""
            status_return.save()
        #####a_name / a_date 받기#####
            a_name = username
            today = date.datetime.today()
            a_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
            context = {"controlformdb":controlformdb, "controlformlists": controlformlists, "equipinfo":equipinfo,
                       "equipinforev":equipinforev,"loginid":loginid, "controlno":controlno, "pmsheet":pmsheet,
                       "r_name":r_name,"r_date":r_date,"a_name":a_name,"a_date":a_date}
            context.update(users)
            return render(request, 'pmapproval_main.html', context)  # templates 내 html연결

######################
######PM Manual#######
######################

def pmmanual_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "maker":
                pmmanual = pm_manual.objects.filter(maker__icontains=searchtext).order_by('controlno')  # db 동기화
            elif selecttext == "team":
                pmmanual = pm_manual.objects.filter(team__icontains=searchtext).order_by('controlno')  # db 동기화
            elif selecttext == "controlno":
                pmmanual = pm_manual.objects.filter(controlno__icontains=searchtext).order_by('controlno')  # db 동기화
            elif selecttext == "name":
                pmmanual = pm_manual.objects.filter(name__icontains=searchtext).order_by('controlno')  # db 동기화
            elif selecttext == "partname":
                pmmanual = pm_manual.objects.filter(partname__icontains=searchtext).order_by('controlno')  # db 동기화
            elif selecttext == "division":
                pmmanual = pm_manual.objects.filter(division__icontains=searchtext).order_by('controlno')  # db 동기화
            else:
                pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
        except:
            pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
        if str(searchtext) == "None":
            searchtext = ""
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        context = {"pmmanual":pmmanual, "loginid":loginid,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'pmmanual_main.html', context) #templates 내 html연결

def pmmanual_new(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    # equip 정보값 불러오기
        try:
            equip_info = equiplist.objects.get(controlno=controlno)
            equipname = equip_info.name
            equipteam = equip_info.team
            controlno = equip_info.controlno
        #####equip info 정보 보내기#####
            pmmanual = pm_manual.objects.all().order_by('controlno') #db 동기화
            context = {"pmmanual":pmmanual, "loginid":loginid,"equipname":equipname,"equipteam":equipteam,
                        "controlno":controlno}
            context.update(users)
            return render(request, 'pmmanual_main.html', context) #templates 내 html연결
    # equip 없을때
        except:
            messages.error(request, "Equipment information does not exist.")  # 경고
            pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
            loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
            context = {"pmmanual": pmmanual, "loginid": loginid}
            context.update(users)
            return render(request, 'pmmanual_main.html', context)  # templates 내 html연결

def pmmanual_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        equipteam = request.POST.get('team')  # html에서 해당 값을 받는다
        equipname = request.POST.get('name')  # html에서 해당 값을 받는다
        division = request.POST.get('division')  # html에서 해당 값을 받는다
        partname = request.POST.get('partname')  # html에서 해당 값을 받는다
        maker = request.POST.get('maker')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #################파일업로드하기##################
        try:
            if "upload_files" in request.FILES:
                    # 파일 업로드 하기!!!
               upload_files = request.FILES["upload_files"]
               fs = FileSystemStorage()
               name = fs.save(upload_files.name, upload_files)  # 파일저장 // 이름저장
                        # 파일 읽어오기!!!
               url = fs.url(name)
            else:
                file_name = "-"
        #####equip info 정보 보내기#####
            pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
            context = {"pmmanual": pmmanual, "loginid": loginid, "equipname": equipname, "equipteam": equipteam,
                           "controlno": controlno, "division": division, "partname": partname, "maker": maker,
                           "url": url}
            context.update(users)
            return render(request, 'pmmanual_main.html', context)  # templates 내 html연결
        except:
            messages.error(request, "File selection is missing.")  # 경고
            pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
            context = {"pmmanual": pmmanual, "loginid": loginid, "equipname": equipname, "equipteam": equipteam,
                           "controlno": controlno, "division": division, "partname": partname, "maker": maker}
            context.update(users)
            return render(request, 'pmmanual_main.html', context)  # templates 내 html연결

def pmmanual_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        equipteam = request.POST.get('team')  # html에서 해당 값을 받는다
        equipname = request.POST.get('name')  # html에서 해당 값을 받는다
        division = request.POST.get('division')  # html에서 해당 값을 받는다
        partname = request.POST.get('partname')  # html에서 해당 값을 받는다
        maker = request.POST.get('maker')  # html에서 해당 값을 받는다
        url = request.POST.get('url')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        if controlno != "":
            if equipteam != "":
                if equipname != "":
                    if partname != "":
                        if maker !="":
                            if url !="":
                                #################오늘날짜##################
                                    today = date.datetime.today()
                                    today = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
                                #################db저장하기##################
                                    pm_manual(
                                        team = equipteam,
                                        controlno = controlno,
                                        name = equipname,
                                        division = division,
                                        partname = partname,
                                        maker = maker,
                                        url = url,
                                        userid = username,
                                        date = today
                                    ).save()
                                #####equip info 정보 보내기#####
                                    pmmanual = pm_manual.objects.all().order_by('controlno') #db 동기화
                                    context = {"pmmanual": pmmanual, "loginid": loginid}
                                    context.update(users)
                                    return render(request, 'pmmanual_main.html', context)  # templates 내 html연결

    #####equip info 정보 보내기#####
        messages.error(request, "There are entries not entered.")  # 경고
        pmmanual = pm_manual.objects.all().order_by('controlno')  # db 동기화
        context = {"pmmanual": pmmanual, "loginid": loginid}
        context.update(users)
        return render(request, 'pmmanual_main.html', context)  # templates 내 html연결
#######################
####Information########
#######################

def equipmentlist_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        equiplists = equiplist.objects.all().order_by('no') #db 동기화
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        context = {"equiplists":equiplists, "loginid":loginid}
        context.update(users)
        return render(request, 'equipmentlist_main.html', context) #templates 내 html연결

def equipmentlist_new(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        equiplists = equiplist.objects.all().order_by('no') #db 동기화
        controlno = request.POST.get("controlno")
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    # 중복여부 판단하기
        try:
            equiplist.objects.get(controlno=controlno)
            messages.error(request, "The Control No. of facility is duplicated.")  # 경고
            context = {"equiplists":equiplists, "loginid":loginid}
            context.update(users)
            return render(request, 'equipmentlist_main.html', context)  # templates 내 html연결
        except:
    #입력값 저장
            today = date.datetime.today()
            today_y = "20" + today.strftime('%y')
            count_y = int(today_y) - int(request.POST.get("setupdate"))
            equiplist( #설비리스트에 저장하기
                        controlno = request.POST.get("controlno"),
                        team=request.POST.get("team"),
                        name=request.POST.get("name"),
                        model=request.POST.get("model"),
                        serial=request.POST.get("serial"),
                        maker=request.POST.get("maker"),
                        roomname=request.POST.get("roomname"),
                        roomno=request.POST.get("roomno"),
                        setupdate=request.POST.get("setupdate"),
                        count_y = count_y,
                        pq=request.POST.get("pq"),
                        pmok=request.POST.get("pmok"),
                    ).save() #저장
            messages.error(request, "New facility registration has been completed.")

    # 등록완료
            context = {"equiplists":equiplists, "loginid":loginid}
            context.update(users)
            return render(request, 'equipmentlist_main.html', context) #templates 내 html연결


##############################################################################################################
#################################################WORK ORDER###################################################
##############################################################################################################

def workrequest_new(request):
    return render(request, 'workrequest_new.html') #templates 내 html연결

def workrequest_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
    ##table_signal신호 보내기##
        table_signal = "table_signal"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if user_div == "Engineer":
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext, team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext, team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext, team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext, team=userteam).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        context = {"workorderlist": workorderlist, "loginid": loginid,"table_signal":table_signal,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
    return render(request, 'workrequest_main.html', context) #templates 내 html연결

def workrequest_controlno(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    # equip 정보값 불러오기
        try:
            equip_info = equiplist.objects.get(controlno=controlno)
            equipname = equip_info.name
            equipteam = equip_info.team
            roomname = equip_info.roomname
            roomno = equip_info.roomno
            controlno = equip_info.controlno
        #####equip info 정보 보내기#####
            context = {"loginid":loginid,"equipname":equipname,"equipteam":equipteam,
                        "controlno":controlno,"roomno":roomno,"roomname":roomname}
            context.update(users)
            return render(request, 'workrequest_new.html', context) #templates 내 html연결
    # equip 없을때
        except:
            messages.error(request, "Equipment information does not exist.")  # 경고
            loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
            context = {"loginid": loginid}
            context.update(users)
            return render(request, 'workrequest_new.html', context)  # templates 내 html연결

def workrequest_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        capa = request.POST.get('capa')  # html에서 해당 값을 받는다
        equipteam = request.POST.get('equipteam')  # html에서 해당 값을 받는다
        description = request.POST.get('description')  # html에서 해당 값을 받는다
        req_date = request.POST.get('req_date')  # html에서 해당 값을 받는다
        req_reason = request.POST.get('req_reason')  # html에서 해당 값을 받는다
        request_date = request.POST.get('date')  # html에서 해당 값을 받는다
        equipname = request.POST.get('equipname')  # html에서 해당 값을 받는다
        roomname = request.POST.get('roomname')  # html에서 해당 값을 받는다
        roomno = request.POST.get('roomno')  # html에서 해당 값을 받는다
        type = request.POST.get('type')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##req_date 확인하기##
        if req_date == "N/A":
            req_date_return = ""
            req_na_return = "checked"
        else:
            req_date_return = req_date
            req_na_return = ""
    ##type 체크값 전송하기##
        if type == "BM":
            bm = "checked"
            cm = ""
            pm = ""
            it = ""
        elif type == "CM":
            cm = "checked"
            bm = ""
            pm = ""
            it = ""
        elif type == "PM":
            pm = "checked"
            cm = ""
            bm = ""
            it = ""
        elif type == "IT":
            it = "checked"
            cm = ""
            pm = ""
            bm = ""
        else:
            it = ""
            cm = ""
            pm = ""
            bm = ""
    #################파일업로드하기##################
        if "upload_file" in request.FILES:
                # 파일 업로드 하기!!!
           upload_file = request.FILES["upload_file"]
           fs = FileSystemStorage()
           name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
                    # 파일 읽어오기!!!
           url = fs.url(name)
        else:
            file_name = "-"
    #####첨부파일 시그널 주기#####
        url_comp = "Y"
        context = {"loginid":loginid,"equipname":equipname,"equipteam":equipteam,"capa":capa,
                    "description":description,"req_reason":req_reason,"request_date":request_date,
                    "controlno":controlno,"roomno":roomno,"roomname":roomname,"url_comp":url_comp,
                    "bm": bm, "cm": cm, "pm": pm, "it": it,"url":url,"req_date":req_date,
                   "req_date_return":req_date_return,"req_na_return":req_na_return}
        context.update(users)
        return render(request, 'workrequest_new.html', context) #templates 내 html연결

def workrequest_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        capa = request.POST.get('capa')  # html에서 해당 값을 받는다
        equipteam = request.POST.get('equipteam')  # html에서 해당 값을 받는다
        description = request.POST.get('description')  # html에서 해당 값을 받는다
        req_date = request.POST.get('req_date')  # html에서 해당 값을 받는다
        req_reason = request.POST.get('req_reason')  # html에서 해당 값을 받는다
        request_date = request.POST.get('date')  # html에서 해당 값을 받는다
        equipname = request.POST.get('equipname')  # html에서 해당 값을 받는다
        roomname = request.POST.get('roomname')  # html에서 해당 값을 받는다
        roomno = request.POST.get('roomno')  # html에서 해당 값을 받는다
        type = request.POST.get('type')  # html에서 해당 값을 받는다
        url = request.POST.get('url')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##type 체크값 전송하기##
        if type == "BM":
            bm = "checked"
            cm = ""
            pm = ""
            it = ""
        elif type == "CM":
            cm = "checked"
            bm = ""
            pm = ""
            it = ""
        elif type == "PM":
            pm = "checked"
            cm = ""
            bm = ""
            it = ""
        elif type == "IT":
            it = "checked"
            cm = ""
            pm = ""
            bm = ""
        else:
            it = ""
            cm = ""
            pm = ""
            bm = ""
    ##url comp_url 체크하기##
        if url == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    ##req_date입력 후 요청사유 미 입력 시##
        if req_date != "N/A":
            if req_reason == "N/A":
                messages.error(request, "error1")  # 아이디 중복
                context = {"loginid": loginid, "equipname": equipname, "equipteam": equipteam, "capa": capa,
                           "description": description, "req_reason": req_reason, "request_date": request_date,
                           "controlno": controlno, "roomno": roomno, "roomname": roomname,
                           "bm":bm,"cm":cm,"pm":pm,"it":it,"req_date":req_date,"url_comp":url_comp,"url":url}
                context.update(users)
                return render(request, 'workrequest_new.html', context)  # templates 내 html연결
    ##req_date입력확인##
        if req_date != "":
            if req_reason != "":
                if description != "":
                    if capa != "":
                    ##workodrerno생성
                        today = date.datetime.today()
                        date_check = "20" + today.strftime('%y') +"-"+ today.strftime('%m') +"-"+ today.strftime('%d')
                        workorder_date = today.strftime('%y') + today.strftime('%m') + today.strftime('%d')
                        workorder_count = workorder.objects.filter(date=date_check)
                        workorder_count = workorder_count.values('date')
                        df_workorder_count = pd.DataFrame.from_records(workorder_count)
                        df_workorder_count_len = len(df_workorder_count.index)  # itemcode 하나씩 넘기기
                        workorderno_no = int(df_workorder_count_len) + 1
                        workorderno = workorder_date +"/"+ equipteam +"/"+ str(workorderno_no)
                        ##db저장하기##
                        workorder(
                            type = type,
                            capa = capa,
                            requestor = username,
                            team = equipteam,
                            controlno = controlno,
                            description = description,
                            req_date = req_date,
                            req_reason = req_reason,
                            date = request_date,
                            status = "Request",
                            equipname = equipname,
                            roomname = roomname,
                            roomno = roomno,
                            workorderno = workorderno,
                            r_attach = url
                        ).save()
                        ##해당팀장에 메일보내기##


                        context = {"loginid": loginid, "equipname": equipname, "equipteam": equipteam, "capa": capa,
                                    "description": description, "req_reason": req_reason, "request_date": request_date,
                                       "controlno": controlno, "roomno": roomno, "roomname": roomname,"req_date":req_date,
                                   "bm": bm, "cm": cm, "pm": pm, "it": it,"url":url}
                        context.update(users)
                        return render(request, 'workrequest_comp.html', context)  # templates 내 html연결
    ##입력칸 미 입력 시##
        messages.error(request, "There are entries not entered.")
        context = {"loginid":loginid,"equipname":equipname,"equipteam":equipteam,"capa":capa,
                    "description":description,"req_reason":req_reason,"request_date":request_date,
                    "controlno":controlno,"roomno":roomno,"roomname":roomname,
                    "bm": bm, "cm": cm, "pm": pm, "it": it,"req_date":req_date,"url_comp":url_comp,"url":url}
        context.update(users)
        return render(request, 'workrequest_new.html', context) #templates 내 html연결

def workrequest_comp(request):
    return render(request, 'workrequest_comp.html') #templates 내 html연결

def workrequest_view(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if user_div == "Engineer":
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             requestor__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             controlno__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                        '-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid,"workorder_table":workorder_table,
                   "url_comp":url_comp,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
    return render(request, 'workrequest_main.html', context) #templates 내 html연결

def workrequest_receive(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
            r_t_name = "N"
        else:
            r_t_name = "Y"
        if approve_check.r_s_name == "":
            r_s_name = "N"
        else:
            r_s_name = "Y"
        if approve_check.r_m_name == "":
            r_m_name = "N"
        else:
            r_m_name = "Y"
        if approve_check.r_q_name == "":
            r_q_name = "N"
        else:
            r_q_name = "Y"
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if user_div == "Engineer":
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             requestor__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             controlno__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                        '-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                   "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                    "r_q_name": r_q_name,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
    return render(request, 'workrequest_receive.html', context)  # templates 내 html연결

def workrequest_r_t_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
                r_t_name = "N"
        else:
                r_t_name = "Y"
        if approve_check.r_s_name == "":
                r_s_name = "N"
        else:
                r_s_name = "Y"
        if approve_check.r_m_name == "":
                r_m_name = "N"
        else:
                r_m_name = "Y"
        if approve_check.r_q_name == "":
                r_q_name = "N"
        else:
                r_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##권한일치여부 확인하기##
        #####승인권한 확인#####
        auth_checked = approval_information.objects.get(description="Team Manager", division="Work Request")
        auth_check = workorder.objects.get(workorderno=workorderno)
        if auth_check.team == userteam:
            if auth == auth_checked.code_no:
                auth_check.status="Team_approved"
                auth_check.r_t_name=username
                auth_check.r_t_date=today_check
                auth_check.save()
            #####결재확인#####
                if auth_check.r_t_name == "":
                    r_t_name = "N"
                else:
                    r_t_name = "Y"
            #################검색어 반영##################
                selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
                searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
                if user_div == "Engineer":
                    try:
                        if selecttext == "status":
                            workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                     status__icontains=searchtext).order_by(
                                '-date')  # db 동기화
                        elif selecttext == "requestor":
                            workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                     requestor__icontains=searchtext).order_by(
                                '-date')  # db 동기화
                        elif selecttext == "controlno":
                            workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                     controlno__icontains=searchtext).order_by(
                                '-date')  # db 동기화
                        elif selecttext == "team":
                            workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                     team__icontains=searchtext).order_by(
                                '-date')  # db 동기화
                        else:
                            workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                    except:
                        workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                    if str(searchtext) == "None":
                        searchtext = ""
                else:
                    try:
                        if selecttext == "status":
                            workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                                     team=userteam).order_by('-date')  # db 동기화
                        elif selecttext == "requestor":
                            workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                                     team=userteam).order_by('-date')  # db 동기화
                        elif selecttext == "controlno":
                            workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                                     team=userteam).order_by('-date')  # db 동기화
                        elif selecttext == "team":
                            workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                                     team=userteam).order_by('-date')  # db 동기화
                        else:
                            workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                                '-date')  # db 동기화
                    except:
                        workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                            '-date')  # db 동기화
                    if str(searchtext) == "None":
                        searchtext = ""
                workorder_table = workorder.objects.filter(workorderno=workorderno)
                context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                           "url_comp": url_comp,"r_t_name":r_t_name,"r_s_name":r_s_name,"r_m_name":r_m_name,
                           "r_q_name":r_q_name,"selecttext":selecttext,"searchtext":searchtext}
                context.update(users)
                return render(request, 'workrequest_receive.html', context)  # templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if user_div == "Engineer":
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             requestor__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             controlno__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                        '-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                 "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                       "r_q_name": r_q_name,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'workrequest_receive.html', context)  # templates 내 html연결

def workrequest_r_s_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        detail = request.POST.get('detail')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
                r_t_name = "N"
        else:
                r_t_name = "Y"
        if approve_check.r_s_name == "":
            r_s_name = "N"
        else:
            r_s_name = "Y"
        if approve_check.r_m_name == "":
            r_m_name = "N"
        else:
            r_m_name = "Y"
        if approve_check.r_q_name == "":
            r_q_name = "N"
        else:
            r_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##설비 고장원인 사전 입력 유무 확인하기##
        detail_check = workorder.objects.get(workorderno=workorderno)
        if detail_check.description_info != "" or detail !="":
    ##권한일치여부 확인하기##
            auth_checked = approval_information.objects.get(description="Planner", division="Work Request")
            auth_check = workorder.objects.get(workorderno=workorderno)
    ##설비파트 업무확인하기##
            if auth_check.type != "IT":
                if auth == auth_checked.code_no:
                    auth_check.status="Received"
                    auth_check.r_s_name=username
                    auth_check.r_s_date=today_check
                    auth_check.save()
                ##설비 고장원인 사전 입력 유무 확인하기##
                    if auth_check.description_info == "":
                        auth_check.description_info=detail
                        auth_check.save()
                    ##결재여부 확인하기##
                        if auth_check.r_s_name == "":
                            r_s_name = "N"
                        else:
                            r_s_name = "Y"
                        if auth_check.r_m_name == "":
                            r_m_name = "N"
                        else:
                            r_m_name = "Y"
                        if auth_check.r_q_name == "":
                            r_q_name = "N"
                        else:
                            r_q_name = "Y"
                    #################검색어 반영##################
                        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
                        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
                        if user_div == "Engineer":
                            try:
                                if selecttext == "status":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             status__icontains=searchtext).order_by(
                                        '-date')  # db 동기화
                                elif selecttext == "requestor":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             requestor__icontains=searchtext).order_by(
                                        '-date')  # db 동기화
                                elif selecttext == "controlno":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             controlno__icontains=searchtext).order_by(
                                        '-date')  # db 동기화
                                elif selecttext == "team":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             team__icontains=searchtext).order_by(
                                        '-date')  # db 동기화
                                else:
                                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by(
                                        '-date')  # db 동기화
                            except:
                                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                            if str(searchtext) == "None":
                                searchtext = ""
                        else:
                            try:
                                if selecttext == "status":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             status__icontains=searchtext,
                                                                             team=userteam).order_by('-date')  # db 동기화
                                elif selecttext == "requestor":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             requestor__icontains=searchtext,
                                                                             team=userteam).order_by('-date')  # db 동기화
                                elif selecttext == "controlno":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             controlno__icontains=searchtext,
                                                                             team=userteam).order_by('-date')  # db 동기화
                                elif selecttext == "team":
                                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                             team__icontains=searchtext,
                                                                             team=userteam).order_by('-date')  # db 동기화
                                else:
                                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                                        '-date')  # db 동기화
                            except:
                                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                                    '-date')  # db 동기화
                            if str(searchtext) == "None":
                                searchtext = ""
                        workorder_table = workorder.objects.filter(workorderno=workorderno)
                        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                                       "url_comp": url_comp,"r_t_name":r_t_name,"r_s_name":r_s_name,"r_m_name":r_m_name,
                                       "r_q_name":r_q_name,"selecttext":selecttext,"searchtext":searchtext}
                        context.update(users)
                        return render(request, 'workrequest_receive.html', context)  # templates 내 html연결
            ##it파트 업무확인하기##
            else:
                auth_checked = approval_information.objects.get(description="Planner", division="Work Request")
                auth_check = workorder.objects.get(workorderno=workorderno)
                if auth == auth_checked.code_no:
                    auth_check.status = "Recieved"
                    auth_check.r_s_name = username
                    auth_check.r_s_date = today_check
                    auth_check.save()
                ##설비 고장원인 사전 입력 유무 확인하기##
                    if auth_check.description_info == "":
                       auth_check.description_info = detail
                       auth_check.save()
                    ##결재여부 확인하기##
                       if auth_check.r_s_name == "":
                           r_s_name = "N"
                       else:
                           r_s_name = "Y"
                       if auth_check.r_m_name == "":
                           r_m_name = "N"
                       else:
                           r_m_name = "Y"
                       if auth_check.r_q_name == "":
                           r_q_name = "N"
                       else:
                           r_q_name = "Y"
                    #################검색어 반영##################
                       selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
                       searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
                       if user_div == "Engineer":
                           try:
                               if selecttext == "status":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            status__icontains=searchtext).order_by(
                                       '-date')  # db 동기화
                               elif selecttext == "requestor":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            requestor__icontains=searchtext).order_by(
                                       '-date')  # db 동기화
                               elif selecttext == "controlno":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            controlno__icontains=searchtext).order_by(
                                       '-date')  # db 동기화
                               elif selecttext == "team":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            team__icontains=searchtext).order_by(
                                       '-date')  # db 동기화
                               else:
                                   workorderlist = workorder.objects.filter(workorder_y_n="N").order_by(
                                       '-date')  # db 동기화
                           except:
                               workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                           if str(searchtext) == "None":
                               searchtext = ""
                       else:
                           try:
                               if selecttext == "status":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            status__icontains=searchtext,
                                                                            team=userteam).order_by('-date')  # db 동기화
                               elif selecttext == "requestor":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            requestor__icontains=searchtext,
                                                                            team=userteam).order_by('-date')  # db 동기화
                               elif selecttext == "controlno":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            controlno__icontains=searchtext,
                                                                            team=userteam).order_by('-date')  # db 동기화
                               elif selecttext == "team":
                                   workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                            team__icontains=searchtext,
                                                                            team=userteam).order_by('-date')  # db 동기화
                               else:
                                   workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                                       '-date')  # db 동기화
                           except:
                               workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                                   '-date')  # db 동기화
                           if str(searchtext) == "None":
                               searchtext = ""
                       workorder_table = workorder.objects.filter(workorderno=workorderno)
                       context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                                       "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                                       "r_q_name": r_q_name,"selecttext":selecttext,"searchtext":searchtext}
                       context.update(users)
                       return render(request, 'workrequest_receive.html', context)  # templates 내 html연결
    #####권한 미일치#####
            messages.error(request, "You do not have permission to approve.")
    #################검색어 반영##################
            selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
            searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
            if user_div == "Engineer":
                try:
                    if selecttext == "status":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by(
                            '-date')  # db 동기화
                    elif selecttext == "requestor":
                        workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                 requestor__icontains=searchtext).order_by(
                            '-date')  # db 동기화
                    elif selecttext == "controlno":
                        workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                                 controlno__icontains=searchtext).order_by(
                            '-date')  # db 동기화
                    elif selecttext == "team":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by(
                            '-date')  # db 동기화
                    else:
                        workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                except:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
                if str(searchtext) == "None":
                    searchtext = ""
            else:
                try:
                    if selecttext == "status":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                                 team=userteam).order_by('-date')  # db 동기화
                    elif selecttext == "requestor":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                                 team=userteam).order_by('-date')  # db 동기화
                    elif selecttext == "controlno":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                                 team=userteam).order_by('-date')  # db 동기화
                    elif selecttext == "team":
                        workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                                 team=userteam).order_by('-date')  # db 동기화
                    else:
                        workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                            '-date')  # db 동기화
                except:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
                if str(searchtext) == "None":
                    searchtext = ""
            workorder_table = workorder.objects.filter(workorderno=workorderno)
            context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                         "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                               "r_q_name": r_q_name,"selecttext":selecttext,"searchtext":searchtext}
            context.update(users)
            return render(request, 'workrequest_receive.html', context)  # templates 내 html연결
    #####고장사유 미입력#####
        messages.error(request, "If you do not enter the Breakdown Cause, Unable to accept.")
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        if user_div == "Engineer":
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             requestor__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N",
                                                             controlno__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext).order_by(
                        '-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N").order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        else:
            try:
                if selecttext == "status":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", status__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "requestor":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", requestor__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "controlno":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", controlno__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                elif selecttext == "team":
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team__icontains=searchtext,
                                                             team=userteam).order_by('-date')  # db 동기화
                else:
                    workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by(
                        '-date')  # db 동기화
            except:
                workorderlist = workorder.objects.filter(workorder_y_n="N", team=userteam).order_by('-date')  # db 동기화
            if str(searchtext) == "None":
                searchtext = ""
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                   "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                     "r_q_name": r_q_name,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'workrequest_receive.html', context)  # templates 내 html연결

def workorderlist_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        if user_div == "Engineer":
            workorderlist = workorder.objects.all().order_by('-date')  # db 동기화
        elif userteam == "QA":
            workorderlist = workorder.objects.all().order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(team=userteam).order_by('-date')  # db 동기화
        context = {"workorderlist": workorderlist, "loginid": loginid}
        context.update(users)
    return render(request, 'workorderlist_main.html', context) #templates 내 html연결

def workorder_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        workorderlist = workorder.objects.filter(workorder_y_n="Y").order_by('-date')  # db 동기화
        context = {"workorderlist": workorderlist, "loginid": loginid}
        context.update(users)
    return render(request, 'workorder_main.html', context) #templates 내 html연결

def workorder_form(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##COMP_SIGNAL보내기##
        comp_check = workorder.objects.get(workorderno=workorderno)
        if comp_check.workorder_y_n == "Y":
            if comp_check.status != "Approved":
                comp_signal = "Y"
            else:
                comp_signal = "N"
        else:
            comp_signal ="N"
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url=""
        else:
            url_comp = "Y"
            url=url_check.w_attach
    ##pm_trans N/A 시그널##
        pm_check = workorder.objects.get(workorderno=workorderno)
        if pm_check.pm_trans == "Y":
            pm_trans_Y = "selected"
            pm_trans_N = ""
        else:
            pm_trans_N = "selected"
            pm_trans_Y = ""
    ##usedpart N/A 시그널##
        used_check = workorder.objects.get(workorderno=workorderno)
        if used_check.usedpart == "Y":
            usedpart_Y = "selected"
            usedpart_N = ""
        else:
            usedpart_N = "selected"
            usedpart_Y = ""
    ##정보보내기##
        spare_list = spare_out.objects.filter(used_y_n=workorderno)
        controlno_call = workorder.objects.get(workorderno=workorderno)
        controlno= controlno_call.controlno
        equipinfos=equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_call": workorder_call, "loginid": loginid, "workorderno":workorderno,"spare_list":spare_list,
                   "equipinfos":equipinfos,"username":username,"comp_signal":comp_signal,"pm_trans_N":pm_trans_N,
                   "url_comp":url_comp,"url":url,"spare_list":spare_list,"pm_trans_Y":pm_trans_Y,"usedpart_Y":usedpart_Y,
                   "usedpart_N":usedpart_N}
        context.update(users)
    return render(request, 'workorder_form.html', context) #templates 내 html연결

def workorder_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        action_name = request.POST.get('action_name')  # html에서 해당 값을 받는다
        action_company = request.POST.get('action_company')  # html에서 해당 값을 받는다
        work_desc = request.POST.get('work_desc')  # html에서 해당 값을 받는다
        test_result = request.POST.get('test_result')  # html에서 해당 값을 받는다
        detail_type = request.POST.get('detail_type')  # html에서 해당 값을 받는다
        repair_method = request.POST.get('repair_method')  # html에서 해당 값을 받는다
        pm_trans = request.POST.get('pm_trans')  # html에서 해당 값을 받는다
        repair_type = request.POST.get('repair_type')  # html에서 해당 값을 받는다
        action_date = request.POST.get('action_date')  # html에서 해당 값을 받는다
        url = request.POST.get('url_up')  # html에서 해당 값을 받는다
        usedparts_na = request.POST.get('usedparts_na')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##값저장하기##
        workorder_save = workorder.objects.get(workorderno=workorderno)
        workorder_save.action_name = action_name
        workorder_save.action_company = action_company
        workorder_save.work_desc = work_desc
        workorder_save.test_result = test_result
        workorder_save.detail_type = detail_type
        workorder_save.repair_method = repair_method
        workorder_save.pm_trans = pm_trans
        workorder_save.repair_type = repair_type
        workorder_save.action_date = action_date
        workorder_save.status = "Repaired"
        workorder_save.w_attach = url
        workorder_save.usedpart = usedparts_na
        workorder_save.save()
    ##COMP_SIGNAL보내기##
        comp_signal ="Y"
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url=""
        else:
            url_comp = "Y"
            url=url_check.w_attach
    ##신청자에세 매일보내기##


    ##pm_trans N/A 시그널##
        if pm_trans == "Y":
            pm_trans_Y = "selected"
            pm_trans_N = ""
        else:
            pm_trans_N = "selected"
            pm_trans_Y = ""
    ##usedpart N/A 시그널##
        used_check = workorder.objects.get(workorderno=workorderno)
        if used_check.usedpart == "Y":
            usedpart_Y = "selected"
            usedpart_N = ""
        else:
            usedpart_N = "selected"
            usedpart_Y = ""
    ##정보보내기##
        spare_list = spare_out.objects.filter(used_y_n=workorderno)
        controlno_call = workorder.objects.get(workorderno=workorderno)
        controlno= controlno_call.controlno
        equipinfos=equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_call": workorder_call, "loginid": loginid, "workorderno":workorderno,"spare_list":spare_list,
                   "equipinfos":equipinfos,"username":username,"comp_signal":comp_signal,"url_comp":url_comp,"url":url,
                   "pm_trans_N":pm_trans_N,"pm_trans_Y":pm_trans_Y,"usedpart_N":usedpart_N,"usedpart_Y":usedpart_Y}
        context.update(users)
    return render(request, 'workorder_form.html', context) #templates 내 html연결

def workorder_pmcontrolform(request):
    pmreference = pm_reference.objects.all()
    context = {"pmreference": pmreference}
    return render(request, 'workorder_pmcontrolform.html', context) #templates 내 html연결

def workorder_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        action_name = request.POST.get('action_name')  # html에서 해당 값을 받는다
        action_company = request.POST.get('action_company')  # html에서 해당 값을 받는다
        work_desc = request.POST.get('work_desc')  # html에서 해당 값을 받는다
        test_result = request.POST.get('test_result')  # html에서 해당 값을 받는다
        detail_type = request.POST.get('detail_type')  # html에서 해당 값을 받는다
        repair_method = request.POST.get('repair_method')  # html에서 해당 값을 받는다
        pm_trans = request.POST.get('pm_trans')  # html에서 해당 값을 받는다
        repair_type = request.POST.get('repair_type')  # html에서 해당 값을 받는다
        action_date = request.POST.get('action_date')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##action_company N/A 시그널##
        if action_company == "N/A":
            company_na_return ="checked"
        else:
            company_na_return =""
    ##pm_trans N/A 시그널##
        if pm_trans == "Y":
            pm_trans_Y = "selected"
            pm_trans_N = ""
        else:
            pm_trans_N = "selected"
            pm_trans_Y = ""
    ##usedpart N/A 시그널##
        used_check = workorder.objects.get(workorderno=workorderno)
        if used_check.usedpart == "Y":
            usedpart_Y = "selected"
            usedpart_N = ""
        else:
            usedpart_N = "selected"
            usedpart_Y = ""
    ##repair N/A 시그널##
        if repair_type == "Elec.Part":
            repair_type_1 = "selected"
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "Pump":
            repair_type_1 = ""
            repair_type_2 = "selected"
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "Piping":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = "selected"
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "PLC":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = "selected"
            repair_type_5 = ""
        elif repair_type == "ETC":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = "selected"
    #################파일업로드하기##################
        if "upload_file" in request.FILES:
                # 파일 업로드 하기!!!
           upload_file = request.FILES["upload_file"]
           fs = FileSystemStorage()
           name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
                    # 파일 읽어오기!!!
           url = fs.url(name)
        else:
            file_name = "-"
    #####첨부파일 시그널 주기#####
        url_comp = "Y"
    ##COMP_SIGNAL보내기##
        comp_check = workorder.objects.get(workorderno=workorderno)
        if comp_check.workorder_y_n == "Y":
            if comp_check.status != "Approved":
                comp_signal = "Y"
            else:
                comp_signal = "N"
        else:
            comp_signal = "N"
    ##정보보내기##
        spare_list = spare_out.objects.filter(used_y_n=workorderno)
        controlno_call = workorder.objects.get(workorderno=workorderno)
        controlno= controlno_call.controlno
        equipinfos=equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_call": workorder_call, "loginid": loginid, "workorderno":workorderno,
                   "equipinfos":equipinfos,"username":username,"comp_signal":comp_signal,"url_comp":url_comp,
                   "url":url,"action_name":action_name,"action_company":action_company,"work_desc":work_desc,
                   "test_result":test_result,"detail_type":detail_type,"repair_method":repair_method,"pm_trans":pm_trans,
                   "repair_type":repair_type,"action_date":action_date,"company_na_return":company_na_return,
                   "pm_trans_N":pm_trans_N,"pm_trans_Y":pm_trans_Y,"repair_type_1":repair_type_1,"repair_type_2":repair_type_2,
                   "repair_type_3":repair_type_3,"repair_type_4":repair_type_4,"repair_type_5":repair_type_5,"spare_list":spare_list,
                   "usedpart_N":usedpart_N,"usedpart_Y":usedpart_Y}
        context.update(users)
    return render(request, 'workorder_form.html', context) #templates 내 html연결

def workorder_approval_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
    ##table_signal신호 보내기##
        table_signal = "table_signal"
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Order", description="Team Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_S:
            workorderlist = workorder.objects.filter(status="Repaired", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == SO_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Checked", workorder_y_n="Y").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Repaired", workorder_y_n="Y") |
                                                     Q(status="Reviewed", workorder_y_n="Y") |
                                                     Q(status="Checked", workorder_y_n="Y")).order_by('-date')  # db 동기화
        context = {"workorderlist": workorderlist, "loginid": loginid,"table_signal":table_signal}
        context.update(users)
    return render(request, 'workorder_approval_main.html', context) #templates 내 html연결

def workorder_approval_view(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.w_attach
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.w_s_name == "":
            w_s_name = "N"
        else:
            w_s_name = "Y"
        if approve_check.w_m_name == "":
            w_m_name = "N"
        else:
            w_m_name = "Y"
        if approve_check.w_q_name == "":
            w_q_name = "N"
        else:
            w_q_name = "Y"
    #####equip info 정보 보내기#####
        equipinfos=equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Order", description="Team Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_S:
            workorderlist = workorder.objects.filter(status="Repaired", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == SO_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Checked", workorder_y_n="Y").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Repaired", workorder_y_n="Y") |
                                                     Q(status="Reviewed", workorder_y_n="Y") |
                                                     Q(status="Checked", workorder_y_n="Y")).order_by('-date')  # db 동기화
        context = {"workorderlist": workorderlist, "loginid": loginid,"equipinfos":equipinfos,"url":url,
                   "workorder_call":workorder_call,"url_comp":url_comp,"w_s_name":w_s_name,"w_m_name":w_m_name,
                   "w_q_name":w_q_name}
        context.update(users)
    return render(request, 'workorder_approval_main.html', context) #templates 내 html연결

def workrequest_approval_main(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
    ##table_signal신호 보내기##
        table_signal = "table_signal"
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_M:
            workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                     Q(status="Reviewed", workorder_y_n="N") |
                                                     Q(status="Approved", workorder_y_n="N")).order_by('-date')  # db 동기화
        context = {"workorderlist": workorderlist, "loginid": loginid,"table_signal":table_signal}
        context.update(users)
    return render(request, 'workrequest_approval_main.html', context) #templates 내 html연결

def workrequest_approval(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
            r_t_name = "N"
        else:
            r_t_name = "Y"
        if approve_check.r_s_name == "":
            r_s_name = "N"
        else:
            r_s_name = "Y"
        if approve_check.r_m_name == "":
            r_m_name = "N"
        else:
            r_m_name = "Y"
        if approve_check.r_q_name == "":
            r_q_name = "N"
        else:
            r_q_name = "Y"
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_M:
            workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                         Q(status="Reviewed", workorder_y_n="N") |
                                                         Q(status="Approved", workorder_y_n="N")).order_by('-date')  # db 동기화
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                   "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                    "r_q_name": r_q_name}
        context.update(users)
    return render(request, 'workrequest_approval_main.html', context)  # templates 내 html연결

def workrequest_r_m_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
                r_t_name = "N"
        else:
                r_t_name = "Y"
        if approve_check.r_s_name == "":
                r_s_name = "N"
        else:
                r_s_name = "Y"
        if approve_check.r_m_name == "":
            r_m_name = "N"
        else:
            r_m_name = "Y"
        if approve_check.r_q_name == "":
            r_q_name = "N"
        else:
            r_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##권한일치여부 확인하기##
        auth_checked = approval_information.objects.get(description="Maintenance Manager", division="Work Request")
        auth_check = workorder.objects.get(workorderno=workorderno)
        if auth == auth_checked.code_no:
            auth_check.status="Reviewed"
            auth_check.r_m_name=username
            auth_check.r_m_date=today_check
            auth_check.save()
        #####결재여부 확인하기#####
            if auth_check.r_m_name == "":
                r_m_name = "N"
            else:
                r_m_name = "Y"
            if auth_check.r_q_name == "":
                r_q_name = "N"
            else:
                r_q_name = "Y"
        #####equip info 정보 보내기#####
            auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
            SO_M = auth_check.code_no
            auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
            QA_M = auth_check.code_no
            if auth == SO_M:
                workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by(
                    '-date')  # db 동기화
            elif auth == QA_M:
                workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by(
                    '-date')  # db 동기화
            else:
                workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                         Q(status="Reviewed", workorder_y_n="N") |
                                                         Q(status="Approved", workorder_y_n="N")).order_by(
                    '-date')  # db 동기화
            workorder_table = workorder.objects.filter(workorderno=workorderno)
            context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                        "url_comp": url_comp,"r_t_name":r_t_name,"r_s_name":r_s_name,"r_m_name":r_m_name,
                        "r_q_name":r_q_name}
            context.update(users)
            return render(request, 'workrequest_approval_main.html', context)  # templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_M:
            workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                     Q(status="Reviewed", workorder_y_n="N") |
                                                     Q(status="Approved", workorder_y_n="N")).order_by(
                '-date')  # db 동기화
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                 "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                       "r_q_name": r_q_name}
        context.update(users)
        return render(request, 'workrequest_approval_main.html', context)  # templates 내 html연결

def workrequest_r_q_accept(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url comp_url 체크하기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
        else:
            url_comp = "Y"
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.r_t_name == "":
                r_t_name = "N"
        else:
                r_t_name = "Y"
        if approve_check.r_s_name == "":
                r_s_name = "N"
        else:
                r_s_name = "Y"
        if approve_check.r_m_name == "":
                r_m_name = "N"
        else:
                r_m_name = "Y"
        if approve_check.r_q_name == "":
            r_q_name = "N"
        else:
            r_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##권한일치여부 확인하기##
        auth_checked = approval_information.objects.get(description="QA Manager", division="Work Request")
        auth_check = workorder.objects.get(workorderno=workorderno)
        if auth == auth_checked.code_no:
            auth_check.status="Approved"
            auth_check.r_q_name=username
            auth_check.r_q_date=today_check
            auth_check.workorder_y_n="Y"
            auth_check.save()
        ##결재여부 확인하기##
            if auth_check.r_q_name == "":
                r_q_name = "N"
            else:
                r_q_name = "Y"
        #####equip info 정보 보내기#####
            auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
            SO_M = auth_check.code_no
            auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
            QA_M = auth_check.code_no
            if auth == SO_M:
                workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by(
                    '-date')  # db 동기화
            elif auth == QA_M:
                workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by(
                    '-date')  # db 동기화
            else:
                workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                         Q(status="Reviewed", workorder_y_n="N") |
                                                         Q(status="Approved", workorder_y_n="N")).order_by(
                    '-date')  # db 동기화
            workorder_table = workorder.objects.filter(workorderno=workorderno)
            context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                       "url_comp": url_comp,"r_t_name":r_t_name,"r_s_name":r_s_name,"r_m_name":r_m_name,
                       "r_q_name":r_q_name}
            context.update(users)
            return render(request, 'workrequest_approval_main.html', context)  # templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Request", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Request", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_M:
            workorderlist = workorder.objects.filter(status="Received", workorder_y_n="N").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="N").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Received", workorder_y_n="N") |
                                                     Q(status="Reviewed", workorder_y_n="N") |
                                                     Q(status="Approved", workorder_y_n="N")).order_by(
                '-date')  # db 동기화
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "workorder_table": workorder_table,
                 "url_comp": url_comp, "r_t_name": r_t_name, "r_s_name": r_s_name, "r_m_name": r_m_name,
                       "r_q_name": r_q_name}
        context.update(users)
        return render(request, 'workrequest_approval_main.html', context)  # templates 내 html연결

def workorder_w_s_accept(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.w_attach
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.w_s_name == "":
            w_s_name = "N"
        else:
            w_s_name = "Y"
        if approve_check.w_m_name == "":
            w_m_name = "N"
        else:
            w_m_name = "Y"
        if approve_check.w_q_name == "":
            w_q_name = "N"
        else:
            w_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Order", description="Team Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_S:
            workorderlist = workorder.objects.filter(status="Repaired", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == SO_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Checked", workorder_y_n="Y").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Repaired", workorder_y_n="Y") |
                                                     Q(status="Reviewed", workorder_y_n="Y") |
                                                     Q(status="Checked", workorder_y_n="Y")).order_by(
                '-date')  # db 동기화
    ##권한일치여부 확인하기##
        auth_checked = approval_information.objects.get(description="Team Reviewed", division="Work Order")
        auth_check = workorder.objects.get(workorderno=workorderno)
        if auth_check.type != "IT": ##ENG항목확인
            if auth == auth_checked.code_no:
                auth_check.status = "Reviewed"
                auth_check.w_s_name = username
                auth_check.w_s_date = today_check
                auth_check.save()
            #####결재확인#####
                if auth_check.w_s_name == "":
                    w_s_name = "N"
                else:
                    w_s_name = "Y"
                #####equip info 정보 보내기#####
                equipinfos = equiplist.objects.filter(controlno=controlno)
                workorder_call = workorder.objects.filter(workorderno=workorderno)
                context = {"workorderlist": workorderlist, "loginid": loginid, "equipinfos": equipinfos, "url": url,
                           "workorder_call": workorder_call, "url_comp": url_comp, "w_s_name": w_s_name,
                           "w_m_name": w_m_name, "w_q_name": w_q_name}
                context.update(users)
                return render(request, 'workorder_approval_main.html', context)  # templates 내 html연결
        else: #IT항목 확인
            auth_checked = approval_information.objects.get(description="Team Reviewed", division="Work Order")
            if auth == auth_checked.code_no:
                auth_check.status = "Reviewed"
                auth_check.w_s_name = username
                auth_check.w_s_date = today_check
                auth_check.save()
            #####결재확인#####
                if auth_check.w_s_name == "":
                    w_s_name = "N"
                else:
                    w_s_name = "Y"
                #####equip info 정보 보내기#####
                equipinfos=equiplist.objects.filter(controlno=controlno)
                workorder_call = workorder.objects.filter(workorderno=workorderno)
                context = {"workorderlist": workorderlist, "loginid": loginid,"equipinfos":equipinfos,"url":url,
                           "workorder_call":workorder_call,"url_comp":url_comp,"w_s_name":w_s_name,
                           "w_m_name":w_m_name,"w_q_name":w_q_name}
                context.update(users)
                return render(request, 'workorder_approval_main.html', context) #templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
        equipinfos = equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "equipinfos": equipinfos, "url": url,
                   "workorder_call": workorder_call, "url_comp": url_comp, "w_s_name": w_s_name,
                   "w_m_name": w_m_name, "w_q_name": w_q_name}
        context.update(users)
        return render(request, 'workorder_approval_main.html', context)  # templates 내 html연결

def workorder_w_m_accept(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.w_attach
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.w_s_name == "":
            w_s_name = "N"
        else:
            w_s_name = "Y"
        if approve_check.w_m_name == "":
            w_m_name = "N"
        else:
            w_m_name = "Y"
        if approve_check.w_q_name == "":
            w_q_name = "N"
        else:
            w_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Order", description="Team Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_S:
            workorderlist = workorder.objects.filter(status="Repaired", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == SO_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Checked", workorder_y_n="Y").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Repaired", workorder_y_n="Y") |
                                                     Q(status="Reviewed", workorder_y_n="Y") |
                                                     Q(status="Checked", workorder_y_n="Y")).order_by('-date')  # db 동기화
    ##권한일치여부 확인하기##
        auth_checked = approval_information.objects.get(description="Maintenance Manager", division="Work Order")
        auth_check=workorder.objects.get(workorderno = workorderno)
        if auth == auth_checked.code_no:
            auth_check.status = "Checked"
            auth_check.w_m_name = username
            auth_check.w_m_date = today_check
            auth_check.save()
            #####결재확인#####
            if auth_check.w_s_name == "":
                w_m_name = "N"
            else:
                w_m_name = "Y"
        #####equip info 정보 보내기#####
            equipinfos=equiplist.objects.filter(controlno=controlno)
            workorder_call = workorder.objects.filter(workorderno=workorderno)
            context = {"workorderlist": workorderlist, "loginid": loginid,"equipinfos":equipinfos,"url":url,
                       "workorder_call":workorder_call,"url_comp":url_comp,"w_s_name":w_s_name,
                       "w_m_name":w_m_name,"w_q_name":w_q_name}
            context.update(users)
            return render(request, 'workorder_approval_main.html', context) #templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
        equipinfos = equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "equipinfos": equipinfos, "url": url,
                   "workorder_call": workorder_call, "url_comp": url_comp, "w_s_name": w_s_name,
                   "w_m_name": w_m_name, "w_q_name": w_q_name}
        context.update(users)
        return render(request, 'workorder_approval_main.html', context)  # templates 내 html연결

def workorder_w_q_accept(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.w_attach
    ##결재여부 확인하기##
        approve_check = workorder.objects.get(workorderno=workorderno)
        if approve_check.w_s_name == "":
            w_s_name = "N"
        else:
            w_s_name = "Y"
        if approve_check.w_m_name == "":
            w_m_name = "N"
        else:
            w_m_name = "Y"
        if approve_check.w_q_name == "":
            w_q_name = "N"
        else:
            w_q_name = "Y"
    ##오늘날짜 생성하기
        today = date.datetime.today()
        today_check = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    #####equip info 정보 보내기#####
        auth_check = approval_information.objects.get(division="Work Order", description="Team Reviewed")
        SO_S = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="Maintenance Manager")
        SO_M = auth_check.code_no
        auth_check = approval_information.objects.get(division="Work Order", description="QA Manager")
        QA_M = auth_check.code_no
        if auth == SO_S:
            workorderlist = workorder.objects.filter(status="Repaired", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == SO_M:
            workorderlist = workorder.objects.filter(status="Reviewed", workorder_y_n="Y").order_by('-date')  # db 동기화
        elif auth == QA_M:
            workorderlist = workorder.objects.filter(status="Checked", workorder_y_n="Y").order_by('-date')  # db 동기화
        else:
            workorderlist = workorder.objects.filter(Q(status="Repaired", workorder_y_n="Y") |
                                                     Q(status="Reviewed", workorder_y_n="Y") |
                                                     Q(status="Checked", workorder_y_n="Y")).order_by('-date')  # db 동기화
    ##권한일치여부 확인하기##
        auth_checked = approval_information.objects.get(description="QA Manager", division="Work Order")
        auth_check=workorder.objects.get(workorderno = workorderno)
        if auth == auth_checked.code_no:
            auth_check.status = "Completed"
            auth_check.workorder_y_n = "C"
            auth_check.w_q_name = username
            auth_check.w_q_date = today_check
            auth_check.save()
            #####결재확인#####
            if auth_check.w_s_name == "":
                w_q_name = "N"
            else:
                w_q_name = "Y"
        #####equip info 정보 보내기#####
            equipinfos=equiplist.objects.filter(controlno=controlno)
            workorder_call = workorder.objects.filter(workorderno=workorderno)
            context = {"workorderlist": workorderlist, "loginid": loginid,"equipinfos":equipinfos,"url":url,
                       "workorder_call":workorder_call,"url_comp":url_comp,"w_s_name":w_s_name,
                       "w_m_name":w_m_name,"w_q_name":w_q_name}
            context.update(users)
            return render(request, 'workorder_approval_main.html', context) #templates 내 html연결
    #####equip info 정보 보내기#####
        messages.error(request, "You do not have permission to approve.")
        equipinfos = equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorderlist": workorderlist, "loginid": loginid, "equipinfos": equipinfos, "url": url,
                   "workorder_call": workorder_call, "url_comp": url_comp, "w_s_name": w_s_name,
                   "w_m_name": w_m_name, "w_q_name": w_q_name}
        context.update(users)
        return render(request, 'workorder_approval_main.html', context)  # templates 내 html연결

def workorder_return(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        workorderno = request.POST.get('workorderno')  # html에서 해당 값을 받는다
        action_name = request.POST.get('action_name')  # html에서 해당 값을 받는다
        action_company = request.POST.get('action_company')  # html에서 해당 값을 받는다
        work_desc = request.POST.get('work_desc')  # html에서 해당 값을 받는다
        test_result = request.POST.get('test_result')  # html에서 해당 값을 받는다
        detail_type = request.POST.get('detail_type')  # html에서 해당 값을 받는다
        repair_method = request.POST.get('repair_method')  # html에서 해당 값을 받는다
        pm_trans = request.POST.get('pm_trans')  # html에서 해당 값을 받는다
        repair_type = request.POST.get('repair_type')  # html에서 해당 값을 받는다
        action_date = request.POST.get('action_date')  # html에서 해당 값을 받는다
        url = request.POST.get('url_up')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##action_company N/A 시그널##
        if action_company == "N/A":
            company_na_return = "checked"
        else:
            company_na_return = ""
    ##pm_trans N/A 시그널##
        if pm_trans == "Y":
            pm_trans_Y = "selected"
            pm_trans_N = ""
        else:
            pm_trans_N = "selected"
            pm_trans_Y = ""
    ##pm_trans N/A 시그널##
        if repair_type == "Elec.Part":
            repair_type_1 = "selected"
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "Pump":
            repair_type_1 = ""
            repair_type_2 = "selected"
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "Piping":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = "selected"
            repair_type_4 = ""
            repair_type_5 = ""
        elif repair_type == "PLC":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = "selected"
            repair_type_5 = ""
        elif repair_type == "ETC":
            repair_type_1 = ""
            repair_type_2 = ""
            repair_type_3 = ""
            repair_type_4 = ""
            repair_type_5 = "selected"
        ##결재 Status확인##
        status_check = workorder.objects.get(workorderno=workorderno, workorder_y_n="Y")
        if status_check.status == "Repaired":
    ##값저장하기##
            workorder_save = workorder.objects.get(workorderno=workorderno)
            workorder_save.status = "Approved"
            workorder_save.save()
            comp_signal = "N"
        else:
            messages.error(request, "PM Check Sheet that have been approved cannot be returned.")  # 경고
            comp_signal = "Y"
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url=""
        else:
            url_comp = "Y"
            url=url_check.w_attach
    ##정보보내기##
        spare_list = spare_out.objects.filter(used_y_n=workorderno)
        controlno_call = workorder.objects.get(workorderno=workorderno)
        controlno= controlno_call.controlno
        equipinfos=equiplist.objects.filter(controlno=controlno)
        workorder_call = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_call": workorder_call, "loginid": loginid, "workorderno":workorderno,
                       "equipinfos":equipinfos,"username":username,"comp_signal":comp_signal,"url_comp":url_comp,
                       "url":url,"action_name":action_name,"action_company":action_company,"work_desc":work_desc,
                       "test_result":test_result,"detail_type":detail_type,"repair_method":repair_method,"pm_trans":pm_trans,
                       "repair_type":repair_type,"action_date":action_date,"company_na_return":company_na_return,
                       "pm_trans_N":pm_trans_N,"pm_trans_Y":pm_trans_Y,"repair_type_1":repair_type_1,"repair_type_2":repair_type_2,
                       "repair_type_3":repair_type_3,"repair_type_4":repair_type_4,"repair_type_5":repair_type_5,
                        "spare_list":spare_list}
        context.update(users)
        return render(request, 'workorder_form.html', context) #templates 내 html연결

def history_of_repair_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    #################검색어 반영##################
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        try:
            if selecttext == "controlno":
                history_info = workorder.objects.filter(~Q(repair_method="N/A"),controlno__icontains=searchtext).order_by('team','controlno')
            elif selecttext == "equipname":
                history_info = workorder.objects.filter(~Q(repair_method="N/A"),equipname__icontains=searchtext).order_by('team','controlno')
            elif selecttext == "detail_type":
                history_info = workorder.objects.filter(~Q(repair_method="N/A"),detail_type__icontains=searchtext).order_by('team','controlno')
            elif selecttext == "repair_type":
                history_info = workorder.objects.filter(~Q(repair_method="N/A"),repair_type__icontains=searchtext).order_by('team','controlno')
            elif selecttext == "team":
                history_info = workorder.objects.filter(~Q(repair_method="N/A"),team__icontains=searchtext).order_by('team','controlno')
            else:
                history_info = workorder.objects.filter(~Q(repair_method="N/A")).order_by('team','controlno')
        except:
            history_info = workorder.objects.filter(~Q(repair_method="N/A")).order_by('team','controlno')
        if str(searchtext) == "None":
            searchtext = ""
    ##정보보내기##
        context = {"history_info": history_info, "loginid":loginid,"selecttext":selecttext,"searchtext":searchtext}
        context.update(users)
        return render(request, 'history_of_repair_main.html', context) #templates 내 html연결

def workorderlist_request(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        workorderno = request.POST.get('workorderno_get')  # html에서 해당 값을 받는다
    ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.r_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.r_attach
    ##정보보내기##
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_table": workorder_table,"url_comp":url_comp,"url":url}
        return render(request, 'workorderlist_request.html', context) #templates 내 html연결

def workorderlist_request_print(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        workorderno = request.POST.get('workorderno_trans')  # html에서 해당 값을 받는다
    ##정보보내기##
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_table": workorder_table}
        return render(request, 'workorderlist_request_print.html', context) #templates 내 html연결

def workorderlist_request_main(request):
        return render(request, 'workorderlist_request_main.html') #templates 내 html연결

def workorderlist_order(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        workorderno = request.POST.get('workorderno_get')  # html에서 해당 값을 받는다
        controlno_get = workorder.objects.get(workorderno=workorderno)
        controlno = controlno_get.controlno
        ##url_SIGNAL보내기##
        url_check = workorder.objects.get(workorderno=workorderno)
        if url_check.w_attach == "":
            url_comp = "N"
            url = ""
        else:
            url_comp = "Y"
            url = url_check.w_attach
    ##정보보내기##
        equipinfos = equiplist.objects.filter(controlno=controlno)
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_table": workorder_table,"equipinfos":equipinfos,"url_comp":url_comp,"url":url}
        return render(request, 'workorderlist_order.html', context) #templates 내 html연결

def workorderlist_order_print(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        workorderno = request.POST.get('workorderno_trans')  # html에서 해당 값을 받는다
    ##정보보내기##
        workorder_table = workorder.objects.filter(workorderno=workorderno)
        context = {"workorder_table": workorder_table}
        return render(request, 'workorderlist_order_print.html', context) #templates 내 html연결

def workorderlist_order_main(request):
        return render(request, 'workorderlist_order_main.html') #templates 내 html연결

def workorder_pmcontrolform_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    #####equip info 정보 보내기#####
        equiptable = equiplist.objects.get(controlno=controlno)
        equiptablerev = controlformlist.objects.get(controlno=controlno, recent_y="Y")
    ######기존 중복 입력여부 확인하기#####
        workorderno_check = request.POST.get('change_reason')
        try:
            chk = pmmasterlist_temp.objects.get(change=workorderno_check)
            pmreference = pm_reference.objects.all()
            context = {"pmreference": pmreference}
            messages.error(request, "This Workorder No. is already registered.")  # 비번 불일치
            return render(request, 'workorder_pmcontrolform.html', context)  # templates 내 html연결
        except:
        #####데이터 가공하기#####
        ######sheet No. 만들기#####
            freq_no=request.POST.get('freq_no')
            freq_my=request.POST.get('freq_my')
            if freq_my == "Month":
                freq_my = "M"
            else:
                freq_my = "Y"
            sheetno = str(controlno) + "-" + str(freq_no) + freq_my
        ######주기만들기#####
            freq_no=request.POST.get('freq_no')
            freq_my=request.POST.get('freq_my')
            freq = str(freq_no) + str(freq_my)
        ######itemno 만들기#####
            itemno_make = pmmasterlist_temp.objects.filter(sheetno = sheetno).values('sheetno')
            df = pd.DataFrame.from_records(itemno_make)
            itemno = len(df.index) + 1
        ######itemcode 만들기#####
            itemcode = sheetno + str(itemno)
        ######시트시작일 만들기#####
            try:
                chk = pmsheetdb.objects.get(pmsheetno_temp=sheetno)
            except:
                pmsheetdb(
                    controlno=controlno,
                    pmsheetno_temp = sheetno, #신규Sheet No. 임시입력
                    freq_temp= freq, #신규주기 임시입력
                    startdate_temp= "New", #시작일자 입력
                ).save()
        #####새로운 값 저장하기#####
            pmmasterlist_temp(  # 컨트롤폼에 신규등록하기
                team=equiptable.team,  # 팀명
                controlno=controlno,  # 컨트롤넘버
                name=equiptable.name,  # 설비명
                model=equiptable.model,  # 모델명
                serial=equiptable.serial,  # 시리얼넘버
                maker=equiptable.maker,  # 제조사
                roomname=equiptable.roomname,  # 룸명
                roomno=equiptable.roomno,  # 룸넘버
                revno=equiptablerev.revno,  # 리비젼넘버
                date=equiptablerev.revdate,  # 리비젼날짜
                freq=freq,  # 주기
                ra=equiptable.ra,  # ra결과
                sheetno=sheetno,  # 시트넘버
                amd="A",  # a/m/d
                itemno= itemno,  # 순번
                item=request.POST.get('item'),  # 점검내용
                check=request.POST.get('check'),  # 점검기준
                startdate= "New",  # 시트시작일
                change=request.POST.get('change_reason'),  # 변경사유
                itemcode=itemcode,  # 점검내용 구분좌
                division=request.POST.get('division'),
            ).save()
        #####컨트롤폼 status 변경#####
            controlform_status = controlformlist.objects.get(controlno=controlno, recent_y="Y")
            controlform_status.status = "Review"  # 기존버전 RECENT값 Y로 바꾸기
            controlform_status.save()
        #####signal 정보 보내기#####
            item = request.POST.get('item')
            check = request.POST.get('check')
            change = request.POST.get('change_reason')
            division = request.POST.get('division')
            context = {"loginid": loginid,"freq_no":freq_no,"freq_my":freq_my,"item":item,"check":check,"change":change,
                       "division":division}
            context.update(users)
            return render(request, 'workorder_pmcontrolform_comp.html', context)  # templates 내 html연결

def workorder_used_part(request):
    spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code','team')  # db 동기화
    context = {"spareparts_release":spareparts_release}
    return render(request, 'workorder_used_part.html', context) #templates 내 html연결


def workorder_used_click(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html 선택조건의 값을 받는다
        used_part = request.POST.get('used_part')  # html 입력 값을 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        workorderno = request.POST.get('workorderno')  # html 선택조건의 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####값 저장하기###
        if used_part =="Y":
            used_part_input = spare_out.objects.get(no=no)
            used_part_input.used_y_n_temp = workorderno
            used_part_input.check_y_n_temp = "checked"
            used_part_input.save()
        elif used_part =="N":
            used_part_input = spare_out.objects.get(no=no)
            used_part_input.used_y_n_temp = ""
            used_part_input.check_y_n_temp = ""
            used_part_input.save()
        context = {"spareparts_release": spareparts_release}
        context.update(users)
        return render(request, 'workorder_used_part.html', context)  # templates 내 html연결

def workorder_used_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        workorderno = request.POST.get('workorderno')  # html 선택조건의 값을 받는다
        itemcode = request.POST.get('itemcode')  # html 선택조건의 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####사용자재 링크저장하기###
        used_submit = spare_out.objects.filter(used_y_n_temp=workorderno)
        used_submit = used_submit.values('no')  # sql문 dataframe으로 변경
        df_used_submit = pd.DataFrame.from_records(used_submit)
        df_used_submit_len = len(df_used_submit.index)  # 일정 숫자로 변환
        for k in range(df_used_submit_len):
            used_no = df_used_submit.iat[k, 0]
            used_no_save = spare_out.objects.get(no=used_no)
            used_no_save.used_y_n = used_no_save.used_y_n_temp
            used_no_save.check_y_n = used_no_save.check_y_n_temp
            used_no_save.save()
    ####사용자재 Y 입력하기###
        used_check = workorder.objects.get(workorderno=workorderno)
        used_check.usedpart="Y"
        used_check.save()
    ####입력창 닫힘###
        close_signal ="Y"
        context = {"spareparts_release": spareparts_release,"close_signal":close_signal}
        return render(request, 'workorder_used_part.html', context)  # templates 내 html연결

def workorder_used_minus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                          'team')  # db 동기화
        ####값 저장하기###
        qy_get = spare_out.objects.get(no=no)
        qy_cal = int(qy_get.used_qy) - 1
        if qy_cal > 0:
            qy_get.used_qy = qy_cal
            qy_get.save()
        context = {"spareparts_release": spareparts_release}
        return render(request, 'workorder_used_part.html', context)  # templates 내 html연결

def workorder_used_plus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        no = request.POST.get('no')  # html 입력 값을 받는다
        spareparts_release = spare_out.objects.filter(temp_y_n="Y", used_y_n="").order_by('date', 'out_code',
                                                                                              'team')  # db 동기화
    ####값 저장하기###
        qy_get = spare_out.objects.get(no=no)
        qy_cal = int(qy_get.used_qy) + 1
        if qy_cal <= int(qy_get.qy):
            qy_get.used_qy = qy_cal
            qy_get.save()
        context = {"spareparts_release": spareparts_release}
        return render(request, 'workorder_used_part.html', context)  # templates 내 html연결


##############################################################################################################
#################################################Admin########################################################
##############################################################################################################

def user_info(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        user_info = userinfo.objects.all() #db 동기화
        approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
        context = {"user_info": user_info, "loginid":loginid,"approval_infos":approval_infos}
        context.update(users)
        return render(request, 'user_info.html', context) #templates 내 html연결

def user_info_new(request):
    approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
    context = {"approval_infos": approval_infos}
    return render(request, 'user_info_new.html', context)  # templates 내 html연결

def user_info_new_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##입력값 불러오기##
        userid_up = request.POST.get('userid')  # html Login id의 값을
        username_up = request.POST.get('username')  # html Login id의 값을
        userteam_up = request.POST.get('userteam')  # html Login id의 값을
        password_up = request.POST.get('password')  # html Login id의 값을
        password_again_up = request.POST.get('password_again')  # html Login id의 값을
        useremail_up = request.POST.get('useremail')  # html Login id의 값을
        auth_1_up = request.POST.get('auth_1')  # html Login id의 값을
        user_div_up = request.POST.get('user_div')  # html Login id의 값을
    # ID중복여부 판단하기
        try:
            id_check= userinfo.objects.get(userid = userid_up)  # db 동기화
            messages.error(request, "ID already exists.")  # 아이디 중복
            approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
            context = {"approval_infos": approval_infos, "loginid":loginid}
            context.update(users)
            return render(request, 'user_info_new.html', context) #templates 내 html연결
        except:
    # PASSWORD 일치여부 판단하기
            if password_up != password_again_up:
                messages.error(request, "Passwords do not match.")  # 비번 불일치
                approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
                context = {"approval_infos": approval_infos, "loginid": loginid}
                context.update(users)
                return render(request, 'user_info_new.html', context)  # templates 내 html연결
            else:
    # PASSWORD 복잡도 판단하기
                check = password_up
                if len(check) > 7: #8자 이상
                    a = re.compile('[a-z]') #소문자 포함
                    result_a = a.search(check)
                    if result_a != None:
                        b = re.compile(r'\d')  # 숫자 포함
                        result_b = b.search(check)
                        if result_b != None:
                            c = re.compile('[A-Z]')  # 대문자 포함
                            result_c = c.search(check)
                            if result_c != None:
                                d = re.compile('[~!@#$%^&*]')  # 특수문자자 포함
                                result_d = d.search(check)
                                if result_d != None:
    ######################### 값 저장하기
                                    userinfo(
                                        userid=userid_up,
                                        username=username_up,
                                        userteam=userteam_up,
                                        password=password_up,
                                        useremail=useremail_up,
                                        auth1=auth_1_up,
                                        user_division=user_div_up).save()
                                    comp_signal="Y"
                                    approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
                                    context = {"approval_infos": approval_infos, "loginid":loginid,"comp_signal":comp_signal}
                                    context.update(users)
                                    return render(request, 'user_info_new.html', context) #templates 내 html연결
                messages.error(request, "Password policy was violated.")  # 아이디 중복
                approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
                context = {"uapproval_infos": approval_infos, "loginid": loginid}
                context.update(users)
                return render(request, 'user_info_new.html', context)  # templates 내 html연결

def user_info_change(request):
    approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
    context={"approval_infos":approval_infos}
    return render(request, 'user_info_change.html', context)  # templates 내 html연결

def approval_info(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
        approval_infos = approval_information.objects.all().order_by('division') #db 동기화
        context = {"approval_infos": approval_infos, "loginid":loginid}
        context.update(users)
        return render(request, 'approval_info.html', context) #templates 내 html연결

def approval_info_new(request):
    return render(request, 'approval_info_new.html')  # templates 내 html연결

def approval_info_new_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        division_get = request.POST.get('division')  # html에서 해당 값을 받는다
        description_get = request.POST.get('description')  # html에서 해당 값을 받는다
        team_get = request.POST.get('team')  # html에서 해당 값을 받는다
        auth_name_get = request.POST.get('auth_name')  # html에서 해당 값을 받는다
        authority_get = request.POST.get('authority')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##값저장하기##
        approval_information(
            division = division_get,
            description = description_get,
            auth_team = team_get,
            auth_name = auth_name_get,
            code_no = authority_get,
        ).save()
    ##정보보내기##
        comp_signal="Y"
        context = {"loginid":loginid,"comp_signal":comp_signal}
        context.update(users)
        return render(request, 'approval_info_new.html', context) #templates 내 html연결

def approval_info_change(request):
    return render(request, 'approval_info_change.html')  # templates 내 html연결

def approval_info_change_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        division_get = request.POST.get('division')  # html에서 해당 값을 받는다
        description_get = request.POST.get('description')  # html에서 해당 값을 받는다
        team_get = request.POST.get('auth_team')  # html에서 해당 값을 받는다
        auth_name_get = request.POST.get('auth_name')  # html에서 해당 값을 받는다
        authority_get = request.POST.get('code_no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##값변경하기##
        try:
            auth_change= approval_information.objects.get(division=division_get, description=description_get)
            auth_change.division = division_get
            auth_change.description = description_get
            auth_change.auth_team = team_get
            auth_change.auth_name = auth_name_get
            auth_change.code_no = authority_get
            auth_change.save()
        except:
            pass
    ##정보보내기##
        comp_signal="Y"
        context = {"loginid":loginid,"comp_signal":comp_signal}
        context.update(users)
        return render(request, 'approval_info_new.html', context) #templates 내 html연결

def approval_info_delete(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        division_get = request.POST.get('division')  # html에서 해당 값을 받는다
        description_get = request.POST.get('description')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##삭제하기##
        delete_check = approval_information.objects.get(division=division_get, description=description_get)
        delete_check.delete()
        approval_infos = approval_information.objects.all().order_by('division') #db 동기화
        context = {"approval_infos": approval_infos, "loginid":loginid}
        context.update(users)
        return render(request, 'approval_info.html', context) #templates 내 html연결

def user_info_change_submit(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        userteam_get = request.POST.get('userteam')  # html에서 해당 값을 받는다
        password_get = request.POST.get('password')  # html에서 해당 값을 받는다
        useremail_get = request.POST.get('useremail')  # html에서 해당 값을 받는다
        auth_1_get = request.POST.get('auth_1')  # html에서 해당 값을 받는다
        user_div_get = request.POST.get('user_div')  # html에서 해당 값을 받는다
        userid_get = request.POST.get('userid')  # html에서 해당 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##이름 및 권한 끌고다니기##
        info_change = userinfo.objects.get(userid=userid_get)
        info_change.userteam = userteam_get
        info_change.password = password_get
        info_change.useremail = useremail_get
        info_change.auth1 = auth_1_get
        info_change.user_division = user_div_get
        info_change.save()
    ##자동클로우즈##
        comp_signal = "Y"
        context = {"loginid":loginid,"comp_signal":comp_signal}
        context.update(users)
        return render(request, 'user_info_change.html', context) #templates 내 html연결

def user_info_change_delete(request):
    if request.method =='POST': #매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        userid_get = request.POST.get('userid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth":auth,"password":password,"username":username,"userteam":userteam,"user_div":user_div}
    ##내용삭제##
        delete_check = userinfo.objects.get(userid=userid_get) #db 동기화
        delete_check.delete()
        user_info = userinfo.objects.all() #db 동기화
        approval_infos = approval_information.objects.all().values('code_no').annotate(Count('code_no'))
        context = {"user_info": user_info, "loginid":loginid,"approval_infos":approval_infos}
        context.update(users)
        return render(request, 'user_info.html', context) #templates 내 html연결

##############################################################################################################
#############################################Spare Parts######################################################
##############################################################################################################
def spareparts_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        if selecttext == "partname":
            spare_list = spare_parts_list.objects.filter(partname__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "vendor":
            spare_list = spare_parts_list.objects.filter(vendor__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "team":
            spare_list = spare_parts_list.objects.filter(team__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "codeo":
            spare_list = spare_parts_list.objects.filter(codeno__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "stock":
            spare_list = spare_parts_list.objects.filter(stock__icontains=searchtext).order_by('team','codeno')  # db 동기화
        else:
            spare_list = spare_parts_list.objects.all().order_by('team','codeno')  # db 동기화
        context = {"spare_list": spare_list, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_main.html', context)  # templates 내 html연결

def spareparts_new(request):
    return render(request, 'spareparts_new.html') #templates 내 html연결

def spareparts_new_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        team = request.POST.get('team')  # html 선택조건의 값을 받는다
        partsname = request.POST.get('partsname')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        vendor = request.POST.get('vendor')  # html 선택조건의 값을 받는다
        modelno = request.POST.get('modelno')  # html 입력 값을 받는다
        spec = request.POST.get('spec')  # html에서 해당 값을 받는다
        location = request.POST.get('location')  # html 선택조건의 값을 받는다
        safety_stock = request.POST.get('safety_stock')  # html 입력 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
    ####코드넘버 생성하기####
        try:
            code_no = spare_parts_list.objects.filter(team=team)
            code_no = code_no.values('team')
            df_code_no = pd.DataFrame.from_records(code_no)
            code_no_len = len(df_code_no.index)
            code_no_len = int(code_no_len) + 1
            if code_no_len < 10:
                number = "000" + str(code_no_len)
            elif code_no_len < 100:
                number = "00" + str(code_no_len)
            elif code_no_len < 1000:
                number = "0" + str(code_no_len)
            else:
                number = str(code_no_len)
            codeno = team + number
        except:
            codeno = team + "0001"
        spare_parts_list(
            codeno = codeno,
            team = team,
            partname = partsname,
            vendor = vendor,
            modelno = modelno,
            spec = spec,
            location = location,
            staff = username,
            stock = 0,
            safety_stock = safety_stock,
        ).save()
        context = {"team":team,"codeno":codeno,"partsname":partsname,"vendor":vendor,"modelno":modelno,"spec":spec,
                 "location":location,"username":username,"safety_stock":safety_stock}
    return render(request, 'spareparts_new_comp.html', context) #templates 내 html연결

def spareparts_incoming_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_search(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        searchtext = request.POST.get('search_text')  # html에서 해당 값을 받는다
        selecttext = request.POST.get('select_text')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##검색테이블##
        if selecttext == "codeno":
            search_result = spare_parts_list.objects.filter(codeno__icontains=searchtext).order_by('codeno')  # db 동기화                                                                                'codeno')  # db 동기화
        elif selecttext == "partname":
            search_result = spare_parts_list.objects.filter(partname__icontains=searchtext).order_by('codeno')  # db 동기화
        elif selecttext == "team":
            search_result = spare_parts_list.objects.filter(team__icontains=searchtext).order_by('codeno')  # db 동기화
        elif selecttext == "vendor":
            search_result = spare_parts_list.objects.filter(vendor__icontains=searchtext).order_by('codeno') # db 동기화
        elif selecttext == "total":
            search_result = spare_parts_list.objects.filter(Q(codeno__icontains=searchtext)|Q(vendor__icontains=searchtext)
                                                     |Q(partname__icontains=searchtext)|Q(modelno__icontains=searchtext)
                                                     |Q(team__icontains=searchtext)).order_by('codeno')
        elif selecttext == "modelno":
            search_result = spare_parts_list.objects.filter(modelno__icontains=searchtext).order_by('codeno')  # db 동기화
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid,"searchtext":searchtext,
                   "search_result":search_result,"selecttext":selecttext}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_select(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        searchtext = request.POST.get('search_text')  # html에서 해당 값을 받는다
        selecttext = request.POST.get('select_text')  # html에서 해당 값을 받는다
        codeno = request.POST.get('codeno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##검색테이블##
        if selecttext == "codeno":
            search_result = spare_parts_list.objects.filter(codeno__icontains=searchtext).order_by(
                'codeno')
        elif selecttext == "partname":
            search_result = spare_parts_list.objects.filter(partname__icontains=searchtext).order_by('codeno')  # db 동기화
        elif selecttext == "team":
            search_result = spare_parts_list.objects.filter(team__icontains=searchtext).order_by('codeno')  # db 동기화
        elif selecttext == "vendor":
            search_result = spare_parts_list.objects.filter(vendor__icontains=searchtext).order_by('codeno')  # db 동기화
        elif selecttext == "total":
            search_result = spare_parts_list.objects.filter(
                Q(codeno__icontains=searchtext) | Q(vendor__icontains=searchtext)
                | Q(partname__icontains=searchtext) | Q(modelno__icontains=searchtext)
                | Q(team__icontains=searchtext)).order_by('codeno')
        elif selecttext == "modelno":
            search_result = spare_parts_list.objects.filter(modelno__icontains=searchtext).order_by(
                'codeno')  # db 동기화
    ##검색테이블##
        select_result = spare_parts_list.objects.filter(codeno=codeno)
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid,"searchtext":searchtext,
                   "search_result":search_result,"selecttext":selecttext,"select_result":select_result,"codeno":codeno}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_sel_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        qy_text = request.POST.get('qy_text')  # html에서 해당 값을 받는다
        division_text = request.POST.get('division_text')  # html에서 해당 값을 받는다
        codeno = request.POST.get('codeno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##데이터 저장##
        #####입력날짜 받기#####
        today = date.datetime.today()
        today_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        try:
            info_get = spare_parts_list.objects.get(codeno=codeno)
            spare_in(
                codeno=info_get.codeno,
                team=info_get.team,
                partname=info_get.partname,
                vendor=info_get.vendor,
                modelno=info_get.modelno,
                staff=username,
                qy=qy_text,
                date=today_date,
                temp_y_n="N",
                location=info_get.location,
                division=division_text,
            ).save()
        except:
            pass
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_delete(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##삭제##
        try:
            qy_check = spare_in.objects.get(no=no)
            qy_check.delete()
        except:
            pass
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_plus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##수량조절하기##
        qy_check = spare_in.objects.get(no=no)
        qy = int(qy_check.qy)
        qy = qy + 1
        qy_check.qy = qy
        qy_check.save()
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_minus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        ##수량조절하기##
        qy_check = spare_in.objects.get(no=no)
        qy = int(qy_check.qy)
        if qy == 1:
            qy = 1
        else:
            qy = qy - 1
        qy_check.qy = qy
        qy_check.save()
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_reset(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##삭제하기##
        del_check = spare_in.objects.filter(temp_y_n="N", staff=username)
        del_check = del_check.values('no')
        df_del_check = pd.DataFrame.from_records(del_check)
        del_check_len = len(df_del_check.index)
        for k in range(del_check_len):
            no_change = df_del_check.iat[k, 0]
            qy_check = spare_in.objects.get(no=no_change)
            qy_check.delete()
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_location(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        location_up = request.POST.get('location_up')  # html에서 해당 값을 받는다
        no = request.POST.get('no_up')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##위치바꾸기##
        location_check = spare_in.objects.get(no=no)
        location_check.location = location_up
        location_check.save()
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##오늘날짜 확인하기##
        today = date.datetime.today()
        today_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##입고넘버 생성하기 변경하기##
        code_date = today.strftime('%y') + today.strftime('%m') + today.strftime('%d')
        in_code_gen = spare_in.objects.filter(date=today_date)
        in_code_gen = in_code_gen.values('date')
        df_in_code_gen = pd.DataFrame.from_records(in_code_gen)
        in_code_gen_len = len(df_in_code_gen.index)
        in_code_gen = str(code_date) + "/" + str(in_code_gen_len)
    ##토탈계산하기##
        count_check = spare_in.objects.filter(temp_y_n="N", staff=username)
        count_check = count_check.values()
        df_count_check = pd.DataFrame.from_records(count_check)
        count_check_len = len(df_count_check.index)
        for m in range(count_check_len):
            codeno = df_count_check.iat[m, 1]
        # 현 재고수량#
            stock_get = spare_parts_list.objects.get(codeno=codeno)
            now_stock = stock_get.stock
        # 현 재고수량 부족 시 알람발생#
            use_get = df_count_check.iat[m, 7]
            new_stock = int(now_stock) + int(use_get)
            stock_get = spare_parts_list.objects.get(codeno=codeno)
            stock_get.stock = new_stock
            stock_get.save()
    ##location 신규저장하기##
        location_check = spare_in.objects.filter(temp_y_n="N", staff=username)
        location_check = location_check.values('no')
        df_location_check = pd.DataFrame.from_records(location_check)
        location_check_len = len(df_location_check.index)
        for j in range(location_check_len):
            no_check = df_location_check.iat[j, 0]
            location_check = spare_in.objects.get(no=no_check)
            codeno_get = location_check.codeno
            location_get = location_check.location
            location_chk = spare_parts_list.objects.get(codeno=codeno_get)
            location_get2 = location_chk.location
            try:
                location = spare_parts_list.objects.get(codeno=codeno_get,location__icontains=location_get)
            except:
                location_new = str(location_get2) + ", " + str(location_get)
                location_chk.location = location_new
                location_chk.save()
    ##status 변경하기##
        status_check = spare_in.objects.filter(temp_y_n="N", staff=username)
        status_check = status_check.values('no')
        df_status_check = pd.DataFrame.from_records(status_check)
        status_check_len = len(df_status_check.index)
        for k in range(status_check_len):
            no_change = df_status_check.iat[k, 0]
            status_change = spare_in.objects.get(no=no_change)
            status_change.temp_y_n = "Y"
            status_change.date = today_date
            status_change.in_code = in_code_gen
            status_change.save()
        spare_incoming = spare_in.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_incoming": spare_incoming, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_incoming_main.html', context)  # templates 내 html연결

def spareparts_incoming_list(request):
    selecttext = request.GET.get('selecttext')  # html 선택조건의 값을 받는다
    searchtext = request.GET.get('searchtext')  # html 입력 값을 받는다
    if selecttext == "codeno":
        spareparts_incoming = spare_in.objects.filter(codeno__icontains=searchtext, temp_y_n="Y").order_by('-date', 'in_code','team')  # db 동기화                                                                                'codeno')  # db 동기화
    elif selecttext == "partname":
        spareparts_incoming = spare_in.objects.filter(partname__icontains=searchtext, temp_y_n="Y").order_by('-date', 'in_code','team')  # db 동기화
    elif selecttext == "date":
        spareparts_incoming = spare_in.objects.filter(date__icontains=searchtext, temp_y_n="Y").order_by('-date', 'in_code','team')  # db 동기화
    elif selecttext == "in_code":
        spareparts_incoming = spare_in.objects.filter(out_code__icontains=searchtext, temp_y_n="Y").order_by('-date', 'in_code','team')  # db 동기화
    elif selecttext == "staff":
        spareparts_incoming = spare_in.objects.filter(staff__icontains=searchtext, temp_y_n="Y").order_by('-date',
                                                                                                             'in_code',
                                                                                                             'team')  # db 동기화
    else:
        spareparts_incoming = spare_in.objects.filter(temp_y_n="Y").order_by('-date', 'in_code','team')  # db 동기화
    context = {"spareparts_incoming":spareparts_incoming, "selecttext":selecttext,"searchtext":searchtext}
    return render(request, 'spareparts_incoming_list.html', context) #templates 내 html연결

def spareparts_release_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release":spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_scan(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        search_text = request.POST.get('search_text')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    #####입력날짜 받기#####
        today = date.datetime.today()
        today_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
        try:
            info_get = spare_parts_list.objects.get(codeno=search_text)
            spare_out(
                codeno=info_get.codeno,
                team=info_get.team,
                partname=info_get.partname,
                vendor=info_get.vendor,
                modelno=info_get.modelno,
                staff=username,
                qy=1,
                date=today_date,
                temp_y_n="N",
                location=info_get.location,
            ).save()
        except:
            messages.error(request, "No such Code No. exists.")  #
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        release_result = spare_parts_list.objects.filter(codeno=search_text)
        context = {"spare_release":spare_release,"loginid":loginid,"release_result":release_result}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_minus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##수량조절하기##
        qy_check = spare_out.objects.get(no=no)
        qy = int(qy_check.qy)
        if qy == 1:
            qy = 1
        else:
            qy = qy - 1
        qy_check.qy = qy
        qy_check.save()
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release":spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_plus(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##수량조절하기##
        qy_check = spare_out.objects.get(no=no)
        qy = int(qy_check.qy)
        qy = qy + 1
        qy_check.qy = qy
        qy_check.save()
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release":spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_delete(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        no = request.POST.get('no')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##이름 및 권한 끌고다니기##
        try:
            qy_check = spare_out.objects.get(no=no)
            qy_check.delete()
        except:
            pass
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release": spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_controlno(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##설비명 불러오기##
        try:
            equip_get = equiplist.objects.get(controlno=controlno)
            equipname = equip_get.name
        except:
            equipname=""
            controlno=""
            messages.error(request, "No such equipment exists.")  # 아이디 중복
        ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release": spare_release, "loginid": loginid,"equipname":equipname,"controlno":controlno}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_table_controlno(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        controlno = request.POST.get('controlno')  # html에서 해당 값을 받는다
        no_up = request.POST.get('no_up')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##설비명 불러오기##
        try:
            equip_get = equiplist.objects.get(controlno=controlno)
            equipname = equip_get.name
            controlno_get = equip_get.controlno
        ##설비정보 저장하기##
            equip_check = spare_out.objects.get(no=no_up)
            equip_check.controlno = controlno_get
            equip_check.equipname = equipname
            equip_check.save()
        except:
            equipname=""
            controlno=""
            messages.error(request, "No such equipment exists.")  # 아이디 중복
        ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release": spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##오늘날짜 확인하기##
        today = date.datetime.today()
        today_date = "20" + today.strftime('%y') + "-" + today.strftime('%m') + "-" + today.strftime('%d')
    ##미입력값 확인하기##
        input_check = spare_out.objects.filter(temp_y_n="N", staff=username)
        input_check = input_check.values('equipname')
        df_input_check = pd.DataFrame.from_records(input_check)
        input_check_len = len(df_input_check.index)
        for i in range(input_check_len):
            equip_check = df_input_check.iat[i, 0]
            if equip_check == "":
                messages.error(request, "There are entries not entered.")  # 미완료 메세지
                ##정보넘기기##
                spare_release = spare_out.objects.filter(
                    Q(temp_y_n="N", staff=username) | Q(temp_y_n="D", staff=username))
                context = {"spare_release": spare_release, "loginid": loginid}
                context.update(users)
                return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결
    ##출고넘버 생성하기 변경하기##
        code_date = today.strftime('%y') + today.strftime('%m') + today.strftime('%d')
        out_code_gen = spare_out.objects.filter(date=today_date)
        out_code_gen = out_code_gen.values('date')
        df_out_code_gen = pd.DataFrame.from_records(out_code_gen)
        out_code_gen_len = len(df_out_code_gen.index)
        out_code_gen = str(code_date) + "/" + str(out_code_gen_len)
    ##부족숫자 인터락##
        count_check = spare_out.objects.filter(temp_y_n="N", staff=username)
        count_check = count_check.values()
        df_count_check = pd.DataFrame.from_records(count_check)
        count_check_len = len(df_count_check.index)
        for j in range(count_check_len):
            codeno_check = df_count_check.iat[j, 1]
            code_sum = spare_out.objects.filter(temp_y_n="N", staff=username, codeno=codeno_check).aggregate(Sum('qy'))
        #현 재고수량#
            stock_check = spare_parts_list.objects.get(codeno=codeno_check)
            now_check = stock_check.stock
        # 현 재고수량 부족 시 알람발생#
            now_check  = int(now_check) - int(code_sum['qy__sum'])
            if now_check < 0:
                text = codeno_check + "'s stock is not enough"
                messages.error(request, text)  # 미완료 메세지
        ##정보넘기기##
                spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
                context = {"spare_release": spare_release, "loginid": loginid}
                context.update(users)
                return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결
        ##토탈숫자 계산하기##
        for m in range(count_check_len):
            codeno = df_count_check.iat[m, 1]
            # 현 재고수량#
            stock_get = spare_parts_list.objects.get(codeno=codeno)
            now_stock = stock_get.stock
            # 현 재고수량 부족 시 알람발생#
            use_get = df_count_check.iat[m, 7]
            new_stock = int(now_stock) - int(use_get)
            stock_get = spare_parts_list.objects.get(codeno=codeno)
            stock_get.stock = new_stock
            stock_get.save()
    ##status 변경하기##
        status_check = spare_out.objects.filter(temp_y_n="N", staff=username)
        status_check = status_check.values('no')
        df_status_check = pd.DataFrame.from_records(status_check)
        status_check_len = len(df_status_check.index)
        for k in range(status_check_len):
            no_change = df_status_check.iat[k, 0]
            status_change = spare_out.objects.get(no=no_change)
            status_change.temp_y_n = "Y"
            status_change.date = today_date
            status_change.out_code = out_code_gen
            status_change.used_qy = status_change.qy
            status_change.save()
        ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release": spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_reset(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##삭제하기##
        del_check = spare_out.objects.filter(temp_y_n="N", staff=username)
        del_check = del_check.values('no')
        df_del_check = pd.DataFrame.from_records(del_check)
        del_check_len = len(df_del_check.index)
        for k in range(del_check_len):
            no_change = df_del_check.iat[k, 0]
            qy_check = spare_out.objects.get(no=no_change)
            qy_check.delete()
    ##정보넘기기##
        spare_release = spare_out.objects.filter(temp_y_n="N", staff=username)
        context = {"spare_release": spare_release, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_release_main.html', context)  # templates 내 html연결

def spareparts_release_list(request):
    selecttext = request.GET.get('selecttext')  # html 선택조건의 값을 받는다
    searchtext = request.GET.get('searchtext')  # html 입력 값을 받는다
    if selecttext == "codeno":
        spareparts_release = spare_out.objects.filter(codeno__icontains=searchtext, temp_y_n="Y").order_by('-date', 'out_code','team')  # db 동기화                                                                                'codeno')  # db 동기화
    elif selecttext == "partname":
        spareparts_release = spare_out.objects.filter(partname__icontains=searchtext, temp_y_n="Y").order_by('-date', 'out_code','team')  # db 동기화
    elif selecttext == "date":
        spareparts_release = spare_out.objects.filter(date__icontains=searchtext, temp_y_n="Y").order_by('-date', 'out_code','team')  # db 동기화
    elif selecttext == "out_code":
        spareparts_release = spare_out.objects.filter(out_code__icontains=searchtext, temp_y_n="Y").order_by('-date', 'out_code','team')  # db 동기화
    elif selecttext == "staff":
        spareparts_release = spare_out.objects.filter(staff__icontains=searchtext, temp_y_n="Y").order_by('-date',
                                                                                                             'out_code',
                                                                                                             'team')  # db 동기화
    else:
        spareparts_release = spare_out.objects.filter(temp_y_n="Y").order_by('-date', 'out_code','team')  # db 동기화
    context = {"spareparts_release":spareparts_release, "selecttext":selecttext,"searchtext":searchtext}
    return render(request, 'spareparts_release_list.html', context) #templates 내 html연결

def spareparts_cert_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        if selecttext == "partname":
            spare_list = spare_parts_list.objects.filter(partname__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "vendor":
            spare_list = spare_parts_list.objects.filter(vendor__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "team":
            spare_list = spare_parts_list.objects.filter(team__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "codeo":
            spare_list = spare_parts_list.objects.filter(codeno__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "stock":
            spare_list = spare_parts_list.objects.filter(stock__icontains=searchtext).order_by('team','codeno')  # db 동기화
        else:
            spare_list = spare_parts_list.objects.all().order_by('team','codeno')  # db 동기화
        context = {"spare_list": spare_list, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_cert_main.html', context)  # templates 내 html연결

def spareparts_cert_upload(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        codeno = request.POST.get('codeno')  # html에서 해당 값을 받는다
        upload_file = request.POST.get('upload_file')  # html에서 해당 값을 받는다
        print(upload_file)
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        if selecttext == "partname":
            spare_list = spare_parts_list.objects.filter(partname__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "vendor":
            spare_list = spare_parts_list.objects.filter(vendor__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "team":
            spare_list = spare_parts_list.objects.filter(team__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "codeo":
            spare_list = spare_parts_list.objects.filter(codeno__icontains=searchtext).order_by('team','codeno')  # db 동기화
        elif selecttext == "stock":
            spare_list = spare_parts_list.objects.filter(stock__icontains=searchtext).order_by('team','codeno')  # db 동기화
        else:
            spare_list = spare_parts_list.objects.all().order_by('team','codeno')  # db 동기화
    #################파일업로드하기##################
        if "upload_file" in request.FILES:
        # 파일 업로드 하기!!!
            upload_file = request.FILES["upload_file"]
            fs = FileSystemStorage()
            name = fs.save(upload_file.name, upload_file)  # 파일저장 // 이름저장
        # 파일 읽어오기!!!
            url = fs.url(name)
        else:
            file_name = "-"
            url="??"
        print(url)
        try:
            upload_get = spare_parts_list.objects.get(codeno=codeno)
            upload_get.attach = url
            upload_get.save()
        except:
            pass
        context = {"spare_list": spare_list, "loginid": loginid}
        context.update(users)
        return render(request, 'spareparts_cert_main.html', context)  # templates 내 html연결

def partslist_pm_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        parts_pm_list = parts_pm.objects.all()
        context = {"loginid": loginid,"parts_pm_list":parts_pm_list}
        context.update(users)
    return render(request, 'partslist_pm_main.html', context)  # templates 내 html연결

def partslist_pm_new(request):
    return render(request, 'partslist_pm_new.html')  # templates 내 html연결

def partslist_pm_controlno(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        ##컨트롤넘버 정보 불러오기##
        try:
            equip_info = equiplist.objects.get(controlno=controlno)
            equip_get = equip_info.name
            controlno_get = controlno
            pm_list = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
            context = {"loginid": loginid, "pm_list": pm_list, "controlno_get": controlno_get, "equip_get": equip_get}
            context.update(users)
        except:
            messages.error(request, "No such equipment exist.")  # 경고
            context = {"loginid": loginid}
        return render(request, 'partslist_pm_new.html', context)  # templates 내 html연결

def partslist_pm_maint_item(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        maint_item = request.POST.get('maint_item')  # html에서 해당 값을 받는다
        equipname = request.POST.get('equipname')  # html에서 해당 값을 받는다
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        ##컨트롤넘버 정보 불러오기##
        equip_get = equipname
        controlno_get = controlno
        freq_trans = pmmasterlist.objects.get(controlno=controlno, amd="A", pm_y_n="Y", itemcode=maint_item)
        freq_get = freq_trans.freq
        item_get = freq_trans.item
        pm_list = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
        spare_list = spare_parts_list.objects.all().order_by('team', 'codeno')
        view_signal = "Y"
        context = {"loginid": loginid, "pm_list": pm_list, "controlno_get": controlno_get, "equip_get": equip_get,
                   "freq_get":freq_get,"item_get":item_get,"spare_list":spare_list,"view_signal":view_signal,
                   "maint_item":maint_item}
        context.update(users)
        return render(request, 'partslist_pm_new.html', context)  # templates 내 html연결

def partslist_pm_maint_submit(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        controlno = request.POST.get('controlno')  # html controlform의 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
        maint_item = request.POST.get('maint_item')  # html에서 해당 값을 받는다
        equip_get = request.POST.get('equipname')  # html에서 해당 값을 받는다
        item_get = request.POST.get('item_get')  # html에서 해당 값을 받는다
        freq_get = request.POST.get('freq_get')  # html에서 해당 값을 받는다
        checks_var = request.POST.getlist('checks[]')
        qy_var = request.POST.getlist('qy_get[]')
        ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
    ##컨트롤넘버 정보 불러오기##
        controlno_get = controlno
        freq_trans = pmmasterlist.objects.get(controlno=controlno, amd="A", pm_y_n="Y", itemcode=maint_item)
        freq_get = freq_trans.freq
        item_get = freq_trans.item
        pm_list = pmmasterlist.objects.filter(controlno=controlno, amd="A", pm_y_n="Y")
        spare_list = spare_parts_list.objects.all().order_by('team', 'codeno')
    ##저장하기##
        qy_len = len(qy_var)
        for j in range(qy_len):
            if qy_var[j] == "":
               qy_var[j] = "N/A"
        while 'N/A' in qy_var:
            qy_var.remove('N/A')  # 'N/A' 삭제
        code_len = len(checks_var)
        qy_var_len = len(qy_var)
        if int(code_len) != int(qy_var_len):
            messages.error(request, "미입력되었네~")  # 경고
            view_signal = "Y"
            context = {"loginid": loginid, "pm_list": pm_list, "controlno_get": controlno_get, "equip_get": equip_get,
                       "freq_get":freq_get,"item_get":item_get,"spare_list":spare_list,"view_signal":view_signal}
            context.update(users)
            return render(request, 'partslist_pm_new.html', context)  # templates 내 html연결
        else:
            for i in range(code_len):
                code_no= checks_var[i]
                qy=qy_var[i]
                spare_get = spare_parts_list.objects.get(codeno=code_no)
                parts_pm(
                    team=freq_trans.team,
                    controlno=controlno,
                    equipname=equip_get,
                    freq=freq_get,
                    itemcode=maint_item,
                    item=item_get,
                    codeno=code_no,
                    partname=spare_get.partname,
                    vendor=spare_get.vendor,
                    modelno=spare_get.modelno,
                    qy=qy,
                    staff=username,
                ).save()
            part_list = parts_pm.objects.filter(itemcode=maint_item)
            view_signal = "Comp"
            context = {"loginid": loginid, "pm_list": pm_list, "controlno_get": controlno_get, "equip_get": equip_get,
                       "freq_get":freq_get,"item_get":item_get,"spare_list":spare_list,"view_signal":view_signal,
                       "part_list":part_list}
            context.update(users)
            return render(request, 'partslist_pm_new.html', context)  # templates 내 html연결

##############################################################################################################
#################################################Test########################################################
##############################################################################################################

def roomlist_main(request):
    if request.method == 'POST':  # 매소드값이 post인 값만 받는다
        selecttext = request.POST.get('selecttext')  # html 선택조건의 값을 받는다
        searchtext = request.POST.get('searchtext')  # html 입력 값을 받는다
        loginid = request.POST.get('loginid')  # html에서 해당 값을 받는다
    ##이름 및 권한 끌고다니기##
        users = userinfo.objects.get(userid=loginid)
        username = users.username
        userteam = users.userteam
        password = users.password
        auth = users.auth1
        user_div = users.user_division
        users = {"auth": auth, "password": password, "username": username, "userteam": userteam, "user_div": user_div}
        context = {"loginid": loginid}
        context.update(users)
        return render(request, 'roomlist_main.html', context)  # templates 내 html연결
##############################################################################################################
#################################################Test########################################################
##############################################################################################################
def temp(request):
    #cap = cv2.VideoCapture(0)
    #i = 0
    #while (cap.isOpened()):
    #    ret, img = cap.read()
    #    if not ret:
    #        continue
    #    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #    decoded = pyzbar.decode(gray)
    #    for d in decoded:
    #        x, y, w, h = d.rect
    #        barcode_data = d.data.decode("utf-8")
    #        barcode_type = d.type
    #        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #        text = '%s (%s)' % (barcode_data, barcode_type)
    #        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
    #    cv2.imshow('img', img)
    #    key = cv2.waitKey(1)
    #    if key == ord('q'):
    #        break
    #    elif key == ord('s'):
    #        i += 1
    #        cv2.imwrite('c_%03d.jpg' % i, img)
    #cap.release()
    #cv2.destroyAllWindows()
    #test= "111122223333"
    #ean = barcode.get('ean13', test, writer=ImageWriter())
    #fullname = ean.save(test)
    return render(request, 'temp.html') #templates 내 html연결

