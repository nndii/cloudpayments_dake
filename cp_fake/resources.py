import datetime
import typing


class Transaction(typing.NamedTuple):
    transaction_id: int
    amount: float
    datetime: datetime.datetime
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
    data: dict = None

    def jsonify(
            self,
            except_fields: typing.Sequence=None,
            add_fields: typing.Mapping=None) -> dict:
        """transaction obj -> dictionary with CamelCase"""
        if except_fields is None:
            except_fields = []

        json_obj = dict()
        for field in self._fields:
            value = getattr(self, field)
            # snake_case -> CamelCase
            attr = ''.join((x.capitalize() for x in field.split('_')))
            if value is not None and field not in except_fields:
                if attr == 'Datetime':
                    json_obj[attr] = value.strftime('%Y-%m-%d %X')
                else:
                    json_obj[attr] = value

        if add_fields is None:
            add_fields = {}

        for field in add_fields:
            json_obj[field] = add_fields[field]

        return json_obj

    def replace(self, **kwargs):
        return self._replace(**kwargs)
