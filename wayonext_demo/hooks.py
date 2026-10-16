"""Builds the WayoNext Pharmaceuticals demo on a fresh Odoo 19 database.

Business model represented:
    WayoNext owns the brands (Wayoprime and Wayomax divisions). Finished goods are
    made by third-party (loan licence) manufacturers, received batch-wise with expiry
    into the Ambarnath warehouse, and sold to stockists under the WayoNext brand.

Everything is created relative to the install date so the demo always looks current.
"""
import logging
import random
from datetime import datetime, time, timedelta

from odoo import Command, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GSTIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def make_gstin(state_code, pan):
    """Return a format-valid GSTIN (with correct check digit) for demo use."""
    body = f"{state_code}{pan}1Z"
    total = 0
    for i, ch in enumerate(body):
        val = GSTIN_CHARS.index(ch) * (2 if i % 2 else 1)
        total += val // 36 + val % 36
    return body + GSTIN_CHARS[(36 - total % 36) % 36]


# ---------------------------------------------------------------------------
# Master data
# ---------------------------------------------------------------------------

VENDORS = {
    'himgiri': {
        'name': 'Himgiri Formulations Pvt. Ltd.',
        'street': 'Plot 14, EPIP Phase I, Jharmajri',
        'city': 'Baddi', 'zip': '173205', 'state': 'HP', 'gst_state': '02',
        'pan': 'AADCH4417K', 'dl': 'MNB/24/1187 (Form 25 and 28)',
        'phone': '+91 1795 244 118', 'email': 'orders@himgiri-formulations.demo',
        'note': 'Loan licence manufacturer for tablets and capsules (Rx range).',
    },
    'devbhoomi': {
        'name': 'Devbhoomi Nutraceuticals LLP',
        'street': 'Plot 38, Sector 6A, SIDCUL',
        'city': 'Haridwar', 'zip': '249403', 'state': 'UT', 'gst_state': '05',
        'pan': 'AAQFD7720M', 'fssai': '10024051000398',
        'phone': '+91 1334 239 410', 'email': 'sales@devbhoomi-nutra.demo',
        'note': 'Third-party manufacturer for nutraceutical tablets and softgels.',
    },
    'sahyadri': {
        'name': 'Sahyadri Wellness Products Pvt. Ltd.',
        'street': 'Plot E-52, MIDC Tarapur',
        'city': 'Boisar', 'zip': '401506', 'state': 'MH', 'gst_state': '27',
        'pan': 'AAJCS5583P', 'fssai': '11524999000713',
        'phone': '+91 2525 272 064', 'email': 'dispatch@sahyadri-wellness.demo',
        'note': 'Powders, sachets and probiotic capsules. Intra-state supplier (CGST + SGST).',
    },
    'coastline': {
        'name': 'Coastline Parenterals Pvt. Ltd.',
        'street': 'Survey No. 112, Kachigam Industrial Area',
        'city': 'Daman', 'zip': '396210', 'state': 'DD', 'gst_state': '26',
        'pan': 'AAHCC2290D', 'dl': 'DD/LVP/0419 (Form 28)',
        'phone': '+91 260 224 1180', 'email': 'orders@coastline-parenterals.demo',
        'note': 'Large volume parenterals (IV infusions).',
    },
}

