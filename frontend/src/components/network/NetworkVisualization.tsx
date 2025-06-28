import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { NetworkGraph, Contact, TrustInsight } from '../../types/api';
import RhizomaticGraph from './RhizomaticGraph';
import TrustMetricsPanel from './TrustMetricsPanel';
import { Users, TrendingUp, Heart, AlertTriangle, RefreshCw } from 'lucide-react';

interface NetworkVisualizationProps {
  className?: string;
}

const NetworkVisualization: React.FC<NetworkVisualizationProps> = ({ className = '' }) => {
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [trustInsights, setTrustInsights] = useState<TrustInsight[]>([]);

  // Fetch network graph data
  const { data: networkData, isLoading: networkLoading, refetch: refetchNetwork } = useQuery({
    queryKey: ['network-graph'],
    queryFn: async (): Promise<NetworkGraph> => {
      const response = await fetch('/api/network/graph', {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('Failed to fetch network data');
      }
      const result = await response.json();
      return result.data || result;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch contacts data
  const { data: contacts, isLoading: contactsLoading } = useQuery({
    queryKey: ['contacts'],
    queryFn: async (): Promise<Contact[]> => {
      const response = await fetch('/api/contacts', {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('Failed to fetch contacts');
      }
      const result = await response.json();
      return result.contacts || result.data || [];
    }
  });

  // Fetch trust insights
  const { data: trustData, isLoading: trustLoading } = useQuery({
    queryKey: ['trust-insights'],
    queryFn: async (): Promise<TrustInsight[]> => {
      const response = await fetch('/api/trust/insights', {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('Failed to fetch trust insights');
      }
      const result = await response.json();
      return result.insights || result.data || [];
    }
  });

  // Enhanced network data with trust scores and contact information
  const enhancedNetworkData = React.useMemo(() => {
    if (!networkData || !contacts || !trustData) return null;

    // Create trust lookup map
    const trustMap = new Map<string, TrustInsight>();
    trustData.forEach(insight => {
      trustMap.set(insight.contact_id, insight);
    });

    // Create contact lookup map
    const contactMap = new Map<string, Contact>();
    contacts.forEach(contact => {
      contactMap.set(contact.id, contact);
    });

    // Enhance nodes with trust and contact data
    const enhancedNodes = networkData.nodes.map(node => {
      const trust = trustMap.get(node.id);
      const contact = contactMap.get(node.id);
      
      return {
        ...node,
        trust_score: trust?.trust_score || 0,
        trust_tier: trust?.trust_tier || 'growing',
        last_interaction: trust?.last_interaction || contact?.updated_at,
        tags: contact ? [contact.company, contact.title].filter(Boolean) : [],
        data: {
          ...node.data,
          contact,
          trust,
          email: contact?.email,
          company: contact?.company,
          title: contact?.title,
        }
      };
    });

    return {
      ...networkData,
      nodes: enhancedNodes
    };
  }, [networkData, contacts, trustData]);

  // Handle node click to show trust panel
  const handleNodeClick = (node: any) => {
    if (node.type === 'contact') {
      setSelectedContactId(node.id);
      const contact = contacts?.find(c => c.id === node.id);
      setSelectedContact(contact || null);
    }
  };

  // Handle node hover for tooltips
  const handleNodeHover = (node: any) => {
    // You can add tooltip logic here
  };

  const isLoading = networkLoading || contactsLoading || trustLoading;

  if (isLoading) {
    return (
      <div className={`glass-card p-8 ${className}`}>
        <div className="flex items-center justify-center space-x-3">
          <RefreshCw className="w-6 h-6 text-primary-400 animate-spin" />
          <span className="text-white">Loading network visualization...</span>
        </div>
      </div>
    );
  }

  if (!enhancedNetworkData) {
    return (
      <div className={`glass-card p-8 ${className}`}>
        <div className="text-center text-gray-400">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
          <h3 className="text-xl font-semibold text-white mb-2">No Network Data</h3>
          <p>Unable to load your relationship network. Try refreshing or check your connection.</p>
          <button
            onClick={() => refetchNetwork()}
            className="mt-4 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Network Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <div className="flex items-center space-x-3">
            <Users className="w-8 h-8 text-primary-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {enhancedNetworkData.stats.total_contacts}
              </div>
              <div className="text-sm text-gray-400">Total Contacts</div>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-green-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {enhancedNetworkData.stats.total_relationships}
              </div>
              <div className="text-sm text-gray-400">Connections</div>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center space-x-3">
            <Heart className="w-8 h-8 text-pink-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {trustData?.filter(t => t.trust_tier === 'rooted').length || 0}
              </div>
              <div className="text-sm text-gray-400">Trusted Connections</div>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-8 h-8 text-yellow-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {Math.round(enhancedNetworkData.stats.avg_connections * 10) / 10}
              </div>
              <div className="text-sm text-gray-400">Avg Connections</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Network Graph */}
        <div className="lg:col-span-2">
          <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Network Visualization</h3>
              <button
                onClick={() => refetchNetwork()}
                className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
                title="Refresh network data"
              >
                <RefreshCw className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            
            <RhizomaticGraph
              nodes={enhancedNetworkData.nodes}
              edges={enhancedNetworkData.edges}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              height={500}
            />
          </div>
        </div>

        {/* Trust Metrics Panel */}
        <div className="lg:col-span-1">
          <TrustMetricsPanel
            contactId={selectedContactId}
            contact={selectedContact}
            trustInsights={trustData || []}
            onClose={() => {
              setSelectedContactId(null);
              setSelectedContact(null);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default NetworkVisualization;