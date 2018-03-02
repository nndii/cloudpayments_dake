import typing


class Transaction(typing.NamedTuple):
    transaction_id: int
    amount: float
    datetime: str
    name: str
    ip_address: str
    card_cryptogram_packet: str
    card_first_six: str = '123456'
    card_last_four: str = '1234'
    card_type: str = 'VISA'
    card_exp_date: str = '15/24'
    test_mode: int = 1
    currency: str = 'RUB'
    status: str = 'Created'

    async def jsonify(self):
        json_obj = dict()
        for field in self._fields:
            value = getattr(self, field)
            attr = ''.join((x.capitalize() for x in field.split('_')))
            json_obj[attr] = value
        return json_obj

    async def replace(self, **kwargs):
        return self._replace(**kwargs)


if __name__ == '__main__':
    omg = Transaction(123, 123.1, 'OMG')
    omg.jsonify()
