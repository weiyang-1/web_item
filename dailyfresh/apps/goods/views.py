from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from goods.models import GoodsType,IndexGoodsBanner,GoodsSKU,IndexTypeGoodsBanner,IndexPromotionBanner
from order.models import OrderGoods
from django_redis import get_redis_connection
from django.core.cache import cache

# Create your views here.


# http://127.0.0.1:8000
# /
# def index(request):
#     """首页"""
#
#     return render(request, 'index.html')

class IndexView(View):
    """首页"""
    def get(self,request):
        """显示"""
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')

        if context is None:
            # 获取商品的分类信息
            return render(request,'index.html',context)
        # print('设置首页缓存')

        # 获取商品分类信息
        types = GoodsType.objects.all()
        # print(len(types))

        # 获取首页的轮播商品的信息
        index_banner = IndexGoodsBanner.objects.all()
        # print(len(index_banner))
        # 获取促销活动信息
        promotion_banner = IndexPromotionBanner.objects.all()
        # print(promotion_banner[0].image.url)

        # 获取首页分类商品的展示信息
        for type in types:

            title_banner = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0)
            image_banner = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1)

            # 给对象设置属性
            type.title_banner = title_banner
            type.image_banner = image_banner


            # print('这是title%d'% len(type.title_banner))

        # print(len(type.title_banner))

        # 组织一下上下文
        context = {
            'types':types,
            'index_banner':index_banner,
            'promotion_banner':promotion_banner,
            'cart_count':0
        }

            # 设置首页缓存
            # from django.core.cache import cache
            # cache.set('缓存名称'，缓存数据，缓存有效时长）pickle

        cache.set('index_page_data',context,3600)

        # 判断用户是否一登录
        cart_count = 0
        if request.user.is_authenticated():
            # 获取redis链接
            conn = get_redis_connection('default')
            print(request.user.id)
            # 连接key
            cart_key = 'cart_%s' % request.user.id

            # 获取用户购物车中商品的条目数
            # hlen(key)-> 返回属性的数目
            cart_count = conn.hlen(cart_key)
            print(cart_count)

        # 组织末班上下文
        # context.update(cart_count = cart_count)
            context['cart_count']=cart_count
        return render(request,'index.html',context)


# goods/1111
class DetailView(View):
    """商品详情页面试图"""
    def get(self,request,sku_id):
        """显示"""
        # 获取商品的详细信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在，跳转到首页
            return redirect(reverse('goods:index'))

        # 获取商品分类的信息
        types = GoodsType.objects.all()
        # for type in types:
        #     print(type.name)

        # 获取商品的评论信息
        order_skus = OrderGoods.objects.filter(sku=sku).exclude(comment='').order_by('-update_time')

        # 获取和商品同一个SPU的其他规格的商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)

        # 获取和商品同一种类的两个新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 如果用户登陆，获取用户购物车中商品的天屏幕数
        cart_count = 0
        if request.user.is_authenticated():
            # 获取redis链接
            conn = get_redis_connection('default')

            # 拼接key
            cart_key = 'cart_%s' % request.user.id
            print(cart_key) # cart_3

            # 获取用户购物车中商品数量
            cart_count = conn.hlen(cart_key)
            print(cart_count)
            # 添加浏览记录
            # 拼接购物记录的用户信息 ‘history_oo1'
            history_key = 'history_%s' % request.user.id

            # 先尝试从redis对应的列表中移除sku_id
            # lrem(key,count,value)
            conn.lrem(history_key,0,sku_id)

            # 把sku_id 添加到redis对应的列表左侧
            conn.lpush(history_key,sku_id)

            # 只保留用户最新浏览的5个商品id  ltrim(self, name, start, end) 删除其他元素 只保留开头和结尾
            conn.ltrim(history_key,0,4)

            # 组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'order_skus': order_skus,
            'same_spu_skus': same_spu_skus,
            'new_skus': new_skus,
            'cart_count': cart_count
        }

        return render(request,'detail.html',context)


class ListView(View):
    """列表"""
    def get(self,request,type_id,page):
        """显示"""
        # 获取type_id对应的商品种类信息
        try:
            type = GoodsType.objects.get(id = type_id)
        except GoodsType.DoesNotExist:
            return redirect(redirect(reverse('goods:index')))

        # 所有商品展示
        types = GoodsType.objects.all()

        # 获取排序顺序
        # sort=price: 按照商品的价格(price)从低到高排序
        # sort=hot: 按照商品的人气(sales)从高到低排序
        # sort=default: 按照默认排序方式(id)从高到低排序
        sort = request.GET.get('sort')

        # 获取type种类的商品信息
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        from django.core.paginator import Paginator
        paginator = Paginator(skus,2)

        # 处理页码
        page = int(page)

        if page > paginator.num_pages:
            # 默认获取第一页的内容
            page = 1

        # 获取第page页的内容，返回Page类的实例对象
        skus_page = paginator.page(page)

        # 页码处理
        # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
        # 1) 分页页码小于5页，显示全部页码
        # 2）当前页属于1-3页，显示1-5页
        # 3) 当前页属于后3页，显示后5页
        # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 1-num_pages
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            # num_pages-4, num_pages
            pages = range(num_pages - 4, num_pages + 1)
        else:
            # page-2, page+2
            pages = range(page - 2, page + 3)

        # 获取type种类的2个新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 如果用户登陆，获取用户购物车中商品的条目书
        cart_count = 0
        if request.user.is_authenticated():
            # 获取redis链接
            conn = get_redis_connection('default')

            # 拼接key
            cart_key = 'cart_%s' % request.user.id

            # 获取用户购物车中商品的条目书
            # hlen（key)-> 返回属性的数目
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文数据
        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }

        return render(request,'list.html',context)


