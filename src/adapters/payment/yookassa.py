from yookassa import Configuration, Payment

from src.config.reader import Config

def create_payment(post_id: int, config: Config) -> tuple[str, str]:
    Configuration.account_id = config.payments.shop_id
    Configuration.secret_key = config.payments.secret_key

    payment = Payment.create({
        "amount": {
            "value": config.payments.post_price,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": config.bot.bot_url
        },
        "capture": True,
        "description": f"Оплата поста #{post_id}",
        "metadata": {"post_id": str(post_id)}
    })

    return payment.confirmation.confirmation_url, payment.id
