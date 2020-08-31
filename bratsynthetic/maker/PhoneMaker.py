from .Maker import Maker

import random
import re

_area_codes = [
'201',
'202',
'203',
'204',
'205',
'206',
'207',
'208',
'209',
'210',
'211',
'212',
'213',
'214',
'215',
'216',
'217',
'218',
'219',
'220',
'223',
'224',
'225',
'226',
'228',
'229',
'231',
'234',
'236',
'239',
'240',
'242',
'246',
'248',
'250',
'251',
'252',
'253',
'254',
'256',
'260',
'262',
'264',
'267',
'268',
'269',
'270',
'272',
'276',
'278',
'281',
'283',
'284',
'289',
'301',
'302',
'303',
'304',
'305',
'306',
'307',
'308',
'309',
'310',
'311',
'312',
'313',
'314',
'315',
'316',
'317',
'318',
'319',
'320',
'321',
'323',
'325',
'330',
'331',
'332',
'334',
'336',
'337',
'339',
'340',
'341',
'343',
'345',
'346',
'347',
'351',
'352',
'360',
'361',
'365',
'369',
'380',
'385',
'386',
'401',
'402',
'403',
'404',
'405',
'406',
'407',
'408',
'409',
'410',
'411',
'412',
'413',
'414',
'415',
'416',
'417',
'418',
'419',
'423',
'424',
'425',
'430',
'431',
'432',
'434',
'435',
'437',
'438',
'440',
'441',
'442',
'443',
'450',
'456',
'458',
'464',
'469',
'470',
'473',
'475',
'478',
'479',
'480',
'481',
'484',
'500',
'501',
'502',
'503',
'504',
'505',
'506',
'507',
'508',
'509',
'510',
'511',
'512',
'513',
'514',
'515',
'516',
'517',
'518',
'519',
'520',
'530',
'539',
'540',
'541',
'548',
'551',
'555',
'557',
'559',
'561',
'562',
'563',
'564',
'567',
'570',
'571',
'573',
'574',
'575',
'579',
'580',
'581',
'585',
'586',
'587',
'600',
'601',
'602',
'603',
'604',
'605',
'606',
'607',
'608',
'609',
'610',
'611',
'612',
'613',
'614',
'615',
'616',
'617',
'618',
'619',
'620',
'623',
'626',
'627',
'628',
'629',
'630',
'631',
'636',
'639',
'641',
'646',
'647',
'649',
'650',
'651',
'657',
'660',
'661',
'662',
'664',
'667',
'669',
'670',
'671',
'678',
'679',
'681',
'682',
'684',
'689',
'700',
'701',
'702',
'703',
'704',
'705',
'706',
'707',
'708',
'709',
'710',
'712',
'713',
'714',
'715',
'716',
'717',
'718',
'719',
'720',
'721',
'724',
'725',
'727',
'731',
'732',
'734',
'737',
'740',
'743',
'747',
'754',
'757',
'758',
'760',
'762',
'763',
'764',
'765',
'767',
'769',
'770',
'772',
'773',
'774',
'775',
'778',
'779',
'780',
'781',
'782',
'784',
'785',
'786',
'787',
'800',
'801',
'802',
'803',
'804',
'805',
'806',
'807',
'808',
'809',
'810',
'811',
'812',
'813',
'814',
'815',
'816',
'817',
'818',
'819',
'822',
'825',
'828',
'829',
'830',
'831',
'832',
'833',
'835',
'843',
'844',
'845',
'847',
'848',
'849',
'850',
'855',
'856',
'857',
'858',
'859',
'860',
'862',
'863',
'864',
'865',
'866',
'867',
'868',
'869',
'870',
'872',
'873',
'876',
'877',
'878',
'880',
'881',
'882',
'888',
'898',
'900',
'901',
'902',
'903',
'904',
'905',
'906',
'907',
'908',
'909',
'910',
'911',
'912',
'913',
'914',
'915',
'916',
'917',
'918',
'919',
'920',
'925',
'927',
'928',
'929',
'931',
'935',
'936',
'937',
'939',
'940',
'941',
'947',
'949',
'951',
'952',
'954',
'956',
'957',
'959',
'970',
'971',
'972',
'973',
'975',
'976',
'978',
'979',
'980',
'984',
'985',
'989'
]




class PhoneMaker(Maker):

    def make_area_code(self) -> str:
        return random.choice(_area_codes)

    def make_exchange_code(self) -> str:
        return str(random.randint(2, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))

    def make_subscriber_number(self) -> str:
        return str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))

    def make_phone_number(self, template="(%a) %e-%s") -> str:
        phone = template

        phone = phone.replace('%a', random.choice(_area_codes))
        phone = phone.replace('%e', self.make_matching_alphanumeric('012'))
        phone = phone.replace('%s', self.make_matching_alphanumeric('0123'))
        phone = phone.replace('%d', self.make_matching_alphanumeric('0'))

        return phone

    def make_phone_regex(self, template) -> str:
        """
        Creates a regular expression given a template of a phone number.
        (%a) %e-%s -> \(\d{3}\) \d{3}-\d{4}

        :param template: %a -> area-code, %e -> exchange code %s -> subscriber number, %d -> digit
        :return: regex expression to match
        """

        escape_chars = ['\\', '^', '$', '.', '|', '*', '+', '(', ')', '[', ']', '{', '}', '?']
        for escape_char in escape_chars:
            template = template.replace(escape_char, '\\' + escape_char)
        regex = template

        regex = regex.replace('%a', r'\d{3}') # Don't be strict
        regex = regex.replace('%e', r'\d{3}')
        regex = regex.replace('%s', r'\d{4}')
        regex = regex.replace('%d', r'\d')
        return regex

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        patterns = [
            '(%a) %e-%s',   # (205) 555-3384
            '(%a)%e-%s',    # (783)508-2821
            '%a.%e.%s',     # 895.376.3157
            '%a-%e-%s',     # 077-765-3083
            '%a %e-%s',     # 516 532-0945
            '%a %e %s',     # 942 077 9578
            '%e-%s',        # 310-7911
            '%d-%s',        # 6-6804
            '%e-%s-%a',      # 851-9764-289
        ]

        matched = False
        for pattern in patterns:
            if re.fullmatch(self.make_phone_regex(pattern), input):
                output = self.make_phone_number(pattern)
                matched = True
                break

        # 82910
        if matched:
            pass
        elif re.fullmatch(r'\d{,10}', input):
            output = self.make_matching_alphanumeric(input)


        # print(f'PhoneMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)

        return output
