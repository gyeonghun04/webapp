from django.db import models

# Create your models here.

class equiplist(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    controlno = models.CharField(max_length=255) #컨트롤넘버
    team = models.CharField(max_length=255) #팀명
    name = models.CharField(max_length=255) #설비명
    model = models.TextField() # 모델이름
    serial = models.TextField() #시리얼넘버
    maker = models.CharField(max_length=255) #제조사
    roomname = models.CharField(max_length=255) #룸명
    roomno = models.CharField(max_length=255) #룸번호
    setupdate = models.CharField(max_length=255) # 설비셋업일
    pq = models.CharField(max_length=45, default="N") # pq (Y or N)
    pmok = models.CharField(max_length=45, default="New") # pm여부 (Y or N)
    pmresult = models.CharField(max_length=45, default="New") # pmstandard (PQ, Manual, IT, None)
    score_f = models.CharField(max_length=255) # Frequency of Use
    count_y = models.CharField(max_length=255) # score_y count
    score_y = models.CharField(max_length=255) # 연식
    pmscore = models.CharField(max_length=45, default="New") # pmscore (score_f + score_y)
    ra = models.CharField(max_length=255, default="New") # result score (___months)
    status = models.CharField(max_length=255, default="New") #상태
    recheck = models.CharField(max_length=255, default="N") # ra다시알람
    p_name = models.CharField(max_length=255, default="None") # 작성자 이름
    p_date = models.CharField(max_length=255, default="None") # 작성자 날짜
    a_name = models.CharField(max_length=255, default="None") # 승인자 이름
    a_date = models.CharField(max_length=255, default="None") # 승인자 날짜
    pmok_temp = models.CharField(max_length=45, default="New") # pm여부 (Y or N) // 결재 전 임시저장
    pmresult_temp = models.CharField(max_length=45, default="New") # pmstandard (PQ, Manual, IT, None) // 결재 전 임시저장
    score_f_temp = models.CharField(max_length=255) # Frequency of Use // 결재 전 임시저장
    score_y_temp = models.CharField(max_length=255) # equipment manual // 결재 전 임시저장
    pmscore_temp = models.CharField(max_length=45, default="New") # pmscore (score_f * score_y) // 결재 전 임시저장
    ra_temp = models.CharField(max_length=255, default="New") # result score (___months) // 결재 전 임시저장
    p_name_temp = models.CharField(max_length=255, default="None") # 작성자 이름 // 결재 전 임시저장
    p_date_temp = models.CharField(max_length=255, default="None") # 작성자 날짜 // 결재 전 임시저장
    pic = models.TextField(default="N/A") #설비사진

    class Meta:
        managed = False
        db_table = 'equiplist'

class controlformlist(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    controlno = models.CharField(max_length=255) #컨트롤넘버
    team = models.CharField(max_length=255) #팀명
    name = models.CharField(max_length=255) #설비명
    status = models.CharField(max_length=255, default="New") #상태(New > Prepared > Reviewed > Complete)
    revno = models.CharField(max_length=255, default="0") #리비젼넘버
    revdate = models.CharField(max_length=255, default="None") #리비젼데이트
    p_name = models.CharField(max_length=255, default="None") #작성자이름
    p_date = models.CharField(max_length=255, default="Unapproved") #작성자승인일
    r_name = models.CharField(max_length=255, default="None") #팀장이름
    r_date = models.CharField(max_length=255, default="Unapproved") #팀장승인일
    a_name = models.CharField(max_length=255, default="None") #큐팀장이름
    a_date = models.CharField(max_length=255, default="Unapproved") #큐팀장승인일
    p_name_temp = models.CharField(max_length=255, default="None")  # 팀장이름_임시
    p_date_temp = models.CharField(max_length=255, default="Unapproved")  # 팀장승인일_임시
    r_name_temp = models.CharField(max_length=255, default="None")  # 팀장이름_임시
    r_date_temp = models.CharField(max_length=255, default="Unapproved")  # 팀장승인일_임시
    a_name_temp = models.CharField(max_length=255, default="None")  # 팀장이름_임시
    a_date_temp = models.CharField(max_length=255, default="Unapproved")  # 팀장승인일_임시
    recent_y = models.CharField(max_length=255, default="N") #최신

    class Meta:
        managed = False
        db_table = 'controlformlist'

class pmmasterlist(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255) #팀명
    controlno = models.CharField(max_length=255) #컨트롤넘버
    name = models.CharField(max_length=255) #설비명
    model = models.CharField(max_length=255) # 모델이름
    serial = models.CharField(max_length=255) #시리얼넘버
    maker = models.CharField(max_length=255) #제조사
    roomname = models.CharField(max_length=255) #룸명
    roomno = models.CharField(max_length=255) #룸번호
    revno = models.CharField(max_length=255, default="0") #리비젼번호
    date = models.CharField(max_length=255, default="None") #컨트롤폼 승인일
    freq = models.CharField(max_length=255, default="None") #주기
    ra = models.CharField(max_length=255) # 주기기준
    sheetno = models.CharField(max_length=255, default="None") #피엠시트번호
    amd = models.CharField(max_length=255, default="None") #컨트롤폼 구분좌
    itemno = models.CharField(max_length=255) #컨트롤폼 순번입력
    item = models.TextField( default="None") #메인트넌스아이템
    check = models.TextField( default="None") #체크스텐다드
    startdate = models.CharField(max_length=255) #시작일
    change = models.CharField(max_length=255, default="New") #변경사유
    itemcode = models.CharField(max_length=255) # 체크아이템 코드넘버
    division = models.CharField(max_length=255) # 구분좌
    pm_y_n = models.CharField(max_length=255, default="N") # pm최신본

    class Meta:
        managed = False
        db_table = 'pmmasterlist'

class pmmasterlist_temp(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255) #팀명
    controlno = models.CharField(max_length=255) #컨트롤넘버
    name = models.CharField(max_length=255) #설비명
    model = models.CharField(max_length=255) # 모델이름
    serial = models.CharField(max_length=255) #시리얼넘버
    maker = models.CharField(max_length=255) #제조사
    roomname = models.CharField(max_length=255) #룸명
    roomno = models.CharField(max_length=255) #룸번호
    revno = models.CharField(max_length=255, default="0") #리비젼번호
    date = models.CharField(max_length=255, default="None") #컨트롤폼 승인일
    freq = models.CharField(max_length=255, default="None") #주기
    ra = models.CharField(max_length=255) # 주기기준
    sheetno = models.CharField(max_length=255, default="None") #피엠시트번호
    amd = models.CharField(max_length=255, default="None") #컨트롤폼 구분좌
    itemno = models.CharField(max_length=255) #컨트롤폼 순번입력
    item = models.TextField( default="None") #메인트넌스아이템
    check = models.TextField( default="None") #체크스텐다드
    startdate = models.CharField(max_length=255) #시작일
    change = models.CharField(max_length=255, default="New") #변경사유
    itemcode = models.CharField(max_length=255)# 체크아이템 코드넘버
    division = models.CharField(max_length=255) # 구분좌

    class Meta:
        managed = False
        db_table = 'pmmasterlist_temp'

class pmsheetdb(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    controlno = models.CharField(max_length=255) #pmsheetno
    pmsheetno = models.CharField(max_length=255) #pmsheetno
    startdate = models.CharField(max_length=255) #pm sheet 시작일
    freq = models.CharField(max_length=255) #주기
    pmsheetno_temp = models.CharField(max_length=255) #pmsheetno 임시저장
    startdate_temp = models.CharField(max_length=255) #pm sheet 시작일 임시저장
    freq_temp = models.CharField(max_length=255) #주기 임시저장
    filter_check = models.CharField(max_length=45, default="N") #주기 임시저장

    class Meta:
        managed = False
        db_table = 'pmsheetdb'

class pmchecksheet(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255) #컨트롤넘버
    controlno = models.CharField(max_length=255) #컨트롤넘버
    pmsheetno = models.CharField(max_length=255) #pmsheetno
    date = models.CharField(max_length=255) #pm진행일
    pmcode = models.CharField(max_length=255) #pmsheetno + / + date
    itemcode = models.CharField(max_length=255) # 체크아이템 코드넘버
    item = models.TextField() #pm 항목
    check = models.TextField() #pm점검기준
    result = models.TextField() #pm 결과
    pass_y = models.CharField(max_length=255) #pm 결과pass
    fail_y = models.CharField(max_length=255) #pm 결과fail/당일 조치완료
    fail_n = models.CharField(max_length=255) #pm 결과fail/워크리퀘스트 발송
    actiondetail = models.TextField() #fail에 대한 결과
    workrequest = models.CharField(max_length=255, default="") #Work Request로 전송
    usedpart = models.CharField(max_length=255) #pm 사용자재 링크
    result_temp = models.TextField() #pm 결과 임시
    pass_y_temp = models.CharField(max_length=255, default="") #pm 결과pass 임시
    fail_y_temp = models.CharField(max_length=255, default="") #pm 결과fail/당일 조치완료 임시
    fail_n_temp = models.CharField(max_length=255, default="") #pm 결과fail/워크리퀘스트 발송 임시
    actiondetail_temp = models.TextField(default="") #fail에 대한 결과 임시
    usedpart_temp = models.CharField(max_length=255, default="") #pm 사용자재 링크 임시
    workrequest_temp = models.CharField(max_length=255, default="") #Work Request로 전송

    class Meta:
        managed = False
        db_table = 'pmchecksheet'

class pm_sch(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255) #팀
    pmsheetno = models.CharField(max_length=255) #pmsheetno
    pmcode = models.CharField(max_length=255) #pmsheetno + / + date
    status = models.CharField(max_length=255, default="Not Fixed") #pm진행일
    revno = models.CharField(max_length=255) #리비젼넘버
    revdate = models.CharField(max_length=255) #리비젼데이트
    controlno = models.CharField(max_length=255) #컨트롤넙버
    name = models.CharField(max_length=255) #설비명
    roomno = models.CharField(max_length=255) #룸넘버
    roomname = models.CharField(max_length=255) #룸명
    date = models.CharField(max_length=255) #계획년월
    plandate = models.CharField(max_length=255) #계획일
    actiondate = models.CharField(max_length=255, default="Not Checked") #실행일
    remark = models.TextField(default="") #기타 추가 기입
    remark_na = models.CharField(max_length=255) #리마크 엔에이표시
    plandate_temp = models.CharField(max_length=255) #계획일_임시
    actiondate_temp = models.CharField(max_length=255, default="Not Checked") #실행일_임시
    sch_clear = models.CharField(max_length=255, default="N") #스케줄 확정
    pmchecksheet_y_n = models.CharField(max_length=255, default="N") #pmchecksheet에 반영
    remark_temp = models.TextField(default="") #기타 추가 기입 임시
    remark_na_temp = models.CharField(max_length=255) #리마크 엔에이표시 임시
    p_name = models.CharField(max_length=255, default="")  # 작성자이름
    p_date = models.CharField(max_length=255, default="")  # 작성자승인일
    r_name = models.CharField(max_length=255, default="")  # 중간관리자 이름
    r_date = models.CharField(max_length=255, default="")  # 중간관리자 승인일
    r_name_temp = models.CharField(max_length=255, default="")  # 중간관리자 이름_임시
    r_date_temp = models.CharField(max_length=255, default="")  # 중간관리자 승인일_임시
    a_name = models.CharField(max_length=255, default="")  # 팀장이름
    a_date = models.CharField(max_length=255, default="")  # 팀장승인일
    attach = models.TextField(default="N/A") #첨부파일 어드레스주소
    attach_temp = models.TextField(default="N/A") #첨부파일 어드레스 주소 임시
    annual_date = models.TextField() #연간스케줄업데이트
    delete_signal = models.CharField(max_length=255, default="N")  # 시트영구삭제신호

    class Meta:
        managed = False
        db_table = 'pm_sch'

class pm_reference(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    description = models.CharField(max_length=255) #reference 내용
    freq_m_y = models.CharField(max_length=255) #freq 숫자
    m_y = models.CharField(max_length=255) #년 OR 월

    class Meta:
        managed = False
        db_table = 'pm_reference'

class pm_manual(models.Model): #PM Master List Table
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255)  # 팀
    controlno = models.CharField(max_length=255)  # 컨트롤넘버
    name = models.CharField(max_length=255)  # 설비명
    division = models.CharField(max_length=255)  # 메뉴얼 구분
    partname = models.CharField(max_length=255)  # 파츠이름
    url = models.TextField()  # 유알엘주소
    maker = models.CharField(max_length=255)  # 파츠메이커
    userid = models.CharField(max_length=255)  # 업로드한 사람
    date = models.CharField(max_length=255)  # 업로드 날짜
    class Meta:
        managed = False
        db_table = 'pm_manual'

class userinfo(models.Model):  # 유저 테이블
    no = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    userteam = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    useremail = models.CharField(max_length=255)
    auth1 = models.CharField(max_length=255)
    user_division = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "userinfo"

class approval_information(models.Model):  # 승인권한자 설정
    no = models.AutoField(primary_key=True)
    division = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    auth_team = models.CharField(max_length=255)
    auth_name = models.CharField(max_length=255)
    code_no = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "approval_information"

class workorder(models.Model):  #
    no = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    capa = models.CharField(max_length=255)
    requestor = models.CharField(max_length=255)
    team = models.CharField(max_length=255)
    controlno = models.CharField(max_length=255)
    equipname = models.CharField(max_length=255)
    roomname = models.CharField(max_length=255)
    roomno = models.CharField(max_length=255)
    description = models.TextField()
    req_date = models.CharField(max_length=255, default="")
    req_reason = models.TextField()
    date = models.CharField(max_length=255)
    r_t_name = models.CharField(max_length=255)
    r_t_date = models.CharField(max_length=255)
    r_s_name = models.CharField(max_length=255)
    r_s_date = models.CharField(max_length=255)
    r_m_name = models.CharField(max_length=255)
    r_m_date = models.CharField(max_length=255)
    r_q_name = models.CharField(max_length=255)
    r_q_date = models.CharField(max_length=255)
    r_attach = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255)
    workorderno = models.CharField(max_length=255)
    work_desc = models.TextField(max_length=255)
    action_name = models.CharField(max_length=255)
    action_company = models.CharField(max_length=255)
    action_date = models.CharField(max_length=255)
    test_result = models.TextField()
    usedpart = models.CharField(max_length=255, default="")
    pm_trans = models.CharField(max_length=255)
    w_s_name = models.CharField(max_length=255)
    w_s_date = models.CharField(max_length=255)
    w_m_name = models.CharField(max_length=255)
    w_m_date = models.CharField(max_length=255)
    w_q_name = models.CharField(max_length=255)
    w_q_date = models.CharField(max_length=255)
    w_attach = models.CharField(max_length=255, default="")
    repair_type = models.CharField(max_length=255, default="N/A")
    detail_type = models.CharField(max_length=255, default="")
    repair_method = models.TextField(default="")
    description_info = models.TextField()
    workorder_y_n = models.CharField(max_length=255,default="N")
    class Meta:
        managed = False
        db_table = "workorder"

class spare_parts_list(models.Model): #spare_parts_list
    no = models.AutoField(primary_key=True) #순번
    codeno= models.CharField(max_length=255) #코드넘버
    team = models.CharField(max_length=255) #팀
    partname = models.CharField(max_length=255) #부품명
    vendor = models.CharField(max_length=255) #업체명
    modelno = models.TextField() #모델명
    spec = models.TextField() #사양
    location = models.CharField(max_length=255) #부품위치
    stock = models.CharField(max_length=255) #재고
    staff = models.CharField(max_length=255) #담당자
    attach = models.CharField(max_length=255) #첨부파일
    pm_link = models.CharField(max_length=255, default="N") #pm링크
    safety_stock = models.CharField(max_length=255) #안전재고
    check_y_n_temp = models.CharField(max_length=255)  #사용여부
    req_qy = models.CharField(max_length=255, default=0)  #요구수량
    short_qy = models.CharField(max_length=255)  #부족수량
    contact_y_n = models.CharField(max_length=255)  # 스페어 구매체크
    used_qy_sum = models.CharField(max_length=255)  # 작년도 소요슈량

    class Meta:
        managed = False
        db_table = 'spare_parts_list'

class spare_in(models.Model): #spare_in
    no = models.AutoField(primary_key=True) #순번
    codeno= models.CharField(max_length=255) #코드넘버
    team = models.CharField(max_length=255)  # 팀
    partname = models.CharField(max_length=255)  # 부품명
    vendor = models.CharField(max_length=255)  # 업체명
    modelno = models.TextField()  # 모델명
    staff = models.CharField(max_length=255) #담당자
    qy = models.CharField(max_length=255) #입고수량
    division = models.CharField(max_length=255) #입고구분
    location = models.CharField(max_length=255)  # 부품위치
    date = models.CharField(max_length=255) #입고일자
    in_code = models.CharField(max_length=255) #입고코드
    temp_y_n = models.CharField(max_length=255) #승인여부

    class Meta:
        managed = False
        db_table = 'spare_in'

class spare_out(models.Model): #spare_out
    no = models.AutoField(primary_key=True) #순번
    codeno= models.CharField(max_length=255) #코드넘버
    team = models.CharField(max_length=255)  # 팀
    partname = models.CharField(max_length=255)  # 부품명
    vendor = models.CharField(max_length=255)  # 업체명
    modelno = models.TextField()  # 모델명
    staff = models.CharField(max_length=255) #담당자
    qy = models.IntegerField() #출고수량
    date = models.CharField(max_length=255) #입고일자
    controlno = models.CharField(max_length=255) #설비명
    out_code = models.CharField(max_length=255) #출고코드
    temp_y_n = models.CharField(max_length=255) #승인여부
    location = models.CharField(max_length=255)  # 부품위치
    equipname = models.CharField(max_length=255, default="")  # 설비명
    used_y_n = models.CharField(max_length=255, default="")  #사용여부
    used_y_n_temp = models.CharField(max_length=255, default="")  #사용여부
    check_y_n = models.CharField(max_length=255)  #사용여부
    check_y_n_temp = models.CharField(max_length=255)  #사용여부
    used_qy = models.CharField(max_length=255)  #실 사용수량

    class Meta:
        managed = False
        db_table = 'spare_out'

class parts_pm(models.Model): #spare_out
    no = models.AutoField(primary_key=True) #순번
    team = models.CharField(max_length=255)  # 담당자
    controlno = models.CharField(max_length=255) #설비명
    equipname = models.CharField(max_length=255)  # 설비명
    freq = models.CharField(max_length=255)  # 설비명
    itemcode = models.CharField(max_length=255)  # 설비명
    item = models.TextField()  # 메인트넌스 아이템
    codeno= models.CharField(max_length=255) #코드넘버
    partname = models.CharField(max_length=255)  # 부품명
    vendor = models.CharField(max_length=255)  # 업체명
    modelno = models.TextField()  # 모델명
    qy = models.CharField(max_length=255) #입고수량
    staff = models.CharField(max_length=255)  # 담당자
    sch = models.CharField(max_length=255)  # 올해,내년도 스케줄
    plan_date = models.CharField(max_length=255)  # 내년스케줄 계산
    location = models.CharField(max_length=255)  # 자재위치
    qy_plan = models.CharField(max_length=255)  # 총 필요수량

    class Meta:
        managed = False
        db_table = 'parts_pm'

class room_db(models.Model): #spare_out
    no = models.AutoField(primary_key=True) #순번
    roomname = models.CharField(max_length=255)  # 담당자
    roomno = models.CharField(max_length=255)  # 담당자

    class Meta:
        managed = False
        db_table = 'room_db'

class audit_trail(models.Model): #spare_out
    no = models.AutoField(primary_key=True) #순번
    date = models.CharField(max_length=255)  # 변경일
    time = models.CharField(max_length=255)  # 변경시간
    document = models.CharField(max_length=255,default="N/A")  # 문서명
    document_no = models.CharField(max_length=255,default="N/A")  # 문서번호
    user = models.CharField(max_length=255)  # 담당자
    division = models.CharField(max_length=255)  # 구분
    controlno = models.CharField(max_length=255,default="N/A")  # 설비번호
    comment = models.TextField(default="N/A")  # 코멘트
    old_value = models.TextField(default="N/A")  # 이전값
    new_value = models.TextField(default="N/A")  # 신규값

    class Meta:
        managed = False
        db_table = 'audit_trail'

class vendor_list(models.Model): #spare_out
    no = models.AutoField(primary_key=True) #순번
    vendor = models.CharField(max_length=255)  # 업체명
    name = models.CharField(max_length=255)  # 이름
    tel = models.CharField(max_length=255,default="N/A")  # 전화번호
    email = models.CharField(max_length=255,default="N/A")  # 이메일주소
    description = models.TextField(default="N/A")  # 업체 설명
    contact_y_n = models.CharField(max_length=255)  # 메일체크

    class Meta:
        managed = False
        db_table = 'vendor_list'