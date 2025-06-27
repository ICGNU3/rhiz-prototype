import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { NetworkNode, NetworkEdge } from '../../services/api';

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
  height = 600,
  width = 800,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Create responsive dimensions
    const container = svg.node()?.parentElement;
    const containerWidth = container?.clientWidth || width;
    const containerHeight = height;

    svg.attr('width', containerWidth).attr('height', containerHeight);

    // Create simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(containerWidth / 2, containerHeight / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create gradient definitions
    const defs = svg.append('defs');
    
    // Node gradients by type
    const nodeGradients = {
      contact: ['#4facfe', '#00f2fe'],
      goal: ['#8b5cf6', '#a855f7'],
      user: ['#ec4899', '#f97316'],
    };

    Object.entries(nodeGradients).forEach(([type, colors]) => {
      const gradient = defs
        .append('radialGradient')
        .attr('id', `gradient-${type}`)
        .attr('cx', '30%')
        .attr('cy', '30%');
      
      gradient.append('stop').attr('offset', '0%').attr('stop-color', colors[0]);
      gradient.append('stop').attr('offset', '100%').attr('stop-color', colors[1]);
    });

    // Edge gradient for connections
    const edgeGradient = defs
      .append('linearGradient')
      .attr('id', 'edge-gradient')
      .attr('gradientUnits', 'userSpaceOnUse');
    
    edgeGradient.append('stop').attr('offset', '0%').attr('stop-color', '#4facfe').attr('stop-opacity', 0.8);
    edgeGradient.append('stop').attr('offset', '100%').attr('stop-color', '#8b5cf6').attr('stop-opacity', 0.3);

    // Create container groups
    const linkGroup = svg.append('g').attr('class', 'links');
    const nodeGroup = svg.append('g').attr('class', 'nodes');

    // Create links
    const link = linkGroup
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('class', 'connection-line')
      .attr('stroke', 'url(#edge-gradient)')
      .attr('stroke-width', (d) => Math.max(1, d.strength * 3))
      .attr('stroke-opacity', 0.6);

    // Create nodes
    const node = nodeGroup
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', 'rhizomatic-node')
      .style('cursor', 'pointer')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
      );

    // Node circles with glassmorphism effect
    node
      .append('circle')
      .attr('r', (d) => {
        switch (d.type) {
          case 'user': return 25;
          case 'goal': return 20;
          case 'contact': return 15;
          default: return 15;
        }
      })
      .attr('fill', (d) => `url(#gradient-${d.type})`)
      .attr('stroke', 'rgba(255, 255, 255, 0.2)')
      .attr('stroke-width', 2)
      .attr('filter', 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3))');

    // Node labels
    node
      .append('text')
      .attr('dy', (d) => {
        switch (d.type) {
          case 'user': return 35;
          case 'goal': return 30;
          default: return 25;
        }
      })
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .attr('text-shadow', '0 1px 2px rgba(0, 0, 0, 0.8)')
      .text((d) => {
        const name = d.name || (d.data as any).title || (d.data as any).email || 'Unknown';
        return name.length > 15 ? name.substring(0, 15) + '...' : name;
      });

    // Node interaction handlers
    node
      .on('click', (event, d) => {
        setSelectedNode(selectedNode === d.id ? null : d.id);
        onNodeClick?.(d);
      })
      .on('mouseenter', (event, d) => {
        setHoveredNode(d.id);
        onNodeHover?.(d);
        
        // Highlight connected nodes and edges
        link
          .attr('stroke-opacity', (l) => 
            l.source === d.id || l.target === d.id ? 1 : 0.1
          )
          .attr('stroke-width', (l) =>
            l.source === d.id || l.target === d.id ? Math.max(2, l.strength * 4) : 1
          );
        
        node.select('circle')
          .attr('stroke-width', (n) => n.id === d.id ? 4 : 2)
          .attr('stroke', (n) => 
            n.id === d.id ? '#4facfe' : 'rgba(255, 255, 255, 0.2)'
          );
      })
      .on('mouseleave', () => {
        setHoveredNode(null);
        onNodeHover?.(null);
        
        // Reset highlights
        link
          .attr('stroke-opacity', 0.6)
          .attr('stroke-width', (d) => Math.max(1, d.strength * 3));
        
        node.select('circle')
          .attr('stroke-width', 2)
          .attr('stroke', 'rgba(255, 255, 255, 0.2)');
      });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
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
  }, [nodes, edges, width, height]);

  return (
    <div className="relative w-full">
      <svg
        ref={svgRef}
        className="w-full border border-dark-border rounded-xl bg-dark-card/20 backdrop-blur-sm"
        style={{ height }}
      />
      
      {/* Network Statistics Overlay */}
      <div className="absolute top-4 left-4 glass-card p-3 space-y-1">
        <div className="text-xs text-gray-400">Network Stats</div>
        <div className="text-sm text-white">
          <div>{nodes.length} nodes</div>
          <div>{edges.length} connections</div>
          <div className="text-xs text-gray-400 mt-1">
            {nodes.filter(n => n.type === 'contact').length} contacts
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute top-4 right-4 glass-card p-3 space-y-2">
        <div className="text-xs text-gray-400">Node Types</div>
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-primary-500 to-blue-400"></div>
            <span className="text-xs text-white">Contacts</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-purple-400"></div>
            <span className="text-xs text-white">Goals</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-pink-500 to-orange-400"></div>
            <span className="text-xs text-white">You</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RhizomaticGraph;