# WayoNext Pharmaceuticals: Odoo 19 Enterprise Demo Database

Prepared by Ochre Digital. Installs a complete, ready-to-present WayoNext demo on a fresh Odoo 19 database.

## Business model represented

WayoNext owns the brands (Wayoprime and Wayomax divisions). Finished goods are made by third-party manufacturers, received batch-wise with expiry into the Ambarnath warehouse, and sold to stockists under the WayoNext brand. Most sales are B2B to stockists; hospitals and walk-in counter sales are occasional.

## Install

1. Create a fresh Odoo 19 Enterprise database. Leave "Load demonstration data" unticked. Country India.
2. Copy the `wayonext_demo` folder into your custom addons path (Odoo.sh: push to the branch).
3. Apps > Update Apps List > search "WayoNext" > Activate. Takes about two minutes.
4. Optional, after install: Settings > Inventory > tick Expiration Dates and Lots if any menu is not visible to your user.

On a fresh database the main company becomes WayoNext. On a database that is already in use with another chart of accounts (for example an Odoo.sh development build, which always loads Odoo's own demo data), the loader creates WayoNext as a separate company with the Indian chart and makes it the admin's default company. For client demos, a staging or production branch gives the cleanest result, with no Odoo sample companies alongside.

On GitHub, the repository must contain the unzipped `wayonext_demo` folder at its root (repo/wayonext_demo/__manifest__.py), not the zip file.

## What gets created

| Area | Content |
|---|---|
| Company | WayoNext Pharmaceuticals Pvt. Ltd., Ambarnath, Indian chart of accounts, GST, credit limit control on |
| Catalogue | 25 SKUs from wayonext.com in two divisions, with composition, indication, pack size, drug schedule, HSN, MRP, PTR and PTS |
| Manufacturers | 4 third-party makers (Baddi, Haridwar, Tarapur, Daman) with vendor price lists and lead times |
| Stockists | 14 stockists (10 Maharashtra, 4 inter-state), each with GSTIN, drug licence and expiry, credit limit, 30 or 45 day terms |
| Others | 1 IVF hospital on PTR pricelist, 1 walk-in counter customer on MRP pricelist |
| Purchases | 12 purchase orders over 4 months, received batch-wise with expiry dates, vendor bills posted and partly paid |
| Sales | 39 orders: delivered and invoiced history, partial and unpaid invoices (overdue ageing), orders waiting dispatch, open quotations |
| Inventory | FEFO picking, 50+ batches, one expired batch and one near-expiry batch, reorder rules on six fast movers |
| Returns | Breakage return from a stockist with credit note adjusted against the invoice |
| CRM | 7 opportunities (new stockist appointments, IVF chain rate contract, hospital listing) and 2 leads |
| People | 12 employees across Sales, Warehouse, Accounts, Purchase, Regulatory; 6 login users; two division sales teams |

## Demo walkthrough (suggested order)

1. **Product master**: open Dydroway 10. Show the Pharma Details tab (composition, schedule, MRP, PTR, PTS), lot tracking with expiry, vendor on the Purchase tab.
2. **Buy from manufacturer**: Purchase > open a Himgiri order. Show receipt with batch numbers and expiry, then the posted vendor bill.
3. **Stock by batch**: Inventory > Reporting > Stock, group by Lot. Point out FEFO: the older batch of OVABD was used up first.
4. **Expiry control**: Inventory > Lots. Filter "Expiration Alerts". Batch HI2410EXP (Wayopan) is expired; HI2411NRX (Wayo D3) is past its removal date and is not offered for dispatch.
5. **Sell to stockist**: open the quotation for Goodwill Pharma, confirm, deliver (system picks batches by FEFO), invoice. Show CGST + SGST.
6. **Inter-state GST**: open an Ambika Pharma (Ahmedabad) invoice. Shows IGST automatically.
7. **Licence compliance**: open the Vidarbha Pharma (Nagpur) quotation and click Confirm. Blocked because the drug licence expired.
8. **Credit control**: Accounting > Customers > Aged Receivable. Partial and overdue stockists are visible. Credit limit warning appears on new orders for stockists near their limit.
9. **Hospital and counter pricing**: Ankur Women's Hospital order priced at PTR; walk-in counter sale at MRP.
10. **Replenishment**: Inventory > Operations > Replenishment. Reorder rules suggest purchase quantities per manufacturer.
11. **Pipeline**: CRM shows new territory stockist appointments by division.

## Demo logins

All users are created without passwords. Set one from Settings > Users if you want to log in as them.

| User | Role |
|---|---|
| rahul.patil@wayonext.demo | National Sales Manager |
| sneha.kulkarni@wayonext.demo | ASM, Wayoprime |
| amit.deshmukh@wayonext.demo | ASM, Wayomax |
| nilesh.jadhav@wayonext.demo | Warehouse In-charge |
| meera.iyer@wayonext.demo | Accounts Manager |
| prakash.joshi@wayonext.demo | Purchase Executive |

## Data notes

- Company name, address, phone, founder and the full product list are from wayonext.com. Everything else (manufacturers, stockists, GSTINs, drug licence numbers, prices, batch numbers, employees) is fictitious demo data.
- GSTINs are format-valid with correct check digits but are not real registrations.
- All SKUs carry 5% GST following the September 2025 rate rationalisation. HSN codes and rates per SKU should be confirmed with WayoNext's tax adviser before go-live, particularly for the nutraceutical range.
- Pricing logic used: PTR = MRP less GST less 20% retailer margin; PTS = PTR less 10% stockist margin; purchase cost 34% to 42% of PTS.
- Dates are generated relative to the install date, so the demo always looks current.

## Validation

Installed and verified on Odoo 19.0 (community core, which Enterprise builds on), on a blank database, one pre-set to India, and one with Odoo demo data loaded (as on Odoo.sh development builds). Checks run: Indian chart and GST, intra-state and inter-state tax split, FEFO allocation, expiry and removal alerts, licence block on order confirmation, partial payments and overdue ageing, return with credit note.