# (code, name, division, form, pack, schedule, hsn, mrp, vendor, tags, composition, indication)
CATALOGUE = [
    # Wayoprime division
    ('WP-OVABD', 'OVABD Sachet', 'prime', 'sachet', '10 sachets per box', 'nutra', '21069099', 690, 'sahyadri',
     ['Gynaecology', 'Fertility', 'PCOS'],
     'Myo-inositol : D-chiro-inositol, Berberine, Fenugreek, Grape Seed Extract, NAC, Chromium, Chasteberry, L-Methylfolate, Vitamin D3',
     'PCOS / PCOD, oligo / amenorrhoea, anovulation, acne and hirsutism'),
    ('WP-DRMF', 'Dreamfert F Tablet', 'prime', 'tablet', '10 tablets per strip', 'nutra', '21069099', 650, 'devbhoomi',
     ['Fertility'],
     'Green Tea, Chasteberry, Lycopene, Berberine, Fenugreek, Melatonin, Reduced CoQ10, Astaxanthin, L-Arginine, Benfotiamine, L-Methylfolate, Zinc, Selenium, Magnesium',
     'Unexplained infertility, age-related decline in fertility, patients undergoing IUI / IVF'),
    ('WP-W9NVP', 'Wayo 9 NVP Tablet', 'prime', 'tablet', '10 tablets per strip', 'h', '30049099', 280, 'himgiri',
     ['Obstetrics'],
     'Doxylamine Succinate, Pyridoxal-5-Phosphate, L-Methylfolate Calcium, Methylcobalamin',
     'Nausea and vomiting during pregnancy'),
    ('WP-WCAL', 'Wayocal Tablet', 'prime', 'tablet', '15 tablets per strip', 'nutra', '21069099', 260, 'devbhoomi',
     ['Obstetrics', 'Bone Health'],
     'Calcium Citrate Malate, Vitamin D3, Magnesium, Zinc',
     'Pregnancy, lactation, pre, peri and post-menopause'),
    ('WP-WCALXT', 'Wayocal XT Tablet', 'prime', 'tablet', '15 tablets per strip', 'nutra', '21069099', 295, 'devbhoomi',
     ['Obstetrics', 'Bone Health'],
     'Calcium Citrate Malate, Vitamin D3, L-Methylfolate, Methylcobalamin, P5P',
     'Preeclampsia, IUGR, prevention of preterm birth'),
    ('WP-AQPRO', 'AQPRO Protein Powder', 'prime', 'powder', '200 g jar', 'nutra', '21069099', 545, 'sahyadri',
     ['Obstetrics', 'Nutrition'],
     'Protein Hydrolysate, Iron, DHA, Calcium, Folic Acid, Zinc, Selenium, Magnesium',
     'Pregnancy and lactation, illness, fatigue, weakness, menopause'),
    ('WP-WCLAV', 'Wayoclav 625 Tablet', 'prime', 'tablet', '6 tablets per strip', 'h1', '30042019', 220, 'himgiri',
     ['Anti-infective'],
     'Amoxicillin 500 mg, Clavulanic Acid 125 mg, Lactic Acid Bacillus 60 million spores',
     'Bacterial vaginitis, gonorrhoea, urogenital infections, post-operative care, skin and soft tissue infections'),
    ('WP-WBACT', 'Wayobact Capsule', 'prime', 'capsule', '10 capsules per strip', 'nutra', '21069099', 190, 'sahyadri',
     ['Probiotic'],
     'Saccharomyces boulardii, Lactobacillus sporogenes, Streptococcus faecalis, Clostridium butyricum, Bacillus mesentericus, FOS',
     'Bacterial and fungal vaginitis, UTIs, diarrhoea in pregnancy, IBS, antibiotic associated diarrhoea'),
    ('WP-WPAN', 'Wayopan 40 Tablet', 'prime', 'tablet', '15 tablets per strip', 'h', '30049099', 155, 'himgiri',
     ['Gastro'],
     'Pantoprazole 40 mg',
     'Hyperacidity, GERD, peptic ulcer disease'),
    ('WP-WPAND', 'Wayopan D Capsule', 'prime', 'capsule', '15 capsules per strip', 'h', '30049099', 210, 'himgiri',
     ['Gastro'],
     'Pantoprazole 40 mg, Domperidone 30 mg (SR)',
     'Hyperacidity and reflux disorder'),
    ('WP-WMINIV', 'Wayomin IV Infusion', 'prime', 'infusion', '500 ml bottle', 'h', '30049099', 1250, 'coastline',
     ['Obstetrics'],
     '18 essential and non-essential amino acids',
     'Oligohydramnios and IUGR'),
    ('WP-DHEA', 'Dheacure Capsule', 'prime', 'capsule', '10 capsules per strip', 'h', '30049099', 850, 'himgiri',
     ['Fertility'],
     'Micronised DHEA 75 mg, Melatonin 3 mg, CoQ10 200 mg, Vitamin D 2000 IU',
     'Diminished ovarian reserve and poor responders to ovulation induction'),
    # Wayomax division
    ('WM-W9', 'Wayo 9 Tablet', 'max', 'tablet', '10 tablets per strip', 'nutra', '21069099', 245, 'devbhoomi',
     ['Obstetrics'],
     'L-Methylfolate, Methylcobalamin, Pyridoxal-5-Phosphate',
     'Reduces risk of miscarriage and neural tube defects'),
    ('WM-W9D', 'Wayo 9 D Softgel', 'max', 'softgel', '10 softgels per strip', 'nutra', '21069099', 320, 'devbhoomi',
     ['Obstetrics'],
     'L-Methylfolate, Methylcobalamin, Pyridoxal-5-Phosphate, DHA, Vitamin D3',
     'Preeclampsia, preterm birth, IUGR, low birth weight; supports vision and brain development'),
    ('WM-DRMM', 'Dreamfert M Tablet', 'max', 'tablet', '10 tablets per strip', 'nutra', '21069099', 680, 'devbhoomi',
     ['Fertility', 'Andrology'],
     'Wheatgerm Oil, L-Carnitine, Pine Bark Extract, Reduced CoQ10, Lycopene, Astaxanthin, Zinc, Piperine, Selenium, L-Methylfolate',
     'Oligoasthenoteratozoospermia, idiopathic male infertility, asthenozoospermia in varicocele'),
    ('WM-WGEST', 'Wayogest 200 SR Capsule', 'max', 'softgel', '10 capsules per strip', 'h', '30043990', 450, 'himgiri',
     ['Gynaecology', 'Obstetrics'],
     'Natural Micronised Progesterone 200 mg',
     'Luteal phase support, DUB and spotting'),
    ('WM-ADNCR', 'AD-NCR 10 Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30043990', 120, 'himgiri',
     ['Gynaecology'],
     'Norethisterone Acetate 10 mg',
     'DUB, secondary amenorrhoea, menorrhagia, premenstrual symptoms, postponement of menses, endometriosis'),
    ('WM-WBIS', 'Wayobis Tablet', 'max', 'tablet', '15 tablets per strip', 'nutra', '21069099', 225, 'devbhoomi',
     ['Haematinic'],
     'Ferrous Bisglycinate, Zinc Bisglycinate, Folic Acid, Methylcobalamin',
     'Iron deficiency, iron deficiency anaemia, heavy menstrual bleeding'),
    ('WM-HERFIL', 'Herfil 25 Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30049099', 160, 'himgiri',
     ['Fertility'],
     'Sildenafil Citrate 25 mg',
     'To increase endometrial thickness and in IUGR'),
    ('WM-WD3', 'Wayo D3 60K Capsule', 'max', 'softgel', '4 capsules per strip', 'h', '30045020', 145, 'himgiri',
     ['Bone Health'],
     'Cholecalciferol 60,000 IU',
     'Infertility, pregnancy, lactation, menopause, osteopenia, osteoporosis, fracture, diabetes and CVD'),
    ('WM-WFIT', 'Wayofit Tablet', 'max', 'tablet', '15 tablets per strip', 'nutra', '21069099', 330, 'devbhoomi',
     ['Nutrition'],
     'Multivitamin, Multimineral with Grape Seed Extract',
     'Acute and chronic conditions, fatigue, weakness, low back pain, post-operative recovery'),
    ('WM-WHEAL', 'Wayoheal Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30049099', 210, 'himgiri',
     ['Orthopaedics', 'Pain'],
     'Aceclofenac, Paracetamol, Trypsin Chymotrypsin',
     'Post-operative wound, inflammation, oedema, PID'),
    ('WM-DYDRO', 'Dydroway 10 Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30043990', 690, 'himgiri',
     ['Obstetrics'],
     'Micronised Dydrogesterone 10 mg',
     'Recurrent pregnancy loss, luteal phase support in ART, threatened miscarriage, subchorionic haematoma'),
    ('WM-FIB10', 'Fibro-10 Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30043990', 450, 'himgiri',
     ['Gynaecology'],
     'Mifepristone 10 mg',
     'Uterine fibroids'),
    ('WM-FIB25', 'Fibro-25 Tablet', 'max', 'tablet', '10 tablets per strip', 'h', '30043990', 650, 'himgiri',
     ['Gynaecology'],
     'Mifepristone 25 mg',
     'Uterine fibroids'),
]

