import React from 'react';

interface SkeletonLoaderProps {
  variant?: 'text' | 'avatar' | 'card' | 'stat' | 'button';
  size?: 'small' | 'medium' | 'large';
  width?: string;
  height?: string;
  className?: string;
  count?: number;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'text',
  size = 'medium',
  width,
  height,
  className = '',
  count = 1
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return `skeleton skeleton-text ${size}`;
      case 'avatar':
        return 'skeleton skeleton-avatar';
      case 'card':
        return 'skeleton skeleton-card';
      case 'stat':
        return 'skeleton skeleton-card h-32';
      case 'button':
        return 'skeleton h-10 w-24 rounded-lg';
      default:
        return 'skeleton skeleton-text';
    }
  };

  const getCustomStyle = () => {
    const style: React.CSSProperties = {};
    if (width) style.width = width;
    if (height) style.height = height;
    return style;
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`${getVariantClasses()} ${className}`}
          style={getCustomStyle()}
        />
      ))}
    </>
  );
};

// Skeleton components for specific use cases
export const StatCardSkeleton: React.FC = () => (
  <div className="glass-card p-6 backdrop-blur-sm border border-white/10 rounded-xl">
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <SkeletonLoader variant="text" size="small" width="60%" />
        <SkeletonLoader variant="text" size="large" width="40%" className="mt-3" />
        <SkeletonLoader variant="text" size="small" width="80%" className="mt-2" />
      </div>
      <SkeletonLoader variant="avatar" className="w-12 h-12" />
    </div>
  </div>
);

export const GoalCardSkeleton: React.FC = () => (
  <div className="glass-card p-6 border border-white/10 rounded-xl">
    <div className="flex items-start justify-between mb-4">
      <SkeletonLoader variant="avatar" className="w-10 h-10" />
      <SkeletonLoader variant="button" width="60px" height="24px" />
    </div>
    <SkeletonLoader variant="text" size="large" width="80%" />
    <SkeletonLoader variant="text" size="medium" width="100%" className="mt-2" />
    <SkeletonLoader variant="text" size="medium" width="60%" className="mt-1" />
    
    <div className="flex items-center justify-between mt-4">
      <SkeletonLoader variant="text" size="small" width="40%" />
      <SkeletonLoader variant="text" size="small" width="30%" />
    </div>
  </div>
);

export const ContactCardSkeleton: React.FC = () => (
  <div className="glass-card p-4 border border-white/10 rounded-xl">
    <div className="flex items-center space-x-3">
      <SkeletonLoader variant="avatar" />
      <div className="flex-1">
        <SkeletonLoader variant="text" size="medium" width="70%" />
        <SkeletonLoader variant="text" size="small" width="50%" className="mt-1" />
        <SkeletonLoader variant="text" size="small" width="40%" className="mt-1" />
      </div>
      <SkeletonLoader variant="button" width="80px" height="32px" />
    </div>
  </div>
);

export const AIInsightSkeleton: React.FC = () => (
  <div className="glass-card p-4 border border-white/10 rounded-xl">
    <div className="flex items-center space-x-2 mb-3">
      <SkeletonLoader variant="avatar" className="w-6 h-6" />
      <SkeletonLoader variant="text" size="medium" width="40%" />
    </div>
    <SkeletonLoader variant="text" size="medium" width="100%" />
    <SkeletonLoader variant="text" size="medium" width="90%" className="mt-1" />
    <SkeletonLoader variant="text" size="small" width="60%" className="mt-2" />
    
    <div className="flex space-x-2 mt-4">
      <SkeletonLoader variant="button" width="60px" height="28px" />
      <SkeletonLoader variant="button" width="80px" height="28px" />
    </div>
  </div>
);

export const DashboardSkeleton: React.FC = () => (
  <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
    <div className="container mx-auto px-6 py-8">
      <div className="mb-8">
        <SkeletonLoader variant="text" size="large" width="200px" />
        <SkeletonLoader variant="text" size="medium" width="300px" className="mt-2" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <SkeletonLoader variant="text" size="large" width="150px" className="mb-4" />
          <div className="space-y-3">
            <AIInsightSkeleton />
            <AIInsightSkeleton />
            <AIInsightSkeleton />
          </div>
        </div>
        
        <div>
          <SkeletonLoader variant="text" size="large" width="180px" className="mb-4" />
          <div className="space-y-3">
            <ContactCardSkeleton />
            <ContactCardSkeleton />
            <ContactCardSkeleton />
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default SkeletonLoader;