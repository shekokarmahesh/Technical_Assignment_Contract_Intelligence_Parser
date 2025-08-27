import { useState, useCallback } from "react";
import { Upload as UploadIcon, FileText, X, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  contractId?: string;
}

const Upload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    files.forEach(file => {
      // Validate file type
      if (file.type !== 'application/pdf') {
        toast({
          title: "Invalid File Type",
          description: "Only PDF files are supported.",
          variant: "destructive"
        });
        return;
      }

      // Validate file size (50MB limit)
      const maxSize = 50 * 1024 * 1024; // 50MB in bytes
      if (file.size > maxSize) {
        toast({
          title: "File Too Large", 
          description: "File size must be less than 50MB.",
          variant: "destructive"
        });
        return;
      }

      const fileId = Math.random().toString(36).substr(2, 9);
      const uploadFile: UploadedFile = {
        file,
        id: fileId,
        progress: 0,
        status: 'uploading'
      };

      setUploadedFiles(prev => [...prev, uploadFile]);
      simulateUpload(fileId);
    });
  };

  const simulateUpload = (fileId: string) => {
    const interval = setInterval(() => {
      setUploadedFiles(prev => 
        prev.map(file => {
          if (file.id === fileId) {
            const newProgress = Math.min(file.progress + Math.random() * 20, 100);
            
            if (newProgress >= 100) {
              clearInterval(interval);
              const contractId = `CTR-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
              
              toast({
                title: "Upload Successful",
                description: `Contract ${contractId} is now being processed.`
              });

              // Auto-redirect after 2 seconds
              setTimeout(() => {
                navigate(`/contracts/${contractId}`);
              }, 2000);

              return {
                ...file,
                progress: 100,
                status: 'completed' as const,
                contractId
              };
            }
            
            return { ...file, progress: newProgress };
          }
          return file;
        })
      );
    }, 500);
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Upload Contract</h1>
            <p className="text-muted-foreground">
              Upload PDF contracts for automated intelligence processing and analysis
            </p>
          </div>

          {/* Upload Zone */}
          <Card className="card-elegant mb-8">
            <CardContent className="p-8">
              <div
                className={`upload-zone ${dragActive ? 'upload-zone-active' : ''} p-12 text-center`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
              >
                <UploadIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">
                  {dragActive ? 'Drop files here' : 'Upload your contracts'}
                </h3>
                <p className="text-muted-foreground mb-4">
                  Drag and drop PDF files here, or click to browse
                </p>
                <div className="text-sm text-muted-foreground">
                  <p>Supported format: PDF</p>
                  <p>Maximum file size: 50MB</p>
                </div>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileInput}
                  className="hidden"
                />
              </div>
            </CardContent>
          </Card>

          {/* Upload Progress */}
          {uploadedFiles.length > 0 && (
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle>Upload Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {uploadedFiles.map((uploadFile) => (
                    <div key={uploadFile.id} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-primary" />
                          <div>
                            <p className="font-medium">{uploadFile.file.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {formatFileSize(uploadFile.file.size)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {uploadFile.status === 'completed' && (
                            <>
                              <CheckCircle className="h-5 w-5 text-success" />
                              <span className="text-sm font-medium text-success">
                                ID: {uploadFile.contractId}
                              </span>
                            </>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(uploadFile.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">
                            {uploadFile.status === 'uploading' && 'Uploading...'}
                            {uploadFile.status === 'completed' && 'Upload completed'}
                            {uploadFile.status === 'error' && 'Upload failed'}
                          </span>
                          <span className="font-medium">
                            {Math.round(uploadFile.progress)}%
                          </span>
                        </div>
                        <Progress value={uploadFile.progress} className="h-2" />
                      </div>
                      
                      {uploadFile.status === 'completed' && uploadFile.contractId && (
                        <div className="mt-3 p-3 bg-success-light rounded-md">
                          <p className="text-sm text-success-foreground">
                            Contract uploaded successfully! 
                            <Button
                              asChild
                              variant="link"
                              size="sm"
                              className="p-0 ml-1 h-auto text-success underline"
                            >
                              <span
                                onClick={() => navigate(`/contracts/${uploadFile.contractId}`)}
                                className="cursor-pointer"
                              >
                                View processing status →
                              </span>
                            </Button>
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload Guidelines */}
          <Card className="card-elegant mt-8">
            <CardHeader>
              <CardTitle>Upload Guidelines</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2 text-success">✓ Supported Files</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• PDF format only</li>
                    <li>• Text-based PDFs (not scanned images)</li>
                    <li>• File size up to 50MB</li>
                    <li>• Multiple files supported</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2 text-primary">📋 Best Practices</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Ensure clear, readable text</li>
                    <li>• Include complete contract documents</li>
                    <li>• Remove password protection</li>
                    <li>• Use descriptive filenames</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Upload;