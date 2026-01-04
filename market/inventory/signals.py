from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

from .models import Cart

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Cart)
def send_cart_notification_email(sender, instance, created, **kwargs):
    if created and instance.status == Cart.Status.IN_CART:
        try:
            user = instance.user
            product = instance.product
            
            if not user.email:
                logger.warning(f"Користувач {user.username} не має email адреси")
                return
            
            context = {
                'user_first_name': instance.user.name or instance.user.username or instance.user.email,
                'product_name': product.name,
                'product_price': product.unit_price,
                'product_unit': product.get_unit_display(),
                'quantity': instance.quantity,
                'total_price': product.unit_price * instance.quantity,
                'cart_url': f"{settings.SITE_URL}/inventory/cart/",
            }
            
            html_message = render_to_string('emails/cart_notification.html', context)
            send_mail(
                subject="🛒 Товар додано в кошик",
                message=f"Товар {product.name} додано в кошик", 
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
            
            logger.info(f"Email відправлено користувачу {user.email} про додавання {product.name} в кошик")
            
        except Exception as e:
            logger.error(f"Помилка при відправці email: {str(e)}", exc_info=True)


def ready():
    pass
