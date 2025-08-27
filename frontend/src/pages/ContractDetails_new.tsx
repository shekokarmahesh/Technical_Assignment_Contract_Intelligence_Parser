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
  RefreshCw,
  Trash2
} from "lucide-react";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  useContractDetails, 
  useContractStatus, 
  useDownloadContract, 
  useDeleteContract,
  useRefreshContract 
} from "@/services/queries";
import { useNavigate } from "react-router-dom";

const ContractDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { refreshStatus, refreshDetails } = useRefreshContract();
  
  // Hooks for API calls
  const { data: status, isLoading: statusLoading } = useContractStatus(id!, !!id);
  const { data: contract, isLoading: contractLoading, error: contractError } = useContractDetails(
    id!, 
    !!id && status?.status === 'completed'
  );
  const downloadMutation = useDownloadContract();
  const deleteMutation = useDeleteContract();

  if (!id) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card className="text-center">
            <CardContent className="pt-6">
              <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Invalid Contract ID</h2>
              <p className="text-muted-foreground">The contract ID provided is not valid.</p>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const handleDownload = () => {
    if (status) {
      downloadMutation.mutate({
        contractId: id,
        filename: status.filename || `contract_${id}.pdf`
      });
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this contract? This action cannot be undone.')) {
      try {
        await deleteMutation.mutateAsync(id);
        navigate('/contracts');
      } catch (error) {
        // Error is handled by the mutation
      }
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-success";
    if (score >= 70) return "text-warning";
    return "text-error";
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Loading states
  if (statusLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card className="text-center">
            <CardContent className="pt-6">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">Loading contract status...</p>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  // Error states
  if (!status) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card className="text-center">
            <CardContent className="pt-6">
              <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Contract Not Found</h2>
              <p className="text-muted-foreground mb-4">
                The contract with ID {id} could not be found.
              </p>
              <Button asChild>
                <Link to="/contracts">Back to Contracts</Link>
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <Button asChild variant="outline" size="sm">
                <Link to="/contracts">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Contracts
                </Link>
              </Button>
              <div>
                <h1 className="text-3xl font-bold">{status.filename}</h1>
                <p className="text-muted-foreground">
                  Contract ID: {id.substring(0, 8)}...
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                onClick={() => {
                  refreshStatus(id);
                  refreshDetails(id);
                }}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button 
                variant="outline" 
                onClick={handleDownload}
                disabled={downloadMutation.isPending}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button 
                variant="destructive" 
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>

          {/* Status Card */}
          <Card className="card-elegant mb-8">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${
                    status.status === 'completed' ? 'bg-success/20' :
                    status.status === 'processing' ? 'bg-warning/20' :
                    status.status === 'failed' ? 'bg-destructive/20' : 'bg-muted'
                  }`}>
                    {status.status === 'completed' && <CheckCircle className="h-5 w-5 text-success" />}
                    {status.status === 'processing' && <Clock className="h-5 w-5 text-warning" />}
                    {status.status === 'failed' && <AlertTriangle className="h-5 w-5 text-destructive" />}
                    {status.status === 'pending' && <Clock className="h-5 w-5 text-muted-foreground" />}
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <p className="font-semibold capitalize">{status.status}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-full bg-primary/20">
                    <TrendingUp className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Progress</p>
                    <div className="flex items-center space-x-2">
                      <Progress value={status.progress} className="w-16 h-2" />
                      <span className="text-sm font-medium">{status.progress}%</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-full bg-muted">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">File Size</p>
                    <p className="font-semibold">{formatFileSize(status.file_size)}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-full bg-muted">
                    <Calendar className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Uploaded</p>
                    <p className="font-semibold text-xs">{formatDate(status.upload_date)}</p>
                  </div>
                </div>
              </div>

              {status.status === 'failed' && status.error && (
                <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive font-medium">Error:</p>
                  <p className="text-sm text-destructive">{status.error}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Processing State */}
          {(status.status === 'processing' || status.status === 'pending') && (
            <Card className="card-elegant">
              <CardContent className="p-8 text-center">
                <RefreshCw className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
                <h3 className="text-xl font-semibold mb-2">
                  {status.status === 'processing' ? 'Processing Contract' : 'Contract Queued'}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {status.status === 'processing' 
                    ? 'AI is analyzing your contract and extracting key information...'
                    : 'Your contract is in the queue and will be processed shortly...'
                  }
                </p>
                <Progress value={status.progress} className="w-64 mx-auto" />
                <p className="text-sm text-muted-foreground mt-2">
                  {status.progress}% complete
                </p>
              </CardContent>
            </Card>
          )}

          {/* Contract Details - Only show if completed */}
          {status.status === 'completed' && contract && (
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="grid w-full grid-cols-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="parties">Parties</TabsTrigger>
                <TabsTrigger value="financial">Financial</TabsTrigger>
                <TabsTrigger value="payments">Payments</TabsTrigger>
                <TabsTrigger value="sla">SLA Terms</TabsTrigger>
                <TabsTrigger value="gaps">Gap Analysis</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2" />
                        Overall Score
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={`text-4xl font-bold ${getScoreColor(contract.score || 0)}`}>
                        {contract.score || 0}
                        <span className="text-lg text-muted-foreground">/100</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Contract completeness and quality score
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <AlertTriangle className="h-5 w-5 mr-2" />
                        Identified Gaps
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-4xl font-bold text-warning">
                        {contract.gaps.length}
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Missing or incomplete fields
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Users className="h-5 w-5 mr-2" />
                        Contract Parties
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-4xl font-bold">
                        {contract.extracted_data.parties.length}
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Identified parties in contract
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Confidence Scores */}
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle>Data Extraction Confidence</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(contract.confidence_scores).map(([key, confidence]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-sm font-medium capitalize">
                            {key.replace('_', ' ')}
                          </span>
                          <div className="flex items-center space-x-2">
                            <Progress value={confidence} className="w-24 h-2" />
                            <span className="text-sm font-medium w-12">{confidence}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Parties Tab */}
              <TabsContent value="parties" className="space-y-6">
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Users className="h-5 w-5 mr-2" />
                      Contract Parties
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {contract.extracted_data.parties.map((party, index) => (
                        <div key={index} className="border border-border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold">{party.name}</h4>
                            <Badge variant="secondary">{party.role}</Badge>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-muted-foreground">Legal Entity</p>
                              <p>{party.legal_entity || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Confidence</p>
                              <div className="flex items-center space-x-2">
                                <Progress value={party.confidence} className="w-16 h-2" />
                                <span className="font-medium">{party.confidence}%</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Financial Tab */}
              <TabsContent value="financial" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <DollarSign className="h-5 w-5 mr-2" />
                        Contract Value
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Total Value</p>
                          <p className="text-2xl font-bold">
                            {contract.extracted_data.financial_details.total_value || 'N/A'}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Currency: {contract.extracted_data.financial_details.currency || 'N/A'}
                          </p>
                        </div>
                        {contract.extracted_data.financial_details.tax_information && (
                          <div>
                            <p className="text-sm text-muted-foreground">Tax Rate</p>
                            <p className="font-semibold">
                              {contract.extracted_data.financial_details.tax_information.rate}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle>Revenue Classification</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Type</p>
                          <Badge variant={
                            contract.extracted_data.revenue_classification.type === 'Recurring' 
                              ? 'default' : 'secondary'
                          }>
                            {contract.extracted_data.revenue_classification.type}
                          </Badge>
                        </div>
                        {contract.extracted_data.revenue_classification.billing_cycle && (
                          <div>
                            <p className="text-sm text-muted-foreground">Billing Cycle</p>
                            <p className="font-semibold">
                              {contract.extracted_data.revenue_classification.billing_cycle}
                            </p>
                          </div>
                        )}
                        {contract.extracted_data.revenue_classification.renewal_terms && (
                          <div>
                            <p className="text-sm text-muted-foreground">Renewal Terms</p>
                            <p className="text-sm">
                              {contract.extracted_data.revenue_classification.renewal_terms}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Line Items */}
                {contract.extracted_data.financial_details.line_items && 
                 contract.extracted_data.financial_details.line_items.length > 0 && (
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle>Line Items</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-border">
                              <th className="text-left py-2 px-4">Description</th>
                              <th className="text-left py-2 px-4">Quantity</th>
                              <th className="text-left py-2 px-4">Unit Price</th>
                              <th className="text-left py-2 px-4">Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {contract.extracted_data.financial_details.line_items.map((item, index) => (
                              <tr key={index} className="border-b border-border">
                                <td className="py-2 px-4">{item.description}</td>
                                <td className="py-2 px-4">{item.quantity}</td>
                                <td className="py-2 px-4">{item.unit_price}</td>
                                <td className="py-2 px-4 font-semibold">{item.total}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Payments Tab */}
              <TabsContent value="payments" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <CreditCard className="h-5 w-5 mr-2" />
                        Payment Structure
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {contract.extracted_data.payment_structure.terms && (
                          <div>
                            <p className="text-sm text-muted-foreground">Payment Terms</p>
                            <p className="font-semibold">{contract.extracted_data.payment_structure.terms}</p>
                          </div>
                        )}
                        {contract.extracted_data.payment_structure.schedule && (
                          <div>
                            <p className="text-sm text-muted-foreground">Schedule</p>
                            <p className="font-semibold">{contract.extracted_data.payment_structure.schedule}</p>
                          </div>
                        )}
                        {contract.extracted_data.payment_structure.method && (
                          <div>
                            <p className="text-sm text-muted-foreground">Method</p>
                            <p className="font-semibold">{contract.extracted_data.payment_structure.method}</p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Building className="h-5 w-5 mr-2" />
                        Account Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {contract.extracted_data.account_information.account_number && (
                          <div>
                            <p className="text-sm text-muted-foreground">Account Number</p>
                            <p className="font-semibold">{contract.extracted_data.account_information.account_number}</p>
                          </div>
                        )}
                        {contract.extracted_data.account_information.billing_address && (
                          <div>
                            <p className="text-sm text-muted-foreground">Billing Address</p>
                            <p className="text-sm whitespace-pre-line">
                              {contract.extracted_data.account_information.billing_address}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Contact Information */}
                {(contract.extracted_data.contact_information.emails?.length || 
                  contract.extracted_data.contact_information.phones?.length) && (
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle>Contact Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {contract.extracted_data.contact_information.emails?.length && (
                          <div>
                            <p className="text-sm text-muted-foreground mb-2">Email Addresses</p>
                            <div className="space-y-1">
                              {contract.extracted_data.contact_information.emails.map((email, index) => (
                                <p key={index} className="text-sm">{email}</p>
                              ))}
                            </div>
                          </div>
                        )}
                        {contract.extracted_data.contact_information.phones?.length && (
                          <div>
                            <p className="text-sm text-muted-foreground mb-2">Phone Numbers</p>
                            <div className="space-y-1">
                              {contract.extracted_data.contact_information.phones.map((phone, index) => (
                                <p key={index} className="text-sm">{phone}</p>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* SLA Tab */}
              <TabsContent value="sla" className="space-y-6">
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Shield className="h-5 w-5 mr-2" />
                      Service Level Agreements
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {contract.extracted_data.sla_terms.response_time && (
                        <div>
                          <p className="text-sm text-muted-foreground">Response Time</p>
                          <p className="font-semibold">{contract.extracted_data.sla_terms.response_time}</p>
                          {contract.extracted_data.sla_terms.response_time_confidence && (
                            <div className="flex items-center space-x-2 mt-1">
                              <Progress 
                                value={contract.extracted_data.sla_terms.response_time_confidence} 
                                className="w-16 h-2" 
                              />
                              <span className="text-xs text-muted-foreground">
                                {contract.extracted_data.sla_terms.response_time_confidence}%
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                      {contract.extracted_data.sla_terms.uptime_guarantee && (
                        <div>
                          <p className="text-sm text-muted-foreground">Uptime Guarantee</p>
                          <p className="font-semibold">{contract.extracted_data.sla_terms.uptime_guarantee}</p>
                          {contract.extracted_data.sla_terms.uptime_confidence && (
                            <div className="flex items-center space-x-2 mt-1">
                              <Progress 
                                value={contract.extracted_data.sla_terms.uptime_confidence} 
                                className="w-16 h-2" 
                              />
                              <span className="text-xs text-muted-foreground">
                                {contract.extracted_data.sla_terms.uptime_confidence}%
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                      {contract.extracted_data.sla_terms.penalties && (
                        <div>
                          <p className="text-sm text-muted-foreground">Penalties</p>
                          <p className="font-semibold text-sm">{contract.extracted_data.sla_terms.penalties}</p>
                          {contract.extracted_data.sla_terms.penalties_confidence && (
                            <div className="flex items-center space-x-2 mt-1">
                              <Progress 
                                value={contract.extracted_data.sla_terms.penalties_confidence} 
                                className="w-16 h-2" 
                              />
                              <span className="text-xs text-muted-foreground">
                                {contract.extracted_data.sla_terms.penalties_confidence}%
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Gap Analysis Tab */}
              <TabsContent value="gaps" className="space-y-6">
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <AlertTriangle className="h-5 w-5 mr-2" />
                      Gap Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {contract.gaps.length === 0 ? (
                      <div className="text-center py-8">
                        <CheckCircle className="h-12 w-12 text-success mx-auto mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No gaps identified!</h3>
                        <p className="text-muted-foreground">
                          This contract appears to have all critical information present.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {contract.gaps.map((gap, index) => (
                          <div key={index} className="border border-border rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-semibold">{gap.field}</h4>
                              <Badge variant={
                                gap.importance === 'High' ? 'destructive' :
                                gap.importance === 'Medium' ? 'default' : 'secondary'
                              }>
                                {gap.importance} Priority
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mb-1">
                              Status: <span className="font-medium">{gap.status}</span>
                            </p>
                            <p className="text-sm">{gap.description}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}

          {/* Failed State */}
          {status.status === 'failed' && (
            <Card className="card-elegant">
              <CardContent className="p-8 text-center">
                <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Processing Failed</h3>
                <p className="text-muted-foreground mb-4">
                  There was an error processing this contract.
                </p>
                {status.error && (
                  <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 mb-4">
                    <p className="text-sm text-destructive">{status.error}</p>
                  </div>
                )}
                <div className="flex items-center justify-center space-x-4">
                  <Button variant="outline" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" />
                    Download Original
                  </Button>
                  <Button onClick={handleDelete} variant="destructive">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Contract
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default ContractDetails;
