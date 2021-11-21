import json
import logging
import ast

logger = logging.getLogger("filter")

_filter_map = {
    "Ações": "stocks",
    "Fundos Imobiliários": "real_state",
    "COE": "coe",
    "Fundos de Investimento": "funds",
    "Previdência Privada": "pension_funds"
}


class Filter:
    def __init__(self, emails, redis, messages):
        self.redis = redis
        self.emails = emails
        self.messages = messages

    @property
    async def filter_products(self):
        results = list()
        emails = list()
        cur = b'0'
        if self.emails == ["all"]:
            while cur:
                cur, keys = await self.redis.scan(cur, match='user:*')
                if keys:
                    emails.append(keys[0].decode().split(":")[-1])
        else:
            emails = self.emails
        logger.info(emails)

        for email in emails:
            user_filter = json.loads(await self.redis.get(f"user:{email}"))
            products = ast.literal_eval(self.messages[0]["payload"].get("products", []))
            for msg in products:
                _filter_type = _filter_map[msg["category"]]
                is_desired = user_filter.get(_filter_type)
                if not is_desired:
                    continue
                result = self.filter_data(msg, user_filter[_filter_type])
                if result:
                    result["email"] = email
                    results.append(result)
        return results

    @staticmethod
    def filter_data(message, conditions):
        is_valid = True
        for key, value in conditions.items():
            if key in message:
                if isinstance(value, list):
                    if message[key] not in value:
                        is_valid = False
                        break
                elif "min" in key:
                    if float(message[key]) < value:
                        is_valid = False
                        break
                elif "max" in key:
                    if float(message[key]) > value:
                        is_valid = False
                        break
                else:
                    if message[key] != value:
                        is_valid = False
                        break

        return message if is_valid else None