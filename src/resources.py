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
    invoice_id: typing.Union[None, str] = None
    account_id: typing.Union[None, str] = None
    subscription_id: typing.Union[None, str] = None
    email: typing.Union[None, str] = None
    ip_country: typing.Union[None, str] = None
    ip_city: typing.Union[None, str] = None
    ip_region: typing.Union[None, str] = None
    ip_district: typing.Union[None, str] = None
    issuer: typing.Union[None, str] = None
    issuer_bank_country: typing.Union[None, str] = None
    description: typing.Union[None, str] = None

    async def jsonify(self, except_fields=None):
        if except_fields is None:
            except_fields = []

        json_obj = dict()
        for field in self._fields:
            value = getattr(self, field)
            attr = ''.join((x.capitalize() for x in field.split('_')))
            if value is not None and field not in except_fields:
                json_obj[attr] = value
        return json_obj

    async def replace(self, **kwargs):
        return self._replace(**kwargs)


if __name__ == '__main__':
    omg = Transaction(123, 123.1, 'OMG')
    omg.jsonify()
