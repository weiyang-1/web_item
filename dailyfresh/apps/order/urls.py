from django.conf.urls import url
from order.views import OrderPlaceView,OrderCommitView,OrderCheckView,OrderPayView,CommentView
urlpatterns = [
    url('^place$',OrderPlaceView.as_view(),name='place'), # 订单页面显示
    url('^commit$',OrderCommitView.as_view(),name='commit'), # 订单页面显示
    url('^pay$',OrderPayView.as_view(),name='pay'), # 支付订单
    url('^check$',OrderCheckView.as_view(),name='check'), # 支付清单
    url('^comment/(?P<order_id>.*)$',CommentView.as_view(),name='comment'), # 评论区
]
