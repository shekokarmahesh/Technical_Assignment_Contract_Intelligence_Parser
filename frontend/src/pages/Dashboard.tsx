import { useState } from "react";
import { FileText, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Mock data for contracts
const mockContracts = [
  {
    id: "CTR-001",
    filename: "Service_Agreement_2024.pdf",
    uploadDate: "2024-01-15T10:30:00Z",
    status: "completed",
    overallScore: 92,
    fileSize: "2.4 MB"
  },
  {
    id: "CTR-002", 
    filename: "Vendor_Contract_Acme.pdf",
    uploadDate: "2024-01-14T14:20:00Z",
    status: "processing",
    overallScore: null,
    fileSize: "1.8 MB"
  },
  {
    id: "CTR-003",
    filename: "Employment_Agreement.pdf", 
    uploadDate: "2024-01-13T09:15:00Z",
    status: "completed",
    overallScore: 87,
    fileSize: "3.2 MB"
  },
  {
    id: "CTR-004",
    filename: "Lease_Agreement_Downtown.pdf",
    uploadDate: "2024-01-12T16:45:00Z", 
    status: "failed",
    overallScore: null,
    fileSize: "4.1 MB"
  },
  {
    id: "CTR-005",
    filename: "Software_License_Agreement.pdf",
    uploadDate: "2024-01-11T11:30:00Z",
    status: "pending",
    overallScore: null,
    fileSize: "1.5 MB"
  }
];

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
      <span className="text-muted-foreground ml-1">/100</span>
    </div>
  );
};

const Dashboard = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const contractsPerPage = 10;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPages = Math.ceil(mockContracts.length / contractsPerPage);
  const startIndex = (currentPage - 1) * contractsPerPage;
  const displayedContracts = mockContracts.slice(startIndex, startIndex + contractsPerPage);

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
              <div className="text-2xl font-bold">{mockContracts.length}</div>
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
                {mockContracts.filter(c => c.status === 'completed').length}
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Processing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-processing">
                {mockContracts.filter(c => c.status === 'processing').length}
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
                {Math.round(
                  mockContracts
                    .filter(c => c.overallScore !== null)
                    .reduce((acc, c) => acc + (c.overallScore || 0), 0) /
                  mockContracts.filter(c => c.overallScore !== null).length
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Contracts Table */}
        <Card className="card-elegant">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>All Contracts</span>
              <Button asChild size="sm">
                <Link to="/upload">
                  <FileText className="h-4 w-4 mr-2" />
                  Upload New
                </Link>
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
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
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {displayedContracts.map((contract) => (
                    <tr key={contract.id} className="border-b border-border hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-4">
                        <Link 
                          to={`/contracts/${contract.id}`}
                          className="font-medium text-primary hover:text-primary-hover"
                        >
                          {contract.id}
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{contract.filename}</div>
                          <div className="text-sm text-muted-foreground">{contract.fileSize}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {formatDate(contract.uploadDate)}
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={contract.status} />
                      </td>
                      <td className="py-3 px-4">
                        <ScoreBadge score={contract.overallScore} />
                      </td>
                      <td className="py-3 px-4">
                        <Button asChild variant="outline" size="sm">
                          <Link to={`/contracts/${contract.id}`}>
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
            {totalPages > 1 && (
              <div className="flex justify-center items-center space-x-2 mt-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;