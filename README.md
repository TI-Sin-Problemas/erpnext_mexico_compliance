# ERPNext Mexico Compliance

ERPNext app to comply with Mexican Rules and Regulations

## Introduction

ERPNext Mexico Compliance has been designed to adapt ERPNext business logic to comply with the Rules and Regulations of Mexican authorities.

It is built on top of [ERPNext][erpnext_github] and [Frappe Framework][frappe_github]

## Installation

The installation steps assumes you have [Frappe Framework][frappe_github] and [ERPNext][erpnext_github] already installed.

### Frappe Cloud

Signup with [Frappe Cloud][frappe_cloud] and refer to the [Installing an app][frappe_cloud_app_install] documentation

### Self Hosting

```bash
# Download app
bench get-app https://github.com/TI-Sin-Problemas/erpnext_mexico_compliance.git --branch version-15

# Install app
bench --site site_name install-app erpnext_mexico_compliance
```

### CFDI Stamping setup

To enable the CFDI Stamping feature, you will need:

- A package of stamps. To buy a package of stamps please contact us by sending an email to info@tisinproblemas.com
- An API Key and API Secret. You will get your API Key and API Secret whith your package of stamps.
- A valid Digital Signing Certificate (CSD) issued by the Mexican Tax Administration Service (SAT)

Once you have all the requirements, on your ERPNext instance follow the steps below:

1. Go to Desktop -> Mexico Compliance -> Digital Signing Certificate
2. Add a Digital Signing Certificate:

   1. Click on _Add Digital Signing Certificate_
   2. Select your Company
   3. Attach your certificate file (.cer)
   4. Attach your certificate key file (.key)
   5. Enter the Certificate key password
   6. Click on _Save_

3. Go to Desktop -> Mexico Compliance -> CFDI Stamping Settings:
   1. Enter your API Key & API Secret
   2. Uncheck the Test mode checkbox in your production environment
   3. Click on _Save_

You can check the total amount of available credits/stamps in the CFDI Stamping Settings by clicking on the _Available Credits_ button

## Features

### CFDI Stamping

The CFDI Stamping feature allows you to create and stamp CFDI documents for **Sales Invoices** and **Payment Entries** as required by Mexican authorities.

#### Sales invoice stamping

Please be aware that in order to successfully stamp a Sales Invoices, some requirements must be met.

- There must be at least 1 Digital Signing Certificate for the Company issuing the Sales Invoice
- You must have available credits/stamps
- The Address of the Company must have a Zip Code
- The Customer must have a valid CFDI Tax Id (RFC)
- The Customer must have a Tax Regime
- The Customer's address must have a Zip Code
- The Invoice Items must have a SAT Product or Service Key
- The UOM of the Invoice Items must have a SAT UOM Key
- The Mode of Payment of the invoice must have a SAT Payment Method
- The invoice must have a SAT Payment Option

To stamp a Sales Invoice, a **Stamp CFDI** button will be available on the **Sales Invoice** form once it has being submitted.

#### Payment Entry stamping

Please be aware that in order to successfully stamp a Payment Entry, some requirements must be met.

- There must be at least 1 Digital Signing Certificate for the Company issuing the Payment Entry
- You must have available credits/stamps
- The Address of the Company must have a Zip Code
- All the Reference Items must have being stamped

### Mexican authorities catalogs

Some of the Mexican authorities catalogs are added as Doctypes

| Doctype                    | Catalog (in spanish)           |
| -------------------------- | ------------------------------ |
| Cancellation reason        | Motivo de cancelación SAT      |
| SAT CFDI Use               | Uso de CFDI SAT                |
| SAT Payment Method         | Forma de pago SAT              |
| SAT Payment Option         | Método de pago SAT             |
| SAT Product Or Service Key | Clave de producto/servicio SAT |
| SAT Tax Regime             | Régimen fiscal SAT             |
| SAT UOM Key                | Clave de unidad de medida SAT  |

### Compliance fields

New fields are created for the following Doctypes

#### Account Doctype

| Field    | Description                                   |
| -------- | --------------------------------------------- |
| Tax Type | Type of Tax for Tax Accounts (IVA, ISR, IEPS) |

#### Bank Account

| Field | Description                                            |
| ----- | ------------------------------------------------------ |
| CLABE | CLABE (Clave Bancaria Estandarizada) for Bank Accounts |

#### Company

| Field          | Description                  |
| -------------- | ---------------------------- |
| SAT Tax Regime | SAT Tax Regime for Companies |

#### Customer

| Field          | Description                  |
| -------------- | ---------------------------- |
| SAT Tax Regime | SAT Tax Regime for Customers |

#### Item

| Field                      | Description                          |
| -------------------------- | ------------------------------------ |
| SAT Product or Service Key | SAT Product or Service Key for Items |

#### Mode of Payment

| Field              | Description                                                     |
| ------------------ | --------------------------------------------------------------- |
| SAT Payment Method | Used to Link Invoices & Payment Entries with SAT Payment Method |

#### Payment Entry

| Field                        | Description                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| Cancellation reason          | If a stamped Payment Entry needs to be cancelled, a Cancellation Reason must be provided        |
| Substitute payment entry     | If the Cancellation Reason requires it, this field allows to specify a Substitute payment entry |
| Stamped XML                  | Holds the XML data generated by the CFDI Stamping process.                                      |
| Cancellation acknowledgement | Cancellation Acknowledgement XML data generated by the CFDI Cancellation Stamping process.      |

#### Sales Invoice

| Field                        | Description                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| Mode of Payment              | Mode of Payment for Sales Invoices                                                         |
| SAT Payment Option           | SAT Payment Option for Sales Invoices                                                      |
| SAT CFDI Use                 | SAT CFDI Use for Sales Invoices                                                            |
| SAT Payment Method           | SAT Payment Method for Sales Invoices                                                      |
| Stamped XML                  | Holds the XML data generated by the CFDI Stamping process.                                 |
| Cancellation reason          | If a stamped Sales Invoice needs to be cancelled, a Cancellation Reason must be provided   |
| Substitute invoice           | If the Cancellation Reason requires it, this field allows to specify a Substitute invoice  |
| Cancellation acknowledgement | Cancellation Acknowledgement XML data generated by the CFDI Cancellation Stamping process. |

#### Sales Invoice Item

| Field                      | Description                                        |
| -------------------------- | -------------------------------------------------- |
| SAT Product or Service Key | SAT Product or Service Key for Sales Invoice Items |

#### Sales Order Item

| Field                      | Description                                      |
| -------------------------- | ------------------------------------------------ |
| SAT Product or Service Key | SAT Product or Service Key for Sales Order Items |

#### UOM

| Field       | Description                                         |
| ----------- | --------------------------------------------------- |
| SAT UOM Key | Used to link Sales Invoice Items with a SAT UOM Key |

#### License

MIT

[erpnext_github]: https://github.com/frappe/erpnext
[frappe_github]: https://github.com/frappe/frappe
[frappe_cloud]: https://frappecloud.com/
[frappe_cloud_app_install]: https://frappecloud.com/docs/installing-an-app
