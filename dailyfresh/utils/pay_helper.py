from alipay import AliPay
from django.conf import settings



alipay = AliPay(
    appid=settings.ALIPAY_APP_ID,  # 应用APPID
    app_notify_url=settings.ALIPAY_APP_NOTIFY_URL,  # 默认回调url
    app_private_key_path=settings.APP_PRIVATE_KEY_PATH,  # 应用私钥文件路径
    # 支付宝的公钥文件，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
    sign_type="RSA2",  # RSA 或者 RSA2
    debug=settings.ALIPAY_DEBUG  # 默认False，False代表线上环境，True代表沙箱环境
)