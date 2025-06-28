import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { NetworkNode, NetworkEdge } from '../../types/api';

interface RhizomaticGraphProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  onNodeClick?: (node: NetworkNode) => void;
  onNodeHover?: (node: NetworkNode | null) => void;
  height?: number;
  width?: number;
}

const RhizomaticGraph: React.FC<RhizomaticGraphProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeHover,
  height = 400,
  width = 800
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const container = svg.append('g');

    // Set up zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Define color scales for different trust tiers
    const getTrustColor = (tier: string) => {
      switch (tier) {
        case 'rooted': return '#10b981'; // green-500
        case 'growing': return '#3b82f6'; // blue-500
        case 'dormant': return '#f59e0b'; // amber-500
        case 'frayed': return '#ef4444'; // red-500
        default: return '#6b7280'; // gray-500
      }
    };

    const getNodeColor = (node: NetworkNode) => {
      if (node.type === 'user') return '#8b5cf6'; // purple-500
      if (node.type === 'goal') return '#ec4899'; // pink-500
      return getTrustColor(node.trust_tier || 'growing');
    };

    const getNodeSize = (node: NetworkNode) => {
      if (node.type === 'user') return 12;
      if (node.type === 'goal') return 8;
      return Math.max(6, (node.trust_score || 0) / 10); // Scale based on trust score
    };

    // Create simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => getNodeSize(d) + 2));

    // Create gradient definitions for enhanced visual effects
    const defs = svg.append('defs');
    
    // Gradient for user node
    const userGradient = defs.append('radialGradient')
      .attr('id', 'userGradient');
    userGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#c084fc')
      .attr('stop-opacity', 1);
    userGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#7c3aed')
      .attr('stop-opacity', 1);

    // Draw edges
    const link = container.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', '#374151')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: NetworkEdge) => Math.sqrt(d.strength || 1));

    // Draw nodes
    const node = container.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', getNodeSize)
      .attr('fill', (d: NetworkNode) => {
        if (d.type === 'user') return 'url(#userGradient)';
        return getNodeColor(d);
      })
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .style('filter', 'drop-shadow(0px 2px 4px rgba(0,0,0,0.3))')
      .call(d3.drag<SVGCircleElement, NetworkNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const labels = container.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text((d: NetworkNode) => d.name)
      .attr('font-size', 12)
      .attr('font-family', 'system-ui, sans-serif')
      .attr('fill', '#ffffff')
      .attr('text-anchor', 'middle')
      .attr('dy', (d: NetworkNode) => getNodeSize(d) + 16)
      .style('pointer-events', 'none')
      .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)');

    // Add trust score indicators for contacts
    const trustIndicators = container.append('g')
      .selectAll('text')
      .data(nodes.filter(n => n.type === 'contact' && n.trust_score))
      .join('text')
      .text((d: NetworkNode) => `${Math.round(d.trust_score || 0)}%`)
      .attr('font-size', 8)
      .attr('font-family', 'system-ui, sans-serif')
      .attr('fill', '#ffffff')
      .attr('text-anchor', 'middle')
      .attr('dy', 3)
      .style('pointer-events', 'none')
      .style('font-weight', 'bold')
      .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)');

    // Handle interactions
    node
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeClick?.(d);
      })
      .on('mouseover', (event, d) => {
        onNodeHover?.(d);
        
        // Highlight connected nodes and edges
        const connectedNodes = new Set();
        const connectedEdges = new Set();
        
        edges.forEach(edge => {
          if (edge.source === d.id) {
            connectedNodes.add(edge.target);
            connectedEdges.add(edge.id);
          }
          if (edge.target === d.id) {
            connectedNodes.add(edge.source);
            connectedEdges.add(edge.id);
          }
        });

        // Fade non-connected elements
        node.style('opacity', (n: NetworkNode) => 
          n.id === d.id || connectedNodes.has(n.id) ? 1 : 0.3
        );
        
        link.style('opacity', (e: NetworkEdge) => 
          connectedEdges.has(e.id) ? 1 : 0.1
        );
        
        labels.style('opacity', (n: NetworkNode) => 
          n.id === d.id || connectedNodes.has(n.id) ? 1 : 0.3
        );
      })
      .on('mouseout', () => {
        onNodeHover?.(null);
        
        // Reset opacity
        node.style('opacity', 1);
        link.style('opacity', 0.6);
        labels.style('opacity', 1);
      });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);

      trustIndicators
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };

  }, [nodes, edges, onNodeClick, onNodeHover, height, width]);

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-400">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700/50 flex items-center justify-center">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-lg font-medium">No network data available</p>
          <p className="text-sm">Add some contacts and goals to see your relationship network</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="bg-gray-900/20 rounded-lg border border-gray-700/30"
      >
      </svg>
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-gray-900/80 backdrop-blur-sm rounded-lg p-3 text-xs">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-gray-300">You</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-300">Rooted</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-gray-300">Growing</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <span className="text-gray-300">Dormant</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-300">Frayed</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-pink-500"></div>
            <span className="text-gray-300">Goals</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RhizomaticGraph;