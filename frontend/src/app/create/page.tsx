import AssignmentForm from '@/components/AssignmentForm';

export default function CreatePage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Create New Assessment</h1>
        <p className="text-slate-600">Fill in the details below to generate an AI-powered question paper.</p>
      </div>
      <AssignmentForm />
    </div>
  );
}
