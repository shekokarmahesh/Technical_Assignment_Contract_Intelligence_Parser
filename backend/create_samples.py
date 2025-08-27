"""Sample contract PDF generator for testing the contract intelligence system"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_contract_1():
    """Create a comprehensive service agreement PDF"""
    filename = "sample_contract_service_agreement.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("SERVICE AGREEMENT", title_style))
    story.append(Spacer(1, 20))
    
    # Contract details
    content = [
        ("Contract ID:", "CTR-2024-001"),
        ("Effective Date:", "January 1, 2024"),
        ("", ""),
        ("PARTIES", ""),
        ("", ""),
        ("Service Provider:", "TechCorp Solutions Inc."),
        ("Legal Entity:", "Delaware Corporation"),
        ("Address:", "123 Technology Drive, San Francisco, CA 94105"),
        ("Authorized Signatory:", "John Smith, CEO"),
        ("", ""),
        ("Client:", "Global Industries Ltd."),
        ("Legal Entity:", "Limited Company"),
        ("Address:", "456 Business Ave, New York, NY 10001"),
        ("Authorized Signatory:", "Jane Doe, CTO"),
        ("", ""),
        ("FINANCIAL DETAILS", ""),
        ("", ""),
        ("Total Contract Value:", "$150,000 USD"),
        ("Currency:", "United States Dollars (USD)"),
        ("Tax Rate:", "8.5%"),
        ("", ""),
        ("LINE ITEMS", ""),
        ("Software Development Services  1  $120,000  $120,000", ""),
        ("Technical Support  12  $2,500  $30,000", ""),
        ("", ""),
        ("PAYMENT STRUCTURE", ""),
        ("", ""),
        ("Payment Terms:", "Net 30 days"),
        ("Payment Schedule:", "Monthly billing cycle"),
        ("Payment Method:", "Wire Transfer"),
        ("Bank Details:", "Chase Bank - Account #1234567890"),
        ("", ""),
        ("SERVICE LEVEL AGREEMENTS", ""),
        ("", ""),
        ("Response Time:", "4 hours for critical issues"),
        ("Uptime Guarantee:", "99.9% monthly uptime"),
        ("Penalty Clause:", "5% monthly fee reduction for < 99% uptime"),
        ("", ""),
        ("ACCOUNT INFORMATION", ""),
        ("", ""),
        ("Account Number:", "ACC-2024-001"),
        ("Billing Contact:", "billing@techcorp.com"),
        ("Technical Contact:", "support@techcorp.com"),
        ("Phone:", "(555) 123-4567"),
        ("", ""),
        ("REVENUE CLASSIFICATION", ""),
        ("", ""),
        ("Service Type:", "Recurring monthly subscription"),
        ("Billing Cycle:", "Monthly on the 1st"),
        ("Auto-renewal:", "Automatically renews unless cancelled 30 days prior"),
        ("", ""),
        ("ADDITIONAL TERMS", ""),
        ("", ""),
        ("Contract Duration:", "12 months from effective date"),
        ("Termination Notice:", "30 days written notice required"),
        ("Governing Law:", "State of California"),
    ]
    
    for item, value in content:
        if item == "":
            story.append(Spacer(1, 12))
        elif item in ["PARTIES", "FINANCIAL DETAILS", "LINE ITEMS", "PAYMENT STRUCTURE", 
                      "SERVICE LEVEL AGREEMENTS", "ACCOUNT INFORMATION", "REVENUE CLASSIFICATION", 
                      "ADDITIONAL TERMS"]:
            story.append(Paragraph(item, styles['Heading2']))
            story.append(Spacer(1, 6))
        else:
            text = f"<b>{item}</b> {value}" if value else item
            story.append(Paragraph(text, styles['Normal']))
    
    doc.build(story)
    return filename

def create_sample_contract_2():
    """Create a simpler vendor contract PDF"""
    filename = "sample_contract_vendor_agreement.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1
    )
    story.append(Paragraph("VENDOR SERVICES CONTRACT", title_style))
    story.append(Spacer(1, 20))
    
    content = """
    This agreement is between Acme Corporation (Client) and QuickServices LLC (Vendor).
    
    Contract Value: $75,000
    Payment Terms: Net 45 days
    
    Services to be provided:
    - Consulting Services: $50,000
    - Training Programs: $25,000
    
    The vendor agrees to provide services with a response time of 8 hours.
    Uptime guarantee is 99.5%.
    
    Contact Information:
    Vendor Email: contact@quickservices.com
    Client Email: procurement@acme.corp
    
    This is a one-time project contract.
    """
    
    story.append(Paragraph(content, styles['Normal']))
    doc.build(story)
    return filename

def create_sample_contract_3():
    """Create a lease agreement PDF"""
    filename = "sample_contract_lease_agreement.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    content = """
    COMMERCIAL LEASE AGREEMENT
    
    Landlord: Downtown Properties Inc.
    Tenant: StartupCo Ltd.
    
    Monthly Rent: $8,500 USD
    Security Deposit: $17,000
    Lease Term: 24 months
    
    Payment due on the 1st of each month.
    Late fee: $250 after 5 days.
    
    Property maintenance response time: 24 hours for emergencies.
    
    Contact: leasing@downtownprops.com
    Phone: (555) 987-6543
    
    This is a recurring monthly lease agreement.
    """
    
    story.append(Paragraph(content, styles['Normal']))
    doc.build(story)
    return filename

def main():
    """Generate all sample contracts"""
    try:
        # Create samples directory
        os.makedirs("samples", exist_ok=True)
        os.chdir("samples")
        
        print("📄 Generating sample contract PDFs...")
        
        # Generate contracts
        file1 = create_sample_contract_1()
        print(f"✅ Created {file1}")
        
        file2 = create_sample_contract_2()
        print(f"✅ Created {file2}")
        
        file3 = create_sample_contract_3()
        print(f"✅ Created {file3}")
        
        print(f"\n🎉 Generated 3 sample contracts in ./samples/ directory")
        print("You can use these to test the contract intelligence system!")
        
    except ImportError:
        print("⚠️  reportlab not installed. Install with: uv add reportlab")
        print("Creating simple text-based samples instead...")
        create_text_samples()

def create_text_samples():
    """Create simple text file samples when reportlab is not available"""
    samples = {
        "sample_contract_info.txt": """
Sample Contract Information for Testing

These would be PDF files in a real scenario. Here's what each contract contains:

1. Service Agreement (sample_contract_service_agreement.pdf):
   - Parties: TechCorp Solutions Inc. (Service Provider) and Global Industries Ltd. (Client)
   - Value: $150,000 USD
   - Payment: Net 30 days, Monthly billing
   - SLA: 4 hours response time, 99.9% uptime
   - Type: Recurring monthly subscription

2. Vendor Agreement (sample_contract_vendor_agreement.pdf):
   - Parties: Acme Corporation (Client) and QuickServices LLC (Vendor)
   - Value: $75,000
   - Payment: Net 45 days
   - SLA: 8 hours response time, 99.5% uptime
   - Type: One-time project

3. Lease Agreement (sample_contract_lease_agreement.pdf):
   - Parties: Downtown Properties Inc. (Landlord) and StartupCo Ltd. (Tenant)
   - Value: $8,500/month
   - Payment: Monthly on 1st
   - SLA: 24 hours emergency response
   - Type: Recurring monthly lease

To test with real PDFs, install reportlab: uv add reportlab
Then run: python create_samples.py
        """
    }
    
    for filename, content in samples.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Created {filename}")

if __name__ == "__main__":
    main()
