from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('itms.views',
    # Examples:
    # url(r'^$', 'testproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'^$',                                              'login_success'),
    url(r'^loginsuccess/$',                                 'login_success'),
    url(r'^upload_page/$',                                  'upload_page'),
    url(r'^(?P<cpe_id>\d+)/thecpeinfo/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',        'get_cpe_info'),
    url(r'^(?P<cpe_id>\d+)/cpetoworklist/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',     'cpe_to_worklist'),
    url(r'^(?P<cpe_id>\d+)/status/$',                       'check_cpe_status'),
    url(r'^(?P<cpe_id>\d+)/get_relative_list/$',            'get_relative_list'),

    url(r'^manageserver/$',                                                'go_to_server_manage'),
    url(r'^startorstopserver/(?P<server_name>.+)/$',                       'start_or_stop_server'),
    url(r'^upgradeserver/(?P<server_version>.+)/(?P<server_name>.+)/$',    'upgrade_server'),

    url(r'^inquirycpe/$',                                   'inquiry_cpe'),
    url(r'^(?P<page_num>[A-Za-z0-9\*\-\_]+)/inquiryresult/$',   'inquiry_result'),

    url(r'^inquirytasklist/(?P<revert>.+)/$',                               'inquiry_tasklist'),
    url(r'^(?P<cpe_id>\d+)/(?P<page_num>[0-9\*]+)/inquirytasklistresult/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',   'inquiry_tasklist_result'),

    url(r'^soaplog/$',                                       'soap_log'),
    url(r'^(?P<cpe_id>\d+)/(?P<page_num>[0-9\*]+)/soaplogresult/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',   'soap_log_result'),

    url(r'^inquiryworklist/$',                              'inquiry_worklist'),
    url(r'^(?P<page_num>[A-Za-z0-9\*\-\_]+)/inquiryworklistresult/(?P<revert>.+)/$', 'inquiry_worklist_result'),

    url(r'^(?P<worklist_id>\d+)/theworklistinfo/(?P<revert>.+)/$',         'get_worklist_info'),
    url(r'^(?P<worklist_id>\d+)/theworklistlog/(?P<revert>.+)/$',          'show_worklist_log'),
    url(r'^(?P<worklist_id>\d+)/binddevice/(?P<revert>.+)/$',              'bind_device'),
    url(r'^(?P<worklist_id>\d+)/exec_worklist/(?P<revert>.+)/$',           'exec_worklist'),

    url(r'^(?P<cpe_id>\d+)/enterthecpe/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                  'enter_the_cpe'),
    url(r'(?P<cpe_id>\d+)/get_rpc_methods/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',               'get_rpc_methods'),
    url(r'(?P<cpe_id>\d+)/set_parameter_values/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',          'set_parameter_values'),
    url(r'(?P<cpe_id>\d+)/get_parameter_values/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',          'get_parameter_values'),
    url(r'(?P<cpe_id>\d+)/get_parameter_names/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',           'get_parameter_names'),
    url(r'(?P<cpe_id>\d+)/set_parameter_attributes/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',      'set_parameter_attributes'),
    url(r'(?P<cpe_id>\d+)/get_parameter_attributes/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',      'get_parameter_attributes'),
    url(r'(?P<cpe_id>\d+)/add_object/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                    'add_object'),
    url(r'(?P<cpe_id>\d+)/delete_object/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                 'delete_object'),
    url(r'(?P<cpe_id>\d+)/reboot/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                        'reboot'),
    url(r'(?P<cpe_id>\d+)/download/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                      'download'),
    url(r'(?P<cpe_id>\d+)/upload/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                        'upload'),
    url(r'(?P<cpe_id>\d+)/factory_reset/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                 'factory_reset'),
    url(r'(?P<cpe_id>\d+)/schedule_inform/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',               'schedule_inform'),
    url(r'(?P<cpe_id>\d+)/get_queued_transfers/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',          'get_queued_transfers'),
    url(r'(?P<cpe_id>\d+)/set_vouchers/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                  'set_vouchers'),
    url(r'(?P<cpe_id>\d+)/get_options/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',                   'get_options'),
    url(r'(?P<cpe_id>\d+)/get_all_queued_transfers/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',      'get_all_queued_transfers'),
    url(r'(?P<cpe_id>\d+)/schedule_download/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',             'schedule_download'),
    url(r'(?P<cpe_id>\d+)/cancel_transfer/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',               'cancel_transfer'),
    url(r'(?P<cpe_id>\d+)/change_du_state/(?P<revert>.+)/(?P<worklist_id>[A-Za-z0-9]+)/$',               'change_du_state'),

    url(r'(?P<cpe_id>\d+)/ajax_rpc_request/$',                             'ajax_rpc_request'),
    url(r'^add_worklist/(?P<revert>.+)/(?P<cpe_id>[A-Za-z0-9]+)/$',        'add_worklist'),
    #url(r'^worklist_doc/(?P<revert>.+)/(?P<cpe_id>[A-Za-z0-9]+)/$',        'worklist_doc'),
    #url(r'^get_worklist_doc/$',                                            'get_worklist_doc_bs'),
    url(r'^init_worklist/(.+)/$',                                          'init_worklist'),
    url(r'^get_worklist_template/$',                                       'get_worklist_template_data'),
    url(r'^(?P<cpe_id>\d+)/ajax_static_rpc_request/(.+)/$',                'ajax_static_rpc_request'),
)