# (key, name, street, city, zip, state, gst_state, pan, credit_limit, terms, dl_valid_days, area)
STOCKISTS = [
    ('kalyan', 'Shree Siddhivinayak Medical Agencies', 'Shop 4, Gurudev Complex, Station Road, Kalyan West', 'Kalyan', '421301', 'MH', '27', 'AAPFS1043R', 800000, '30', 640, 'Thane Rural'),
    ('thane', 'Om Sai Pharma Distributors', 'Gala 11, Wagle Industrial Estate Road 16', 'Thane', '400604', 'MH', '27', 'AACFO2271L', 1200000, '30', 410, 'Thane'),
    ('dombivli', 'Navkar Pharma', '1st Floor, Manpada Road, Dombivli East', 'Dombivli', '421201', 'MH', '27', 'ABDFN5512Q', 500000, '30', 210, 'Thane Rural'),
    ('dadar', 'Mahavir Medico Agencies', '22 Gokhale Road North, Dadar West', 'Mumbai', '400028', 'MH', '27', 'AAEFM3348H', 1500000, '45', 520, 'Mumbai City'),
    ('andheri', 'Goodwill Pharma Distributors', 'Unit 108, Marol Naka, Andheri East', 'Mumbai', '400059', 'MH', '27', 'AAGFG7781B', 1500000, '45', 300, 'Mumbai Suburban'),
    ('vashi', 'Sanjeevani Medical Agencies', 'Shop 7, Sector 17, Vashi', 'Navi Mumbai', '400703', 'MH', '27', 'AAMFS6630E', 700000, '30', 180, 'Navi Mumbai'),
    ('pune', 'Pawar Pharma Distributors', '1174 Shivajinagar, FC Road', 'Pune', '411005', 'MH', '27', 'AALFP9054N', 1000000, '45', 600, 'Pune'),
    ('nashik', 'Godavari Medico', 'Near CBS, Sharanpur Road', 'Nashik', '422002', 'MH', '27', 'AABFG8812D', 600000, '30', 350, 'Nashik'),
    ('nagpur', 'Vidarbha Pharma Agencies', 'Gandhibagh, Central Avenue', 'Nagpur', '440002', 'MH', '27', 'AAKFV4471C', 800000, '45', -20, 'Vidarbha'),
    ('sambhaji', 'Deccan Medical Distributors', 'Kranti Chowk, Jalna Road', 'Chhatrapati Sambhajinagar', '431001', 'MH', '27', 'AAQFD3307F', 500000, '30', 260, 'Marathwada'),
    ('ahmedabad', 'Ambika Pharma Distributors', '305 Shivalik Plaza, Ashram Road', 'Ahmedabad', '380009', 'GJ', '24', 'AACFA6670G', 900000, '45', 480, 'Gujarat'),
    ('indore', 'Narmada Medical Agencies', '12 Siyaganj Main Road', 'Indore', '452007', 'MP', '23', 'AAHFN2234J', 600000, '45', 390, 'Madhya Pradesh'),
    ('hyderabad', 'Charminar Pharma Distributors', '4-1-12 Sultan Bazar, Koti', 'Hyderabad', '500095', 'TS', '36', 'AAEFC9918K', 900000, '45', 550, 'Telangana'),
    ('bengaluru', 'Kaveri Medical Agencies', '18 Avenue Road, Chickpet', 'Bengaluru', '560053', 'KA', '29', 'AADFK1185M', 700000, '45', 300, 'Karnataka'),
]

PEOPLE = [
    # (name, job, department, user_login or None, team)
    ('Shashikant Satyadev Singh', 'Founder and Managing Director', 'Management', None, None),
    ('Rahul Patil', 'National Sales Manager', 'Sales and Marketing', 'rahul.patil@wayonext.demo', None),
    ('Sneha Kulkarni', 'Area Sales Manager, Wayoprime', 'Sales and Marketing', 'sneha.kulkarni@wayonext.demo', 'prime'),
    ('Amit Deshmukh', 'Area Sales Manager, Wayomax', 'Sales and Marketing', 'amit.deshmukh@wayonext.demo', 'max'),
    ('Pooja Shinde', 'Medical Representative, Thane', 'Sales and Marketing', None, None),
    ('Vikas Yadav', 'Medical Representative, Mumbai', 'Sales and Marketing', None, None),
    ('Kiran More', 'Medical Representative, Pune', 'Sales and Marketing', None, None),
    ('Nilesh Jadhav', 'Warehouse In-charge', 'Warehouse and Dispatch', 'nilesh.jadhav@wayonext.demo', None),
    ('Santosh Gaikwad', 'Dispatch Executive', 'Warehouse and Dispatch', None, None),
    ('Meera Iyer', 'Accounts Manager', 'Accounts and Finance', 'meera.iyer@wayonext.demo', None),
    ('Prakash Joshi', 'Purchase Executive', 'Purchase', 'prakash.joshi@wayonext.demo', None),
    ('Dr. Anjali Rao', 'Qualified Person (Pharmacist)', 'Regulatory and Quality', None, None),
]


