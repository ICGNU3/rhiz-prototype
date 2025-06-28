import React from 'react';
import NetworkVisualization from '../components/network/NetworkVisualization';
import { Share2, MapPin, Target, TrendingUp } from 'lucide-react';

const NetworkPage: React.FC = () => {
  return (
    <>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        {/* Background Elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500 rounded-full opacity-10 blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full opacity-10 blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-pink-500 rounded-full opacity-5 blur-3xl"></div>
        </div>

        <div className="relative z-10 container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Share2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Network Visualization
                </h1>
                <p className="text-gray-400">
                  Explore your relationship network with interactive trust insights
                </p>
              </div>
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass-card p-6">
              <div className="flex items-center space-x-3">
                <MapPin className="w-8 h-8 text-blue-400" />
                <div>
                  <h3 className="text-lg font-semibold text-white">Interactive Map</h3>
                  <p className="text-sm text-gray-400">
                    Visualize relationships as an interactive network graph
                  </p>
                </div>
              </div>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center space-x-3">
                <Target className="w-8 h-8 text-green-400" />
                <div>
                  <h3 className="text-lg font-semibold text-white">Trust Insights</h3>
                  <p className="text-sm text-gray-400">
                    Click on contacts to see detailed trust metrics and analytics
                  </p>
                </div>
              </div>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center space-x-3">
                <TrendingUp className="w-8 h-8 text-purple-400" />
                <div>
                  <h3 className="text-lg font-semibold text-white">Real-time Data</h3>
                  <p className="text-sm text-gray-400">
                    Live updates based on your latest interactions and goals
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Network Visualization */}
          <div className="space-y-6">
            <NetworkVisualization className="w-full" />
          </div>

          {/* Usage Instructions */}
          <div className="mt-8 glass-card p-6">
            <h3 className="text-xl font-semibold text-white mb-4">How to Use</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mt-1">
                    <span className="text-blue-400 font-semibold text-sm">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">Explore Connections</h4>
                    <p className="text-sm text-gray-400">
                      Pan, zoom, and drag nodes to explore your relationship network. Each node represents a contact, goal, or you.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center mt-1">
                    <span className="text-green-400 font-semibold text-sm">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">View Trust Tiers</h4>
                    <p className="text-sm text-gray-400">
                      Contact colors indicate trust levels: Green (Rooted), Blue (Growing), Yellow (Dormant), Red (Frayed).
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center mt-1">
                    <span className="text-purple-400 font-semibold text-sm">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">Click for Details</h4>
                    <p className="text-sm text-gray-400">
                      Click on any contact to open the Trust Metrics panel with detailed analytics and insights.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-pink-500/20 rounded-lg flex items-center justify-center mt-1">
                    <span className="text-pink-400 font-semibold text-sm">4</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">Hover for Highlights</h4>
                    <p className="text-sm text-gray-400">
                      Hover over nodes to highlight connected relationships and see immediate context.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NetworkPage;