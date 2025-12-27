'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageShell } from '@/components/layout/PageShell';
import { FileDropzone } from '@/components/upload/FileDropzone';
import { ConfigPanel, type UploadFormData } from '@/components/upload/ConfigPanel';
import { AdditionalContext } from '@/components/upload/AdditionalContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useUploadWorkflow, useStartWorkflow } from '@/lib/queries';
import { Sparkles, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

export default function UploadPage() {
  const router = useRouter();
  const uploadMutation = useUploadWorkflow();
  const startMutation = useStartWorkflow();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState<UploadFormData>({
    subsystem: '',
    domain: 'generic',
    reviewMode: 'after',
    analysisMode: 'standard',
    qualityThreshold: 0.8,
    maxIterations: 3,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof UploadFormData, string>>>({});
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFormChange = (data: Partial<UploadFormData>) => {
    setFormData((prev) => ({ ...prev, ...data }));
    // Clear errors for changed fields
    const changedKeys = Object.keys(data) as (keyof UploadFormData)[];
    setErrors((prev) => {
      const newErrors = { ...prev };
      changedKeys.forEach((key) => delete newErrors[key]);
      return newErrors;
    });
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof UploadFormData, string>> = {};

    if (!selectedFile) {
      toast.error('Please select a file to upload');
      return false;
    }

    if (!formData.subsystem.trim()) {
      newErrors.subsystem = 'Target subsystem is required';
    }

    if (!formData.domain) {
      newErrors.domain = 'Domain is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !selectedFile) return;

    try {
      // Step 1: Upload file and create workflow
      setUploadProgress(25);
      const uploadResponse = await uploadMutation.mutateAsync({
        file: selectedFile,
        subsystem: formData.subsystem,
        domain: formData.domain,
        reviewMode: formData.reviewMode,
        analysisMode: formData.analysisMode,
        qualityThreshold: formData.qualityThreshold,
        maxIterations: formData.maxIterations,
      });

      setUploadProgress(50);

      // Step 2: Start workflow execution
      await startMutation.mutateAsync(uploadResponse.workflowId);

      setUploadProgress(100);

      toast.success('Workflow started successfully!');

      // Navigate to progress page
      setTimeout(() => {
        router.push(`/progress/${uploadResponse.workflowId}`);
      }, 500);
    } catch (error: any) {
      console.error('Upload failed:', error);
      toast.error(error.response?.data?.message || 'Failed to start workflow. Please try again.');
      setUploadProgress(0);
    }
  };

  const isLoading = uploadMutation.isPending || startMutation.isPending;

  return (
    <PageShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/' },
        { label: 'New Workflow' },
      ]}
      title="Start New Workflow"
      description="Upload your specification document and configure the decomposition workflow"
    >
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: File Upload */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-border-default bg-bg-secondary">
              <CardHeader>
                <CardTitle className="text-lg">Specification Document</CardTitle>
                <CardDescription>
                  Upload the system specification to decompose into subsystem requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileDropzone
                  onFileSelect={setSelectedFile}
                  selectedFile={selectedFile}
                  isUploading={isLoading}
                  uploadProgress={uploadProgress}
                  error={uploadMutation.error?.message}
                />
              </CardContent>
            </Card>

            {/* Additional Context Section */}
            <AdditionalContext />
          </div>

          {/* Right Column: Configuration */}
          <div className="lg:col-span-1">
            <Card className="border-border-default bg-bg-secondary sticky top-20">
              <CardHeader>
                <CardTitle className="text-lg">Configuration</CardTitle>
                <CardDescription>
                  Customize the decomposition workflow settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ConfigPanel
                  formData={formData}
                  onChange={handleFormChange}
                  errors={errors}
                />

                <Separator className="my-6 bg-border-default" />

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  size="lg"
                  disabled={!selectedFile || isLoading}
                >
                  {isLoading ? (
                    <>
                      <Sparkles className="mr-2 h-5 w-5 animate-spin" />
                      Starting Workflow...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5" />
                      Start Decomposition
                    </>
                  )}
                </Button>

                {/* Info Box */}
                <div className="mt-4 p-3 rounded-lg bg-accent-blue/10 border border-accent-blue/20">
                  <div className="flex gap-2">
                    <AlertCircle className="h-4 w-4 text-accent-blue flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-text-secondary">
                      Workflow will execute through 4 stages: Extract, Analyze, Decompose, and
                      Validate. You can monitor progress in real-time.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </PageShell>
  );
}
