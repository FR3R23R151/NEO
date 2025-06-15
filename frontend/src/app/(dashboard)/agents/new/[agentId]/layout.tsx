import { Metadata } from 'next';
import { redirect } from 'next/navigation';
import { isFlagEnabled } from '@/lib/feature-flags';

export const metadata: Metadata = {
  title: 'Create Agent | Kortix NEO',
  description: 'Interactive agent playground powered by Kortix NEO',
  openGraph: {
    title: 'Agent Playground | Kortix NEO',
    description: 'Interactive agent playground powered by Kortix NEO',
    type: 'website',
  },
};

export default async function NewAgentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const agentPlaygroundEnabled = await isFlagEnabled('custom_agents');
  if (!agentPlaygroundEnabled) {
    redirect('/dashboard');
  }
  return <>{children}</>;
}
