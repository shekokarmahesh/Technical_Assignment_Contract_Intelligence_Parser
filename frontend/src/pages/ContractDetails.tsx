import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Users, 
  DollarSign, 
  Calendar,
  Building,
  CreditCard,
  Shield,
  TrendingUp,
  Download,
  ArrowLeft,
  RefreshCw
} from "lucide-react";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

const ContractDetails = () => {
  const { id } = useParams();
  const { toast } = useToast();
  const [contract, setContract] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setContract({
        id,
        filename: "Service_Agreement_2024.pdf",
        fileSize: "2.4 MB",
        uploadDate: "2024-01-15T10:30:00Z",
        processedDate: "2024-01-15T10:35:00Z",
        status: "completed",
        overallScore: 92,
        extractedData: {
          parties: [
            { name: "TechCorp Solutions Inc.", role: "Service Provider", confidence: 95 },
            { name: "Global Industries Ltd.", role: "Client", confidence: 98 }
          ],
          accountInfo: {
            billingAddress: "123 Business Ave, Suite 100, New York, NY 10001",
            accountNumber: "ACC-2024-001",
            contactEmail: "billing@techcorp.com",
            confidence: 87
          },
          financialDetails: {
            contractValue: "$150,000",
            currency: "USD",
            taxRate: "8.5%",
            lineItems: [
              { description: "Software Development Services", quantity: 1, unitPrice: "$120,000", total: "$120,000" },
              { description: "Technical Support", quantity: 12, unitPrice: "$2,500", total: "$30,000" }
            ],
            confidence: 94
          },
          paymentStructure: {
            terms: "Net 30",
            schedule: "Monthly",
            method: "Wire Transfer",
            bankDetails: "Chase Bank - Account #1234567890",
            confidence: 91
          },
          slaTerms: {
            responseTime: "4 hours",
            uptime: "99.9%",
            penalties: "5% reduction for < 99% uptime",
            confidence: 85
          },
          revenueClassification: {
            type: "Recurring",
            billingCycle: "Monthly",
            renewalTerms: "Auto-renewal unless cancelled 30 days prior",
            confidence: 89
          }
        },
        gapAnalysis: [
          { field: "Termination Clause", importance: "High", status: "Missing" },
          { field: "Intellectual Property Rights", importance: "Medium", status: "Incomplete" }, 
          { field: "Data Privacy Terms", importance: "High", status: "Review Required" }
        ]
      });
      setLoading(false);
    }, 1000);
  }, [id]);

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-success";
    if (score >= 70) return "text-warning";
    return "text-error";
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-success";
    if (confidence >= 75) return "text-warning";
    return "text-error";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Loading contract details...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Contract Not Found</h1>
            <p className="text-muted-foreground mb-4">
              The contract you're looking for doesn't exist or has been removed.
            </p>
            <Button asChild>
              <Link to="/contracts">Back to Dashboard</Link>
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button asChild variant="outline" size="sm">
              <Link to="/contracts">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div>
              <h1 className="text-3xl font-bold">{contract.id}</h1>
              <p className="text-muted-foreground">{contract.filename}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Download Original
            </Button>
          </div>
        </div>

        {/* Status & Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Processing Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-success" />
                <span className="font-medium text-success">Completed</span>
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Overall Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className={`text-2xl font-bold ${getScoreColor(contract.overallScore)}`}>
                  {contract.overallScore}
                </div>
                <span className="text-muted-foreground">/100</span>
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                File Size
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{contract.fileSize}</div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Processed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                {new Date(contract.processedDate).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="parties">Parties</TabsTrigger>
            <TabsTrigger value="financial">Financial</TabsTrigger>
            <TabsTrigger value="payment">Payment</TabsTrigger>
            <TabsTrigger value="sla">SLA Terms</TabsTrigger>
            <TabsTrigger value="gaps">Gap Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="card-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>Revenue Classification</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Type:</span>
                      <Badge className="status-badge-success">
                        {contract.extractedData.revenueClassification.type}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Billing Cycle:</span>
                      <span className="font-medium">{contract.extractedData.revenueClassification.billingCycle}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className={`font-medium ${getConfidenceColor(contract.extractedData.revenueClassification.confidence)}`}>
                        {contract.extractedData.revenueClassification.confidence}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <DollarSign className="h-5 w-5" />
                    <span>Contract Value</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-3xl font-bold text-primary">
                      {contract.extractedData.financialDetails.contractValue}
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Currency:</span>
                      <span className="font-medium">{contract.extractedData.financialDetails.currency}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Tax Rate:</span>
                      <span className="font-medium">{contract.extractedData.financialDetails.taxRate}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="parties" className="space-y-6">
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Contract Parties</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {contract.extractedData.parties.map((party: any, index: number) => (
                    <div key={index} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{party.name}</h4>
                        <Badge variant="outline">{party.role}</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Confidence Score</span>
                        <div className="flex items-center space-x-2">
                          <Progress value={party.confidence} className="w-20" />
                          <span className={`text-sm font-medium ${getConfidenceColor(party.confidence)}`}>
                            {party.confidence}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Building className="h-5 w-5" />
                  <span>Account Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Billing Address</label>
                    <p className="font-medium">{contract.extractedData.accountInfo.billingAddress}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Account Number</label>
                    <p className="font-medium">{contract.extractedData.accountInfo.accountNumber}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Contact Email</label>
                    <p className="font-medium">{contract.extractedData.accountInfo.contactEmail}</p>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t">
                    <span className="text-muted-foreground">Confidence Score</span>
                    <span className={`font-medium ${getConfidenceColor(contract.extractedData.accountInfo.confidence)}`}>
                      {contract.extractedData.accountInfo.confidence}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="financial" className="space-y-6">
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5" />
                  <span>Line Items</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-2 text-muted-foreground">Description</th>
                        <th className="text-right py-2 text-muted-foreground">Quantity</th>
                        <th className="text-right py-2 text-muted-foreground">Unit Price</th>
                        <th className="text-right py-2 text-muted-foreground">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {contract.extractedData.financialDetails.lineItems.map((item: any, index: number) => (
                        <tr key={index} className="border-b border-border">
                          <td className="py-3 font-medium">{item.description}</td>
                          <td className="py-3 text-right">{item.quantity}</td>
                          <td className="py-3 text-right">{item.unitPrice}</td>
                          <td className="py-3 text-right font-medium">{item.total}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex justify-between items-center pt-4 border-t">
                  <span className="text-muted-foreground">Confidence Score</span>
                  <span className={`font-medium ${getConfidenceColor(contract.extractedData.financialDetails.confidence)}`}>
                    {contract.extractedData.financialDetails.confidence}%
                  </span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="payment" className="space-y-6">
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CreditCard className="h-5 w-5" />
                  <span>Payment Structure</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Payment Terms</label>
                      <p className="font-medium text-lg">{contract.extractedData.paymentStructure.terms}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Schedule</label>
                      <p className="font-medium">{contract.extractedData.paymentStructure.schedule}</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Payment Method</label>
                      <p className="font-medium">{contract.extractedData.paymentStructure.method}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Bank Details</label>
                      <p className="font-medium">{contract.extractedData.paymentStructure.bankDetails}</p>
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center pt-4 border-t">
                  <span className="text-muted-foreground">Confidence Score</span>
                  <span className={`font-medium ${getConfidenceColor(contract.extractedData.paymentStructure.confidence)}`}>
                    {contract.extractedData.paymentStructure.confidence}%
                  </span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sla" className="space-y-6">
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Service Level Agreements</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border border-border rounded-lg">
                      <Clock className="h-8 w-8 text-primary mx-auto mb-2" />
                      <div className="font-semibold">{contract.extractedData.slaTerms.responseTime}</div>
                      <div className="text-sm text-muted-foreground">Response Time</div>
                    </div>
                    <div className="text-center p-4 border border-border rounded-lg">
                      <TrendingUp className="h-8 w-8 text-success mx-auto mb-2" />
                      <div className="font-semibold">{contract.extractedData.slaTerms.uptime}</div>
                      <div className="text-sm text-muted-foreground">Uptime Guarantee</div>
                    </div>
                    <div className="text-center p-4 border border-border rounded-lg">
                      <AlertTriangle className="h-8 w-8 text-warning mx-auto mb-2" />
                      <div className="font-semibold text-sm">{contract.extractedData.slaTerms.penalties}</div>
                      <div className="text-sm text-muted-foreground">Penalty Terms</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-4 border-t">
                    <span className="text-muted-foreground">Confidence Score</span>
                    <span className={`font-medium ${getConfidenceColor(contract.extractedData.slaTerms.confidence)}`}>
                      {contract.extractedData.slaTerms.confidence}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="gaps" className="space-y-6">
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Gap Analysis</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {contract.gapAnalysis.map((gap: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                      <div>
                        <div className="font-medium">{gap.field}</div>
                        <div className="text-sm text-muted-foreground">Status: {gap.status}</div>
                      </div>
                      <Badge 
                        className={
                          gap.importance === 'High' ? 'status-badge-error' :
                          gap.importance === 'Medium' ? 'status-badge-warning' :
                          'status-badge-success'
                        }
                      >
                        {gap.importance} Priority
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default ContractDetails;