class WayoNextDemoBuilder:

    def __init__(self, env):
        self.env = env
        self.rng = random.Random(2026)
        self.today = fields.Date.context_today(env['res.users'])
        self.company = env.company

    # -- helpers -----------------------------------------------------------
    def _state(self, code):
        return self.env['res.country.state'].search(
            [('country_id.code', '=', 'IN'), ('code', '=', code)], limit=1)

    def _dt(self, d, hour=11):
        return datetime.combine(d, time(hour, 0))

    def _tax(self, xmlid):
        return self.env['account.chart.template'].with_company(self.company).ref(xmlid)

    # -- steps -------------------------------------------------------------
    def run(self):
        self.setup_company()
        self.setup_settings()
        self.setup_people()
        self.setup_categories()
        self.setup_partners()
        self.setup_pricelists()
        self.setup_products()
        self.setup_purchases()
        self.setup_sales()
        self.setup_returns()
        self.setup_expired_stock()
        self.setup_reordering()
        self.setup_crm()
        _logger.info("WayoNext demo data loaded")

    def setup_company(self):
        india = self.env.ref('base.in')
        mh = self._state('MH')
        company_vals = {
            'name': 'WayoNext Pharmaceuticals Pvt. Ltd.',
            'street': 'Unit No. 2, Lower Ground Floor, GNP Galaxy Phase',
            'city': 'Ambarnath',
            'zip': '421501',
            'state_id': mh.id,
            'country_id': india.id,
            'phone': '+91 93210 08495',
            'email': 'info@wayonext.com',
            'website': 'https://www.wayonext.com',
        }
        company = self.company
        has_entries = self.env['account.move'].search_count([('company_id', '=', company.id)], limit=1)
        if company.chart_template == 'in' or not has_entries:
            # Fresh production / staging database: turn the main company into WayoNext.
            company.write(company_vals)
            if company.chart_template != 'in':
                self.env['account.chart.template'].try_loading('in', company, install_demo=False)
                # account schedules its own chart guess for the end of the install; it is
                # superseded by the Indian chart loaded here.
                if hasattr(self.env.registry, '_auto_install_template'):
                    del self.env.registry._auto_install_template
        else:
            # Database already in use with another chart (e.g. an Odoo.sh development
            # build with Odoo demo data): build WayoNext as a separate company.
            company = self.env['res.company'].create(dict(company_vals, currency_id=self.env.ref('base.INR').id))
            self.env['account.chart.template'].try_loading('in', company, install_demo=False)
            users = self.env.ref('base.user_admin', raise_if_not_found=False) or self.env['res.users']
            (users | self.env.user).write({
                'company_ids': [Command.link(company.id)],
                'company_id': company.id,
            })
        self.company = company
        self.env = self.env(context=dict(self.env.context, allowed_company_ids=[company.id]))
        company.write({
            'vat': make_gstin('27', 'AACCW8841H'),
            'account_use_credit_limit': True,
        })
        company.partner_id.write({
            'wn_drug_licence': 'MH-TZ4-5520184 / 5520185 (Form 20B, 21B)',
            'wn_drug_licence_valid_till': self.today + timedelta(days=900),
            'wn_fssai': '11525014000562',
        })

    def setup_settings(self):
        user_group = self.env.ref('base.group_user')
        groups = [
            'stock.group_production_lot',
            'product.group_product_pricelist',
            'sale.group_discount_per_so_line',
            'stock.group_stock_multi_locations',
        ]
        implied = [Command.link(self.env.ref(g).id) for g in groups if self.env.ref(g, raise_if_not_found=False)]
        user_group.write({'implied_ids': implied})
        wh = self.env['stock.warehouse'].search([('company_id', '=', self.company.id)], limit=1)
        if wh:
            wh.write({'name': 'Ambarnath Warehouse'})
        else:
            wh = self.env['stock.warehouse'].create({
                'name': 'Ambarnath Warehouse', 'code': 'AMB', 'company_id': self.company.id,
                'partner_id': self.company.partner_id.id,
            })
        self.warehouse = wh
        self.term_30 = self.env.ref('account.account_payment_term_30days')
        self.term_45 = self.env.ref('account.account_payment_term_45days')

    def setup_people(self):
        Dept = self.env['hr.department']
        Users = self.env['res.users'].with_context(no_reset_password=True)
        sales_user = self.env.ref('sales_team.group_sale_salesman_all_leads')
        sales_mgr = self.env.ref('sales_team.group_sale_manager')
        stock_user = self.env.ref('stock.group_stock_user')
        acc_user = self.env.ref('account.group_account_invoice')
        purchase_user = self.env.ref('purchase.group_purchase_user')
        group_map = {
            'Sales and Marketing': [sales_user],
            'Warehouse and Dispatch': [stock_user],
            'Accounts and Finance': [acc_user],
            'Purchase': [purchase_user, stock_user],
        }
        depts = {}
        self.users = {}
        self.team_leads = {}
        for name, job, dept_name, login, team in PEOPLE:
            if dept_name not in depts:
                depts[dept_name] = Dept.create({'name': dept_name, 'company_id': self.company.id})
            user = False
            if login:
                grps = list(group_map.get(dept_name, []))
                if job == 'National Sales Manager':
                    grps.append(sales_mgr)
                user = Users.create({
                    'name': name,
                    'login': login,
                    'email': login,
                    'company_id': self.company.id,
                    'company_ids': [Command.set(self.company.ids)],
                    'group_ids': [Command.link(g.id) for g in grps] + [Command.link(self.env.ref('base.group_user').id)],
                })
                self.users[login] = user
                if team:
                    self.team_leads[team] = user
            self.env['hr.employee'].create({
                'name': name,
                'job_title': job,
                'department_id': depts[dept_name].id,
                'work_email': login or False,
                'user_id': user.id if user else False,
                'company_id': self.company.id,
            })
        self.nsm = self.users['rahul.patil@wayonext.demo']
        Team = self.env['crm.team']
        self.teams = {
            'prime': Team.create({
                'name': 'Wayoprime Division',
                'user_id': self.team_leads['prime'].id,
                'member_ids': [Command.set([self.team_leads['prime'].id])],
                'company_id': self.company.id,
            }),
            'max': Team.create({
                'name': 'Wayomax Division',
                'user_id': self.team_leads['max'].id,
                'member_ids': [Command.set([self.team_leads['max'].id])],
                'company_id': self.company.id,
            }),
        }

    def setup_categories(self):
        Categ = self.env['product.category']
        fefo = self.env.ref('product_expiry.removal_fefo')
        parent = Categ.create({'name': 'WayoNext Brands', 'removal_strategy_id': fefo.id})
        vals = {'removal_strategy_id': fefo.id}
        if 'property_cost_method' in Categ._fields:
            vals['property_cost_method'] = 'fifo'
        self.categs = {
            'prime': Categ.create(dict(vals, name='Wayoprime Division', parent_id=parent.id)),
            'max': Categ.create(dict(vals, name='Wayomax Division', parent_id=parent.id)),
        }
        self.tags = {}

    def _tag(self, name):
        if name not in self.tags:
            self.tags[name] = self.env['product.tag'].create({'name': name})
        return self.tags[name]

    def setup_partners(self):
        Partner = self.env['res.partner']
        india = self.env.ref('base.in')
        self.vendors = {}
        for key, v in VENDORS.items():
            self.vendors[key] = Partner.create({
                'name': v['name'],
                'is_company': True,
                'street': v['street'], 'city': v['city'], 'zip': v['zip'],
                'state_id': self._state(v['state']).id,
                'country_id': india.id,
                'vat': make_gstin(v['gst_state'], v['pan']),
                'phone': v['phone'], 'email': v['email'],
                'comment': v['note'],
                'wn_partner_type': 'manufacturer',
                'wn_drug_licence': v.get('dl', False),
                'wn_drug_licence_valid_till': self.today + timedelta(days=1100) if v.get('dl') else False,
                'wn_fssai': v.get('fssai', False),
                'property_supplier_payment_term_id': self.term_45.id,
            })
        self.stockists = {}
        self.partner_team = {}
        for (key, name, street, city, zip_code, state, gst_state, pan, limit, terms, dl_days, area) in STOCKISTS:
            team = 'prime' if key in ('kalyan', 'dombivli', 'vashi', 'nashik', 'ahmedabad', 'hyderabad', 'sambhaji') else 'max'
            self.stockists[key] = Partner.create({
                'name': name,
                'is_company': True,
                'street': street, 'city': city, 'zip': zip_code,
                'state_id': self._state(state).id,
                'country_id': india.id,
                'vat': make_gstin(gst_state, pan),
                'phone': '+91 9%09d' % self.rng.randint(10000000, 99999999),
                'email': 'orders@%s.demo' % name.lower().replace(' ', '').replace('.', '')[:20],
                'wn_partner_type': 'stockist',
                'wn_drug_licence': '%s-%s-%06d / %06d' % (state, area[:3].upper(), self.rng.randint(100000, 999999), self.rng.randint(100000, 999999)),
                'wn_drug_licence_valid_till': self.today + timedelta(days=dl_days),
                'credit_limit': limit,
                'property_payment_term_id': (self.term_45 if terms == '45' else self.term_30).id,
                'user_id': self.team_leads[team].id,
                'comment': 'Territory: %s, %s division' % (area, 'Wayoprime' if team == 'prime' else 'Wayomax'),
            })
            self.partner_team[self.stockists[key].id] = team
        self.hospital = Partner.create({
            'name': "Ankur Women's Hospital and IVF Centre",
            'is_company': True,
            'street': 'Murbad Road, Near Shahad Station', 'city': 'Kalyan', 'zip': '421301',
            'state_id': self._state('MH').id, 'country_id': india.id,
            'vat': make_gstin('27', 'AAECA7719Q'),
            'wn_partner_type': 'institution',
            'wn_drug_licence': 'MH-KLN-HSP-20418 (Form 20B, 21B)',
            'wn_drug_licence_valid_till': self.today + timedelta(days=700),
            'property_payment_term_id': self.term_30.id,
            'credit_limit': 300000,
            'user_id': self.team_leads['prime'].id,
        })
        self.walkin = Partner.create({
            'name': 'Counter Sale (Walk-in Patient)',
            'city': 'Ambarnath', 'state_id': self._state('MH').id, 'country_id': india.id,
            'wn_partner_type': 'retail',
        })

    def setup_pricelists(self):
        Pricelist = self.env['product.pricelist']
        inr = self.env.ref('base.INR')
        self.pl_stockist = Pricelist.create({
            'name': 'Stockist (PTS)', 'currency_id': inr.id, 'company_id': self.company.id,
        })
        self.pl_institution = Pricelist.create({
            'name': 'Hospital / Institution (PTR)', 'currency_id': inr.id, 'company_id': self.company.id,
            'item_ids': [Command.create({
                'applied_on': '3_global', 'compute_price': 'percentage', 'percent_price': -11.11,
            })],
        })
        self.pl_retail = Pricelist.create({
            'name': 'Retail Counter (MRP less GST)', 'currency_id': inr.id, 'company_id': self.company.id,
            'item_ids': [Command.create({
                'applied_on': '3_global', 'compute_price': 'percentage', 'percent_price': -38.89,
            })],
        })
        for p in self.stockists.values():
            p.property_product_pricelist = self.pl_stockist
        self.hospital.property_product_pricelist = self.pl_institution
        self.walkin.property_product_pricelist = self.pl_retail

    def setup_products(self):
        Product = self.env['product.template']
        tax_s5 = self._tax('sgst_sale_5')
        tax_p5 = self._tax('sgst_purchase_5')
        self.products = {}
        self.product_vendor = {}
        for (code, name, div, form, pack, sched, hsn, mrp, vendor, tags, comp, ind) in CATALOGUE:
            ptr = round(mrp / 1.05 * 0.80, 2)
            pts = round(ptr * 0.90, 2)
            cost = round(pts * self.rng.uniform(0.34, 0.42), 2)
            tmpl = Product.create({
                'name': name,
                'default_code': code,
                'type': 'consu',
                'is_storable': True,
                'tracking': 'lot',
                'use_expiration_date': True,
                'expiration_time': 730,
                'use_time': 180,
                'removal_time': 60,
                'alert_time': 120,
                'categ_id': self.categs[div].id,
                'product_tag_ids': [Command.set([self._tag(t).id for t in tags])],
                'list_price': pts,
                'standard_price': cost,
                'taxes_id': [Command.set(tax_s5.ids)],
                'supplier_taxes_id': [Command.set(tax_p5.ids)],
                'l10n_in_hsn_code': hsn,
                'sale_ok': True,
                'purchase_ok': True,
                'invoice_policy': 'delivery',
                'description_sale': '%s | %s' % (name, pack),
                'wn_composition': comp,
                'wn_indication': ind,
                'wn_dosage_form': form,
                'wn_pack_size': pack,
                'wn_schedule': sched,
                'wn_mrp': mrp,
                'wn_ptr': ptr,
                'seller_ids': [Command.create({
                    'partner_id': self.vendors[vendor].id,
                    'price': cost,
                    'min_qty': 500,
                    'delay': 21,
                })],
            })
            self.products[code] = tmpl.product_variant_id
            self.product_vendor[code] = vendor

    # -- purchase to stock -------------------------------------------------
    def _receive(self, po, batches):
        """batches: {product_code: [(lot_name, qty, expiry_date, mfg_date), ...]}"""
        picking = po.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        picking.ensure_one()
        for move in picking.move_ids:
            code = move.product_id.default_code
            move.move_line_ids.unlink()
            for lot_name, qty, exp, mfg in batches[code]:
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'picking_id': picking.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'lot_name': lot_name,
                    'expiration_date': self._dt(exp, 0),
                    'quantity': qty,
                })
            move.picked = True
        res = picking.with_context(skip_sms=True, skip_backorder=True, picking_ids_not_to_backorder=picking.ids).button_validate()
        if isinstance(res, dict):
            raise UserError("Receipt %s needs manual confirmation: %s" % (picking.name, res.get('res_model')))
        picking.date_done = self._dt(po.date_order.date() + timedelta(days=4), 15)
        for ml in picking.move_line_ids:
            mfg = next(b[3] for b in batches[ml.product_id.default_code] if b[0] == ml.lot_id.name)
            ml.lot_id.note = '<p>Mfg. date: %s<br/>Manufactured by: %s</p>' % (
                mfg.strftime('%b %Y'), po.partner_id.name)
        return picking

    def setup_purchases(self):
        PO = self.env['purchase.order']
        self.lot_seq = 0
        # Two buying rounds: an older round (short remaining shelf life) and a recent round.
        rounds = [
            {'days_ago': 120, 'mfg_months_ago': 19, 'qty_range': (300, 700), 'paid': True},
            {'days_ago': 62, 'mfg_months_ago': 3, 'qty_range': (1200, 3000), 'paid': True},
            {'days_ago': 18, 'mfg_months_ago': 1, 'qty_range': (1000, 2500), 'paid': False},
        ]
        bill_no = 4100
        for r_idx, rnd in enumerate(rounds):
            for vkey, vendor in self.vendors.items():
                codes = [c for c, v in self.product_vendor.items() if v == vkey]
                if r_idx == 0:
                    codes = codes[:3]  # older stock only for a few fast movers
                if r_idx == 2:
                    codes = codes[::2]
                if not codes:
                    continue
                order_date = self.today - timedelta(days=rnd['days_ago'] + self.rng.randint(0, 4))
                lines = []
                batches = {}
                for code in codes:
                    prod = self.products[code]
                    qty = self.rng.randrange(rnd['qty_range'][0], rnd['qty_range'][1], 50)
                    lines.append(Command.create({
                        'product_id': prod.id,
                        'product_qty': qty,
                        'price_unit': prod.standard_price,
                    }))
                    self.lot_seq += 1
                    mfg = order_date - timedelta(days=30 * rnd['mfg_months_ago'])
                    exp = (mfg + timedelta(days=730)).replace(day=1) - timedelta(days=1)
                    if r_idx == 0:
                        # older round: expiry 4 to 7 months out, so FEFO and near-expiry alerts show
                        exp = self.today + timedelta(days=self.rng.randint(120, 210))
                    lot = '%s%s%03d' % (vkey[:2].upper(), mfg.strftime('%y%m'), self.lot_seq)
                    batches[code] = [(lot, qty, exp, mfg)]
                po = PO.create({
                    'partner_id': vendor.id,
                    'date_order': self._dt(order_date),
                    'partner_ref': 'PI-%s-%d' % (vkey[:3].upper(), 300 + self.lot_seq),
                    'picking_type_id': self.warehouse.in_type_id.id,
                    'user_id': self.users['prakash.joshi@wayonext.demo'].id,
                    'order_line': lines,
                })
                po.button_confirm()
                po.write({'date_approve': self._dt(order_date, 16)})
                self._receive(po, batches)
                po.action_create_invoice()
                bill = po.invoice_ids
                bill_no += 1
                bill.write({
                    'invoice_date': order_date + timedelta(days=4),
                    'ref': '%s/%d/26-27' % (vkey[:3].upper(), bill_no),
                })
                bill.action_post()
                if rnd['paid']:
                    self._pay(bill, order_date + timedelta(days=40))

    def _pay(self, move, pay_date, amount=None):
        vals = {'payment_date': min(pay_date, self.today)}
        if amount:
            vals['amount'] = amount
        self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=move.ids,
        ).create(vals).action_create_payments()

    # -- sales -------------------------------------------------------------
    def _deliver(self, order, ship_date):
        for picking in order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel')):
            picking.action_assign()
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
                move.picked = True
            res = picking.with_context(skip_sms=True, skip_backorder=True, picking_ids_not_to_backorder=picking.ids).button_validate()
            if isinstance(res, dict):
                raise UserError("Delivery %s needs manual confirmation: %s" % (picking.name, res.get('res_model')))
            picking.date_done = self._dt(ship_date, 17)

    def _invoice(self, order, inv_date):
        invoice = order._create_invoices()
        invoice.write({'invoice_date': inv_date})
        invoice.action_post()
        return invoice

    def _order(self, partner, order_date, n_lines, team_key=None, qty_choices=(20, 30, 50, 100, 150, 200)):
        if team_key is None:
            team_key = self.partner_team.get(partner.id, 'prime')
        prefix = 'WP-' if team_key == 'prime' else 'WM-'
        pool = [c for c in self.products if c.startswith(prefix)]
        # cross-division orders happen too
        pool += self.rng.sample([c for c in self.products if not c.startswith(prefix)], 2)
        codes = self.rng.sample(pool, min(n_lines, len(pool)))
        lines = []
        for code in codes:
            qty = self.rng.choice(qty_choices)
            line = {'product_id': self.products[code].id, 'product_uom_qty': qty}
            if qty >= 150 and self.rng.random() < 0.5:
                line['discount'] = 2.0  # volume trade discount
            lines.append(Command.create(line))
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': self._dt(order_date, 10),
            'team_id': self.teams[team_key].id,
            'user_id': partner.user_id.id or self.team_leads[team_key].id,
            'client_order_ref': 'PO/%s/%04d' % (partner.city[:3].upper(), self.rng.randint(1000, 9999)),
            'order_line': lines,
        })
        return order

    def setup_sales(self):
        active = [k for k in self.stockists if k != 'nagpur']
        self.delivered_orders = []
        # 1. Fully closed history: ordered, delivered, invoiced, mostly paid
        for i in range(22):
            key = active[i % len(active)]
            partner = self.stockists[key]
            d = self.today - timedelta(days=self.rng.randint(35, 105))
            so = self._order(partner, d, self.rng.randint(3, 6))
            so.action_confirm()
            so.date_order = self._dt(d, 10)
            self._deliver(so, d + timedelta(days=1))
            inv = self._invoice(so, d + timedelta(days=1))
            self.delivered_orders.append(so)
            if i % 6 == 2:
                self._pay(inv, d + timedelta(days=30), amount=round(inv.amount_total * 0.5, 0))
            elif i % 6 == 4:
                pass  # left unpaid, now overdue for the collections demo
            else:
                self._pay(inv, d + timedelta(days=self.rng.randint(25, 45)))
        # 2. Recent orders, delivered and invoiced, not yet due
        for key in self.rng.sample(active, 8):
            d = self.today - timedelta(days=self.rng.randint(3, 20))
            so = self._order(self.stockists[key], d, self.rng.randint(3, 5))
            so.action_confirm()
            so.date_order = self._dt(d, 10)
            self._deliver(so, d + timedelta(days=1))
            self._invoice(so, d + timedelta(days=1))
            self.delivered_orders.append(so)
        # 3. Confirmed, waiting dispatch (for the warehouse demo)
        for key in ('thane', 'pune', 'ahmedabad'):
            d = self.today - timedelta(days=1)
            so = self._order(self.stockists[key], d, 4)
            so.action_confirm()
            so.date_order = self._dt(d, 10)
        # 4. Open quotations
        for key in ('andheri', 'bengaluru', 'kalyan'):
            self._order(self.stockists[key], self.today, 5)
        # 5. Hospital (institution pricelist) and a rare B2C counter sale
        d = self.today - timedelta(days=12)
        so = self._order(self.hospital, d, 4, team_key='prime', qty_choices=(10, 20, 30))
        so.action_confirm()
        so.date_order = self._dt(d, 10)
        self._deliver(so, d + timedelta(days=1))
        self._invoice(so, d + timedelta(days=1))
        d = self.today - timedelta(days=5)
        so = self._order(self.walkin, d, 2, team_key='prime', qty_choices=(1, 2, 3))
        so.action_confirm()
        so.date_order = self._dt(d, 10)
        self._deliver(so, d)
        inv = self._invoice(so, d)
        self._pay(inv, d)
        # 6. Quotation for the stockist whose drug licence has lapsed (confirm is blocked)
        self._order(self.stockists['nagpur'], self.today - timedelta(days=2), 4)

    def setup_returns(self):
        """Breakage / short-expiry return from a stockist with a credit note."""
        so = self.delivered_orders[4]  # an unpaid invoice, so the credit note offsets it
        picking = so.picking_ids.filtered(lambda p: p.state == 'done')[:1]
        if not picking:
            return
        wizard = self.env['stock.return.picking'].with_context(
            active_id=picking.id, active_ids=picking.ids, active_model='stock.picking',
        ).create({'picking_id': picking.id})
        for i, line in enumerate(wizard.product_return_moves):
            line.quantity = min(10, line.move_id.quantity) if i == 0 else 0
        res = wizard.action_create_returns()
        ret = self.env['stock.picking'].browse(res['res_id'])
        for move in ret.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        ret.with_context(skip_sms=True).button_validate()
        ret.note = '<p>Breakage in transit reported by stockist. Credit note issued.</p>'
        refund = so._create_invoices(final=True)
        if refund and refund.move_type == 'out_refund':
            refund.write({'invoice_date': self.today - timedelta(days=20), 'ref': 'Breakage return'})
            refund.action_post()
            origin = so.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice' and m.state == 'posted')[:1]
            if origin:
                lines = (refund + origin).line_ids.filtered(
                    lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
                if len(lines.move_id) == 2:
                    lines.reconcile()

    def setup_expired_stock(self):
        """Quarantine-worthy stock: one expired batch and one within the alert window."""
        Quant = self.env['stock.quant'].with_context(inventory_mode=True)
        Lot = self.env['stock.lot']
        loc = self.warehouse.lot_stock_id
        for code, lot_name, days, qty in (
            ('WP-WPAN', 'HI2410EXP', -12, 240),
            ('WM-WD3', 'HI2411NRX', 45, 180),
        ):
            prod = self.products[code]
            lot = Lot.create({
                'name': lot_name,
                'product_id': prod.id,
                'company_id': self.company.id,
                'expiration_date': self._dt(self.today + timedelta(days=days), 0),
            })
            quant = Quant.create({
                'product_id': prod.id, 'location_id': loc.id, 'lot_id': lot.id,
                'inventory_quantity': qty,
            })
            quant.action_apply_inventory()

    def setup_reordering(self):
        OP = self.env['stock.warehouse.orderpoint']
        for code in ('WP-OVABD', 'WM-W9', 'WM-DYDRO', 'WP-WCLAV', 'WM-WGEST', 'WP-WCAL'):
            prod = self.products[code]
            OP.create({
                'product_id': prod.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.warehouse.lot_stock_id.id,
                'product_min_qty': 800,
                'product_max_qty': 2500,
                'trigger': 'manual',
            })

    def setup_crm(self):
        Lead = self.env['crm.lead']
        stages = self.env['crm.stage'].search([('is_won', '=', False)], order='sequence')
        def stage(i):
            return stages[min(i, len(stages) - 1)].id
        india = self.env.ref('base.in')
        opps = [
            ('New stockist appointment: Kolhapur', 'Mahalaxmi Pharma Agencies', 'Kolhapur', 'MH', 'prime', 450000, 0, 30),
            ('New stockist appointment: Solapur', 'Siddheshwar Medical Distributors', 'Solapur', 'MH', 'max', 350000, 1, 50),
            ('Surat C&F and stockist tie-up', 'Tapi Healthcare Distributors', 'Surat', 'GJ', 'prime', 900000, 2, 60),
            ('IVF chain rate contract (fertility range)', 'Nova Bloom Fertility Clinics', 'Pune', 'MH', 'prime', 1800000, 2, 70),
            ('Hospital formulary listing: Dydroway, Wayogest', 'Sahyadri Mother and Child Hospital', 'Thane', 'MH', 'max', 600000, 1, 40),
            ('Bhopal stockist for Wayomax', 'Upper Lake Medicos', 'Bhopal', 'MP', 'max', 400000, 0, 20),
            ('Goa stockist appointment', 'Mandovi Pharma', 'Panaji', 'GA', 'prime', 300000, 3, 90),
        ]
        for title, company_name, city, state, team, revenue, st, prob in opps:
            Lead.create({
                'name': title,
                'type': 'opportunity',
                'partner_name': company_name,
                'contact_name': self.rng.choice(['Mr. Shah', 'Mr. Kulkarni', 'Dr. Mehta', 'Mr. Patel', 'Ms. Nair']),
                'city': city,
                'state_id': self._state(state).id,
                'country_id': india.id,
                'expected_revenue': revenue,
                'probability': prob,
                'stage_id': stage(st),
                'team_id': self.teams[team].id,
                'user_id': self.team_leads[team].id,
                'date_deadline': self.today + timedelta(days=self.rng.randint(10, 60)),
            })
        for title, city in (
            ('Enquiry from website: stockistship for Wayo 9 range', 'Jaipur'),
            ('Doctor referral: bulk need for Wayomin IV', 'Kalyan'),
        ):
            Lead.create({'name': title, 'type': 'lead', 'city': city, 'country_id': india.id,
                         'team_id': self.teams['prime'].id})


def post_init_hook(env):
    WayoNextDemoBuilder(env).run()
