"""pmpjt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,  include
import pm.views #앱이름/뷰스
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
#홈페이지
    path('', pm.views.login, name='login'),
    path('main', pm.views.main, name='main'),
    path('logout_page', pm.views.logout_page, name='logout_page'),
    path('login_again', pm.views.login_again, name='login_again'),
    path('information_main', pm.views.information_main, name='information_main'),
    path('audittrail_main', pm.views.audittrail_main, name='audittrail_main'),
    path('audittrail_view', pm.views.audittrail_view, name='audittrail_view'),
    path('audittrail_click', pm.views.audittrail_click, name='audittrail_click'),

##########################################################################################################################################
##########################################################################################################################################

####PM Check Sheet####
    path('pmchecksheet_main', pm.views.pmchecksheet_main, name='pmchecksheet_main'),
    path('pmchecksheet_view', pm.views.pmchecksheet_view, name='pmchecksheet_view'),
    path('pmchecksheet_write', pm.views.pmchecksheet_write, name='pmchecksheet_write'),
    path('pmchecksheet_checkresult', pm.views.pmchecksheet_checkresult, name='pmchecksheet_checkresult'),
    path('pmchecksheet_checkboxform', pm.views.pmchecksheet_checkboxform, name='pmchecksheet_checkboxform'),
    path('pmchecksheet_actiondetail', pm.views.pmchecksheet_actiondetail, name='pmchecksheet_actiondetail'),
    path('pmchecksheet_remark', pm.views.pmchecksheet_remark, name='pmchecksheet_remark'),
    path('pmchecksheet_submit', pm.views.pmchecksheet_submit, name='pmchecksheet_submit'),
    path('pmchecksheet_return', pm.views.pmchecksheet_return, name='pmchecksheet_return'),
    path('pmchecksheet_remark_na', pm.views.pmchecksheet_remark_na, name='pmchecksheet_remark_na'),
    path('pmchecksheet_workrequest', pm.views.pmchecksheet_workrequest, name='pmchecksheet_workrequest'),
    path('pmcheck_workrequest_up', pm.views.pmcheck_workrequest_up, name='pmcheck_workrequest_up'),
    path('pmcheck_workrequest_submit', pm.views.pmcheck_workrequest_submit, name='pmcheck_workrequest_submit'),
    path('used_parts_link', pm.views.used_parts_link, name='used_parts_link'),
    path('used_parts_link_click', pm.views.used_parts_link_click, name='used_parts_link_click'),
    path('used_parts_link_submit', pm.views.used_parts_link_submit, name='used_parts_link_submit'),
    path('used_parts_link_minus', pm.views.used_parts_link_minus, name='used_parts_link_minus'),
    path('used_parts_link_plus', pm.views.used_parts_link_plus, name='used_parts_link_plus'),


####PM Check Sheet Approval####
    path('pmcheckapproval_main', pm.views.pmcheckapproval_main, name='pmcheckapproval_main'),
    path('pmcheckapproval_check', pm.views.pmcheckapproval_check, name='pmcheckapproval_check'),
    path('pmcheckapproval_review_accept', pm.views.pmcheckapproval_review_accept, name='pmcheckapproval_review_accept'),
    path('pmcheckapproval_approve_accept', pm.views.pmcheckapproval_approve_accept, name='pmcheckapproval_approve_accept'),
    path('pmchecksheet_upload', pm.views.pmchecksheet_upload, name='pmchecksheet_upload'),
    path('pmcheckapproval_review_reject', pm.views.pmcheckapproval_review_reject, name='pmcheckapproval_review_reject'),
    path('pmcheckapproval_approve_reject', pm.views.pmcheckapproval_approve_reject,name='pmcheckapproval_approve_reject'),

####Equipment Schedule####
    path('pmequipsch_main', pm.views.pmequipsch_main, name='pmequipsch_main'),
    path('pmequipsch_view', pm.views.pmequipsch_view, name='pmequipsch_view'),
    path('pm_fullscreen', pm.views.pm_fullscreen, name='pm_fullscreen'),

####PM Monthly SCH####
    path('pmmonthly_main', pm.views.pmmonthly_main, name='pmmonthly_main'),
    path('pmmonthly_search', pm.views.pmmonthly_search, name='pmmonthly_search'),
    path('pmmonthly_view', pm.views.pmmonthly_view, name='pmmonthly_view'),
    path('pmmonthly_plandate', pm.views.pmmonthly_plandate, name='pmmonthly_plandate'),
    path('pmmonthly_submit', pm.views.pmmonthly_submit, name='pmmonthly_submit'),

####PM Calendar####
    path('pmcalendar_main', pm.views.pmcalendar_main, name='pmcalendar_main'),
    path('pmcalendar_view', pm.views.pmcalendar_view, name='pmcalendar_view'),
    path('pmcalendar_write', pm.views.pmcalendar_write, name='pmcalendar_write'),
    path('pmcalendar_checkresult', pm.views.pmcalendar_checkresult, name='pmcalendar_checkresult'),
    path('pmcalendar_checkboxform', pm.views.pmcalendar_checkboxform, name='pmcalendar_checkboxform'),
    path('pmcalendar_actiondetail', pm.views.pmcalendar_actiondetail, name='pmcalendar_actiondetail'),
    path('pmcalendar_remark', pm.views.pmcalendar_remark, name='pmcalendar_remark'),
    path('pmcalendar_submit', pm.views.pmcalendar_submit, name='pmcalendar_submit'),
    path('pmcalendar_return', pm.views.pmcalendar_return, name='pmcalendar_return'),
    path('pmcalendar_remark_na', pm.views.pmcalendar_remark_na, name='pmcalendar_remark_na'),
    path('pmcalendar_upload', pm.views.pmcalendar_upload, name='pmcalendar_upload'),

##########################################################################################################################################
##########################################################################################################################################

####PM CONTROL FORM####
    path('pmcontrolform_main', pm.views.pmcontrolform_main, name='pmcontrolform_main'),
    path('pmcontrolform_view', pm.views.pmcontrolform_view, name='pmcontrolform_view'),
    path('pmcontrolform_write', pm.views.pmcontrolform_write, name='pmcontrolform_write'),
    path('pmcontrolform_write_new', pm.views.pmcontrolform_write_new, name='pmcontrolform_write_new'),
    path('pmcontrolform_write_delete', pm.views.pmcontrolform_write_delete, name='pmcontrolform_write_delete'),
    path('pmsheet_startdate', pm.views.pmsheet_startdate, name='pmsheet_startdate'),
    path('pmcontrolform_submit', pm.views.pmcontrolform_submit, name='pmcontrolform_submit'),
    path('pmcontrolform_return', pm.views.pmcontrolform_return, name='pmcontrolform_return'),
    path('pmcontrolform_change_new', pm.views.pmcontrolform_change_new, name='pmcontrolform_change_new'),
    path('pmcontrolform_change_division', pm.views.pmcontrolform_change_division, name='pmcontrolform_change_division'),
    path('pmcontrolform_change_link', pm.views.pmcontrolform_change_link, name='pmcontrolform_change_link'),
    path('pmcontrolform_change_controlno', pm.views.pmcontrolform_change_controlno, name='pmcontrolform_change_controlno'),
    path('pmcontrolform_change_link_submit', pm.views.pmcontrolform_change_link_submit, name='pmcontrolform_change_link_submit'),

####PM Assessment of Period####
    path('pmra_main', pm.views.pmra_main, name='pmra_main'),
    path('pmra_view', pm.views.pmra_view, name='pmra_view'),
    path('pmra_write', pm.views.pmra_write, name='pmra_write'),
    path('pm_write_standard', pm.views.pm_write_standard, name='pm_write_standard'),
    path('pmwritescore', pm.views.pmwritescore, name='pmwritescore'),
    path('pmra_write_prepared', pm.views.pmra_write_prepared, name='pmra_write_prepared'),
    path('pmra_write_approved', pm.views.pmra_write_approved, name='pmra_write_approved'),
    path('pmra_review', pm.views.pmra_review, name='pmra_review'),

####PM Approval####
    path('pmapproval_main', pm.views.pmapproval_main, name='pmapproval_main'),
    path('pmapproval_view', pm.views.pmapproval_view, name='pmapproval_view'),
    path('pmapproval_check_accept', pm.views.pmapproval_check_accept, name='pmapproval_check_accept'),
    path('pmapproval_check_reject', pm.views.pmapproval_check_reject, name='pmapproval_check_reject'),
    path('pmapproval_approved_accept', pm.views.pmapproval_approved_accept, name='pmapproval_approved_accept'),
    path('pmapproval_approved_reject', pm.views.pmapproval_approved_reject, name='pmapproval_approved_reject'),

####PM Manual####
    path('pmmanual_main', pm.views.pmmanual_main, name='pmmanual_main'),
    path('pmmanual_new', pm.views.pmmanual_new, name='pmmanual_new'),
    path('pmmanual_upload', pm.views.pmmanual_upload, name='pmmanual_upload'),
    path('pmmanual_submit', pm.views.pmmanual_submit, name='pmmanual_submit'),
    path('pmmanual_regi', pm.views.pmmanual_regi, name='pmmanual_regi'),

##########################################################################################################################################
##########################################################################################################################################

####Work Request####
    path('workrequest_new', pm.views.workrequest_new, name='workrequest_new'),
    path('workrequest_main', pm.views.workrequest_main, name='workrequest_main'),
    path('workrequest_controlno', pm.views.workrequest_controlno, name='workrequest_controlno'),
    path('workrequest_submit', pm.views.workrequest_submit, name='workrequest_submit'),
    path('workrequest_upload', pm.views.workrequest_upload, name='workrequest_upload'),
    path('workrequest_comp', pm.views.workrequest_comp, name='workrequest_comp'),
    path('workrequest_view', pm.views.workrequest_view, name='workrequest_view'),
    path('workrequest_receive', pm.views.workrequest_receive, name='workrequest_receive'),
    path('workrequest_r_s_accept', pm.views.workrequest_r_s_accept, name='workrequest_r_s_accept'),
    path('workrequest_r_m_accept', pm.views.workrequest_r_m_accept, name='workrequest_r_m_accept'),
    path('workrequest_r_t_accept', pm.views.workrequest_r_t_accept, name='workrequest_r_t_accept'),
    path('workrequest_r_q_accept', pm.views.workrequest_r_q_accept, name='workrequest_r_q_accept'),
    path('workorderlist_main', pm.views.workorderlist_main, name='workorderlist_main'),

    path('workorder_approval_main', pm.views.workorder_approval_main, name='workorder_approval_main'),
    path('workorder_approval_view', pm.views.workorder_approval_view, name='workorder_approval_view'),
    path('workrequest_approval_main', pm.views.workrequest_approval_main, name='workrequest_approval_main'),
    path('workrequest_approval', pm.views.workrequest_approval, name='workrequest_approval'),
    path('workorder_w_s_accept', pm.views.workorder_w_s_accept, name='workorder_w_s_accept'),
    path('workorder_w_m_accept', pm.views.workorder_w_m_accept, name='workorder_w_m_accept'),
    path('workorder_w_q_accept', pm.views.workorder_w_q_accept, name='workorder_w_q_accept'),
    path('workorder_return', pm.views.workorder_return, name='workorder_return'),
    path('history_of_repair_main', pm.views.history_of_repair_main, name='history_of_repair_main'),
    path('workorderlist_request', pm.views.workorderlist_request, name='workorderlist_request'),
    path('workorderlist_request_main', pm.views.workorderlist_request_main, name='workorderlist_request_main'),
    path('workorderlist_request_print', pm.views.workorderlist_request_print, name='workorderlist_request_print'),
    path('workorderlist_order', pm.views.workorderlist_order, name='workorderlist_order'),
    path('workorderlist_order_main', pm.views.workorderlist_order_main, name='workorderlist_order_main'),
    path('workorderlist_order_print', pm.views.workorderlist_order_print, name='workorderlist_order_print'),
####Work Order####
    path('workorder_main', pm.views.workorder_main, name='workorder_main'),
    path('workorder_form', pm.views.workorder_form, name='workorder_form'),
    path('workorder_submit', pm.views.workorder_submit, name='workorder_submit'),
    path('workorder_pmcontrolform', pm.views.workorder_pmcontrolform, name='workorder_pmcontrolform'),
    path('workorder_pmcontrolform_submit', pm.views.workorder_pmcontrolform_submit,
         name='workorder_pmcontrolform_submit'),
    path('workorder_upload', pm.views.workorder_upload, name='workorder_upload'),
    path('workorder_used_part', pm.views.workorder_used_part, name='workorder_used_part'),
    path('workorder_used_click', pm.views.workorder_used_click, name='workorder_used_click'),
    path('workorder_used_submit', pm.views.workorder_used_submit, name='workorder_used_submit'),
    path('workorder_used_minus', pm.views.workorder_used_minus, name='workorder_used_minus'),
    path('workorder_used_plus', pm.views.workorder_used_plus, name='workorder_used_plus'),
    path('workorder_used_delete', pm.views.workorder_used_delete, name='workorder_used_delete'),

##########################################################################################################################################
##########################################################################################################################################
####Spare Parts ####
    path('spareparts_main', pm.views.spareparts_main,name='spareparts_main'),
    path('spareparts_new', pm.views.spareparts_new, name='spareparts_new'),
    path('spareparts_new_submit', pm.views.spareparts_new_submit, name='spareparts_new_submit'),
    path('spareparts_release_main', pm.views.spareparts_release_main, name='spareparts_release_main'),
    path('spareparts_release_scan', pm.views.spareparts_release_scan, name='spareparts_release_scan'),
    path('spareparts_release_minus', pm.views.spareparts_release_minus, name='spareparts_release_minus'),
    path('spareparts_release_plus', pm.views.spareparts_release_plus, name='spareparts_release_plus'),
    path('spareparts_release_delete', pm.views.spareparts_release_delete, name='spareparts_release_delete'),
    path('spareparts_release_controlno', pm.views.spareparts_release_controlno, name='spareparts_release_controlno'),
    path('spareparts_release_item', pm.views.spareparts_release_item, name='spareparts_release_item'),
    path('spareparts_release_table_controlno', pm.views.spareparts_release_table_controlno, name='spareparts_release_table_controlno'),
    path('spareparts_release_submit', pm.views.spareparts_release_submit,name='spareparts_release_submit'),
    path('spareparts_release_reset', pm.views.spareparts_release_reset, name='spareparts_release_reset'),
    path('spareparts_release_list', pm.views.spareparts_release_list, name='spareparts_release_list'),
    path('spareparts_incoming_main', pm.views.spareparts_incoming_main, name='spareparts_incoming_main'),
    path('spareparts_incoming_search', pm.views.spareparts_incoming_search, name='spareparts_incoming_search'),
    path('spareparts_incoming_select', pm.views.spareparts_incoming_select, name='spareparts_incoming_select'),
    path('spareparts_incoming_sel_submit', pm.views.spareparts_incoming_sel_submit, name='spareparts_incoming_sel_submit'),
    path('spareparts_incoming_reset', pm.views.spareparts_incoming_reset, name='spareparts_incoming_reset'),
    path('spareparts_incoming_submit', pm.views.spareparts_incoming_submit, name='spareparts_incoming_submit'),
    path('spareparts_incoming_delete', pm.views.spareparts_incoming_delete, name='spareparts_incoming_delete'),
    path('spareparts_incoming_minus', pm.views.spareparts_incoming_minus, name='spareparts_incoming_minus'),
    path('spareparts_incoming_plus', pm.views.spareparts_incoming_plus, name='spareparts_incoming_plus'),
    path('spareparts_incoming_location', pm.views.spareparts_incoming_location, name='spareparts_incoming_location'),
    path('spareparts_incoming_list', pm.views.spareparts_incoming_list, name='spareparts_incoming_list'),
    path('spareparts_cert_main', pm.views.spareparts_cert_main, name='spareparts_cert_main'),
    path('spareparts_cert_upload', pm.views.spareparts_cert_upload, name='spareparts_cert_upload'),
    path('partslist_pm_main', pm.views.partslist_pm_main, name='partslist_pm_main'),
    path('partslist_pm_controlno', pm.views.partslist_pm_controlno, name='partslist_pm_controlno'),
    path('partslist_pm_new', pm.views.partslist_pm_new, name='partslist_pm_new'),
    path('partslist_pm_maint_item', pm.views.partslist_pm_maint_item, name='partslist_pm_maint_item'),
    path('partslist_pm_maint_submit', pm.views.partslist_pm_maint_submit, name='partslist_pm_maint_submit'),
    path('partslist_pm_view', pm.views.partslist_pm_view, name='partslist_pm_view'),
    path('partslist_pm_delete', pm.views.partslist_pm_delete, name='partslist_pm_delete'),
    path('partslist_pm_cal', pm.views.partslist_pm_cal, name='partslist_pm_cal'),
    path('spareparts_short_main', pm.views.spareparts_short_main, name='spareparts_short_main'),
    path('spareparts_short_request', pm.views.spareparts_short_request, name='spareparts_short_request'),
    path('spareparts_short_submit', pm.views.spareparts_short_submit, name='spareparts_short_submit'),

##########################################################################################################################################
##########################################################################################################################################

####PM Master List####
    path('pmmasterlist_main', pm.views.pmmasterlist_main, name='pmmasterlist_main'),

####Information####
    path('equipmentlist_main', pm.views.equipmentlist_main, name='equipmentlist_main'),
    path('equipmentlist_new', pm.views.equipmentlist_new, name='equipmentlist_new'),
    path('equipmentlist_room', pm.views.equipmentlist_room, name='equipmentlist_room'),
    path('equipmentlist_new_submit', pm.views.equipmentlist_new_submit, name='equipmentlist_new_submit'),
    path('equipmentlist_change', pm.views.equipmentlist_change, name='equipmentlist_change'),
    path('equipmentlist_change_room', pm.views.equipmentlist_change_room, name='equipmentlist_change_room'),
    path('equipmentlist_change_submit', pm.views.equipmentlist_change_submit, name='equipmentlist_change_submit'),
    path('equipmentlist_delete', pm.views.equipmentlist_delete, name='equipmentlist_delete'),
    path('roomlist_main', pm.views.roomlist_main, name='roomlist_main'),
    path('roomlist_new', pm.views.roomlist_new, name='roomlist_new'),
    path('roomlist_new_submit', pm.views.roomlist_new_submit, name='roomlist_new_submit'),
    path('roomlist_change', pm.views.roomlist_change, name='roomlist_change'),
    path('roomlist_delete', pm.views.roomlist_delete, name='roomlist_delete'),

    ####테스트용####
    path('temp', pm.views.temp, name='temp'),

##########################################################################################################################################
##########################################################################################################################################
####admin####
    path('user_info', pm.views.user_info, name='user_info'),
    path('user_info_new', pm.views.user_info_new, name='user_info_new'),
    path('user_info_new_submit', pm.views.user_info_new_submit, name='user_info_new_submit'),
    path('approval_info', pm.views.approval_info, name='approval_info'),
    path('approval_info_new', pm.views.approval_info_new, name='approval_info_new'),
    path('approval_info_new_submit', pm.views.approval_info_new_submit, name='approval_info_new_submit'),
    path('approval_info_change', pm.views.approval_info_change, name='approval_info_change'),
    path('approval_info_change_submit', pm.views.approval_info_change_submit, name='approval_info_change_submit'),
    path('approval_info_delete', pm.views.approval_info_delete, name='approval_info_delete'),
    path('user_info_change', pm.views.user_info_change, name='user_info_change'),
    path('user_info_change_submit', pm.views.user_info_change_submit, name='user_info_change_submit'),
    path('user_info_change_delete', pm.views.user_info_change_delete, name='user_info_change_delete'),
    path('pmrefer_main', pm.views.pmrefer_main, name='pmrefer_main'),
    path('pmrefer_new', pm.views.pmrefer_new, name='pmrefer_new'),
    path('pmrefer_new_submit', pm.views.pmrefer_new_submit, name='pmrefer_new_submit'),
    #path('pmrefer_change', pm.views.pmrefer_change, name='pmrefer_change'),
    path('pmrefer_delete', pm.views.pmrefer_delete, name='pmrefer_delete'),

##########################################################################################################################################
##########################################################################################################################################
####기타####
    path('report_main', pm.views.report_main, name='report_main'),
    path('report_table_bm', pm.views.report_table_bm, name='report_table_bm'),
    path('report_table_sp', pm.views.report_table_sp, name='report_table_sp'),
    path('history_of_equip_main', pm.views.history_of_equip_main, name='history_of_equip_main'),
    path('history_of_equip_upload', pm.views.history_of_equip_upload, name='history_of_equip_upload'),
    path('history_of_equip_reset', pm.views.history_of_equip_reset, name='history_of_equip_reset'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)