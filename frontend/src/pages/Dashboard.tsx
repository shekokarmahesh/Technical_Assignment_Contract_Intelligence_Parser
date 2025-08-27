import { useState } from "react";
import { FileText, Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useContractList, useContractStats } from "@/services/queries";

const StatusBadge = ({ status }: { status: string }) => {
  const statusConfig = {
    completed: { 
      icon: CheckCircle, 
      className: "status-badge-success",
      label: "Completed" 
    },
    processing: { 
      icon: Clock, 
      className: "status-badge-processing", 
      label: "Processing" 
    },
    failed: { 
      icon: XCircle, 
      className: "status-badge-error",
      label: "Failed" 
    },
    pending: { 
      icon: AlertCircle, 
      className: "status-badge-warning",
      label: "Pending" 
    }
  };

  const config = statusConfig[status as keyof typeof statusConfig];
  const Icon = config.icon;

  return (
    <Badge className={config.className}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

const ScoreBadge = ({ score }: { score: number | null }) => {
  if (score === null) return <span className="text-muted-foreground">-</span>;
  
  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-success";
    if (score >= 70) return "text-warning";
    return "text-error";
  };

  return (
    <div className="flex items-center">
      <div className={`text-lg font-bold ${getScoreColor(score)}`}>
        {score}
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const contractsPerPage = 10;

  // Fetch contracts with pagination and filtering
  const { data: contractsData, isLoading, error, refetch } = useContractList({
    page: currentPage,
    limit: contractsPerPage,
    status: statusFilter || undefined,
    sort_by: "upload_date",
    sort_order: "desc"
  });

  // Fetch statistics
  const { data: stats } = useContractStats();

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card className="text-center">
            <CardContent className="pt-6">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Contracts</h2>
              <p className="text-muted-foreground mb-4">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
              <Button onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Contract Dashboard</h1>
          <p className="text-muted-foreground">
            Manage and analyze your contract intelligence data
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Contracts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats?.total_contracts ?? 0}
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Completed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {stats?.completed_contracts ?? 0}
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Completion Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-processing">
                {stats?.completion_rate ? `${stats.completion_rate}%` : '0%'}
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats?.average_score ?? 0}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Contracts Table */}
        <Card className="card-elegant">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>All Contracts</span>
              <div className="flex items-center gap-4">
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1 text-sm border border-border rounded-md bg-background"
                >
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
                <Button asChild size="sm">
                  <Link to="/upload">
                    <FileText className="h-4 w-4 mr-2" />
                    Upload New
                  </Link>
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Loading contracts...</p>
              </div>
            ) : !contractsData?.contracts?.length ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No contracts found</h3>
                <p className="text-muted-foreground mb-4">
                  Get started by uploading your first contract
                </p>
                <Button asChild>
                  <Link to="/upload">Upload Contract</Link>
                </Button>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Contract ID
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Filename
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Upload Date
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Status
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Score
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          File Size
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {contractsData.contracts.map((contract) => (
                        <tr key={contract.contract_id} className="border-b border-border hover:bg-muted/30 transition-colors">
                          <td className="py-3 px-4">
                            <Link 
                              to={`/contracts/${contract.contract_id}`}
                              className="font-medium text-primary hover:text-primary-hover"
                            >
                              {contract.contract_id.substring(0, 8)}...
                            </Link>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center">
                              <FileText className="h-4 w-4 mr-2 text-muted-foreground" />
                              <span className="truncate max-w-xs">{contract.filename}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-sm text-muted-foreground">
                            {formatDate(contract.upload_date)}
                          </td>
                          <td className="py-3 px-4">
                            <StatusBadge status={contract.status} />
                          </td>
                          <td className="py-3 px-4">
                            <ScoreBadge score={contract.score ?? null} />
                          </td>
                          <td className="py-3 px-4 text-sm text-muted-foreground">
                            {formatFileSize(contract.file_size)}
                          </td>
                          <td className="py-3 px-4">
                            <Button asChild variant="outline" size="sm">
                              <Link to={`/contracts/${contract.contract_id}`}>
                                View Details
                              </Link>
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {contractsData.pagination.total_pages > 1 && (
                  <div className="flex justify-between items-center mt-6 pt-4 border-t border-border">
                    <div className="text-sm text-muted-foreground">
                      Showing {((contractsData.pagination.current_page - 1) * contractsPerPage) + 1} to{' '}
                      {Math.min(contractsData.pagination.current_page * contractsPerPage, contractsData.pagination.total_count)} of{' '}
                      {contractsData.pagination.total_count} contracts
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={!contractsData.pagination.has_prev}
                      >
                        Previous
                      </Button>
                      <span className="text-sm">
                        Page {contractsData.pagination.current_page} of {contractsData.pagination.total_pages}
                      </span>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => setCurrentPage(prev => prev + 1)}
                        disabled={!contractsData.pagination.has_next}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;
