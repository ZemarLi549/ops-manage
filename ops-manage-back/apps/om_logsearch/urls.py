from django.urls import path
from .views import *
from .gateallviews import *
from .appallviews import *


urlpatterns = [
    path('source', DataSourceView.as_view()),
    path('gateconfig', GateConfigView.as_view()),
    path('appconfig', AppConfigView.as_view()),
    path('component', ComponentIndexView.as_view()),
    path('datasearch', DataCommonSearchView.as_view()),
    path('applist', AppListView.as_view()),
    path('gatelist', GateListView.as_view()),
    path('gatepass', GatePassView.as_view()),
    path('apppass', AppPassView.as_view()),
    path('gatefilter', GateFilterView.as_view()),
    path('appfilter', AppFilterView.as_view()),
    path('hosttable', AllHostTableView.as_view()),
    path('statusline', StatusLineView.as_view()),
    path('reqallline', ReqAllLineView.as_view()),
    path('netallline', NetAllLineView.as_view()),
    path('methodstline', MethodStatusLineView.as_view()),
    path('resppie', RespPieView.as_view()),
    path('commonpie', CommonPieView.as_view()),
    path('fivenine', FiveNineRespView.as_view()),
    path('clientpie', ClientPieView.as_view()),
    path('gatequery', GateQueryView.as_view()),
    path('appquery', AppQueryView.as_view()),
    path('apphisgram', HistoryGramAggView.as_view()),
    path('applocate', AppLocateView.as_view()),
]
