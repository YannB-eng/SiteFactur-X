import os
from fpdf import FPDF
from lxml import etree
from datetime import datetime

# --- CONFIGURATION DES DONNÉES ---
INVOICE_DATA = {
    "number": "FACT-202601-001",
    "date": "2026-01-27",
    "due_date": "2026-03-31",
    "currency": "EUR",
    "seller": {
        "name": "BYOSPHERE",
        "siret": "79238423200023",
        "vat_id": "FR92792384232",
        "address": "4249 RTE DU MONASTERE",
        "city": "12190 COUBISOU"
    },
    "buyer": {
        "name": "CAFE-RESTAURANT VERDIER (BRASSERIE DU THERON)",
        "siret": "44098837600016",
        "vat_id": "FR85440988376",
        "address": "22 PL DE LA PORTE THERON",
        "city": "12500 SAINT COME D'OLT"
    },
    "lines": [
        {
            "id": "1",
            "name": "Prestation formation n8n (27 janvier 2026)",
            "qty": 1.0,
            "unit": "H87", 
            "price": 350.00,
            "vat_rate": 20.0
        }
    ]
}

def generate_cii_xml(data):
    """Génère le XML Factur-X au format UN/CEFACT CII (Profil BASIC)"""
    NS_MAP = {
        'rsm': "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
        'ram': "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
        'udt': "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
    }
    root = etree.Element("{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice", nsmap=NS_MAP)
    
    ctx = etree.SubElement(root, "{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}ExchangedDocumentContext")
    param = etree.SubElement(ctx, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}GuidelineSpecifiedDocumentContextParameter")
    etree.SubElement(param, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID").text = "urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:basic"
    
    doc = etree.SubElement(root, "{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}ExchangedDocument")
    etree.SubElement(doc, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID").text = data["number"]
    etree.SubElement(doc, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TypeCode").text = "380"
    issue_date = etree.SubElement(doc, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}IssueDateTime")
    dt = etree.SubElement(issue_date, "{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}DateTimeString", format="102")
    dt.text = data["date"].replace("-", "")
    
    trans = etree.SubElement(root, "{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SupplyChainTradeTransaction")
    
    total_ht = 0
    total_vat = 0
    
    for line in data["lines"]:
        line_ht = line["qty"] * line["price"]
        line_vat = line_ht * (line["vat_rate"] / 100)
        total_ht += line_ht
        total_vat += line_vat
        
        item = etree.SubElement(trans, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}IncludedSupplyChainTradeLineItem")
        assoc = etree.SubElement(item, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}AssociatedDocumentLineDocument")
        etree.SubElement(assoc, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineID").text = line["id"]
        
        prod = etree.SubElement(item, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradeProduct")
        etree.SubElement(prod, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name").text = line["name"]
        
        agree = etree.SubElement(item, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedLineTradeAgreement")
        net = etree.SubElement(agree, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}NetPriceProductTradePrice")
        etree.SubElement(net, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ChargeAmount").text = f"{line['price']:.2f}"
        
        deliv = etree.SubElement(item, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedLineTradeDelivery")
        qty = etree.SubElement(deliv, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BilledQuantity", unitCode=line["unit"])
        qty.text = f"{line['qty']:.1f}"
        
        settle = etree.SubElement(item, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedLineTradeSettlement")
        tax = etree.SubElement(settle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableTradeTax")
        etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TypeCode").text = "VAT"
        etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}CategoryCode").text = "S"
        etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}RateApplicablePercent").text = f"{line['vat_rate']:.2f}"
        
        summa = etree.SubElement(settle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradeSettlementLineMonetarySummation")
        etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineTotalAmount").text = f"{line_ht:.2f}"

    total_ttc = total_ht + total_vat

    hagreement = etree.SubElement(trans, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableHeaderTradeAgreement")
    seller = etree.SubElement(hagreement, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SellerTradeParty")
    etree.SubElement(seller, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name").text = data["seller"]["name"]
    sorg = etree.SubElement(seller, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedLegalOrganization")
    etree.SubElement(sorg, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID").text = data["seller"]["siret"]
    svat = etree.SubElement(seller, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTaxRegistration")
    etree.SubElement(svat, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID", schemeID="VA").text = data["seller"]["vat_id"]
    
    buyer = etree.SubElement(hagreement, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BuyerTradeParty")
    etree.SubElement(buyer, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name").text = data["buyer"]["name"]
    borg = etree.SubElement(buyer, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedLegalOrganization")
    etree.SubElement(borg, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID").text = data["buyer"]["siret"]
    bvat = etree.SubElement(buyer, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTaxRegistration")
    etree.SubElement(bvat, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID", schemeID="VA").text = data["buyer"]["vat_id"]

    etree.SubElement(trans, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableHeaderTradeDelivery")

    hsettle = etree.SubElement(trans, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableHeaderTradeSettlement")
    etree.SubElement(hsettle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}InvoiceCurrencyCode").text = data["currency"]
    
    # Due Date (BT-9)
    terms = etree.SubElement(hsettle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradePaymentTerms")
    ddate = etree.SubElement(terms, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}DueDateDateTime")
    dt2 = etree.SubElement(ddate, "{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}DateTimeString", format="102")
    dt2.text = data["due_date"].replace("-", "")

    tax = etree.SubElement(hsettle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableTradeTax")
    etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BasisAmount").text = f"{total_ht:.2f}"
    etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}AttributeAmount").text = f"{total_vat:.2f}"
    etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TypeCode").text = "VAT"
    etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}CategoryCode").text = "S"
    etree.SubElement(tax, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}RateApplicablePercent").text = f"{data['lines'][0]['vat_rate']:.2f}"

    summa = etree.SubElement(hsettle, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradeSettlementHeaderMonetarySummation")
    etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineTotalAmount").text = f"{total_ht:.2f}"
    etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TaxBasisTotalAmount").text = f"{total_ht:.2f}"
    etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TaxTotalAmount", currencyID=data["currency"]).text = f"{total_vat:.2f}"
    etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}GrandTotalAmount").text = f"{total_ttc:.2f}"
    etree.SubElement(summa, "{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}DuePayableAmount").text = f"{total_ttc:.2f}"

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def get_facturx_xmp(profile="BASIC"):
    return f"""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="" xmlns:fx="urn:factur-x.eu:1p0:">
   <fx:ConformanceLevel>{profile}</fx:ConformanceLevel>
   <fx:DocumentFileName>factur-x.xml</fx:DocumentFileName>
   <fx:DocumentType>INVOICE</fx:DocumentType>
   <fx:Version>1.0</fx:Version>
  </rdf:Description>
  <rdf:Description rdf:about="" xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
   <pdfaid:part>3</pdfaid:part>
   <pdfaid:conformance>B</pdfaid:conformance>
  </rdf:Description>
 </rdf:RDF>"""

class FacturePDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(63, 102, 241) 
        self.cell(0, 10, 'FACTURE', ln=0, align='R')
        self.ln(10)

def generate_pdf_v2(data, xml_content, filename):
    pdf = FacturePDF()
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 7, data["seller"]["name"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 5, data["seller"]["address"], new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, data["seller"]["city"], new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"SIRET : {data['seller']['siret']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    
    pdf.set_x(110)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, "DESTINATAIRE :", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(110)
    pdf.set_font('helvetica', '', 10)
    pdf.multi_cell(0, 5, f"{data['buyer']['name']}\n{data['buyer']['address']}\n{data['buyer']['city']}")
    pdf.ln(20)
    
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 7, f"Facture N° {data['number']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.cell(100, 8, " Description", border=1)
    pdf.cell(20, 8, "Qté", border=1, align='C')
    pdf.cell(30, 8, "Unit. HT", border=1, align='C')
    pdf.cell(30, 8, "Tot HT", border=1, align='C')
    pdf.ln()
    
    total_ht = 0
    for line in data["lines"]:
        line_ht = line["qty"] * line["price"]
        total_ht += line_ht
        pdf.cell(100, 8, f" {line['name']}", border=1)
        pdf.cell(20, 8, f"{line['qty']}", border=1, align='C')
        pdf.cell(30, 8, f"{line['price']:.2f}", border=1, align='R')
        pdf.cell(30, 8, f"{line_ht:.2f}", border=1, align='R')
        pdf.ln()
    
    pdf.ln(5)
    pdf.set_x(130)
    pdf.cell(30, 7, "Total TTC")
    pdf.cell(30, 7, f"{total_ht * 1.20:.2f} EUR", align='R', new_x="LMARGIN", new_y="NEXT")

    # --- FACTUR-X SPECIFIC ---
    pdf.embed_file(bytes=xml_content, basename="factur-x.xml")
    pdf.set_xmp_metadata(get_facturx_xmp())
    
    pdf.output(filename)
    print(f"Fichier généré : {filename}")

if __name__ == "__main__":
    xml_data = generate_cii_xml(INVOICE_DATA)
    generate_pdf_v2(INVOICE_DATA, xml_data, "2026-04 Test Factur-Xv2.pdf")
