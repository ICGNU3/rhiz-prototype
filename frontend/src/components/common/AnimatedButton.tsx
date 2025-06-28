import React, { useState, useEffect } from 'react';
import { Loader2, Check, X } from 'lucide-react';

export type ButtonState = 'idle' | 'loading' | 'success' | 'error';

interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent) => void | Promise<void>;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  state?: ButtonState;
  loadingText?: string;
  successText?: string;
  errorText?: string;
  className?: string;
  resetDelay?: number; // Auto-reset after success/error (ms)
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'md',
  state: externalState,
  loadingText = 'Thinking...',
  successText = 'Got it!',
  errorText = 'Try again',
  className = '',
  resetDelay = 2000,
}) => {
  const [internalState, setInternalState] = useState<ButtonState>('idle');
  
  // Use external state if provided, otherwise use internal state
  const state = externalState ?? internalState;

  useEffect(() => {
    if ((state === 'success' || state === 'error') && resetDelay > 0) {
      const timer = setTimeout(() => {
        if (!externalState) {
          setInternalState('idle');
        }
      }, resetDelay);
      return () => clearTimeout(timer);
    }
  }, [state, resetDelay, externalState]);

  const handleClick = async (e: React.MouseEvent) => {
    if (disabled || state === 'loading' || !onClick) return;

    try {
      if (!externalState) {
        setInternalState('loading');
      }
      
      const result = onClick(e);
      
      if (result instanceof Promise) {
        await result;
      }
      
      if (!externalState) {
        setInternalState('success');
      }
    } catch (error) {
      console.error('Button action failed:', error);
      if (!externalState) {
        setInternalState('error');
      }
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white';
      case 'secondary':
        return 'glass-card border-white/20 text-gray-100 hover:border-white/30';
      case 'danger':
        return 'bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white';
      default:
        return 'glass-button-primary';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-2 text-sm';
      case 'lg':
        return 'px-8 py-4 text-lg';
      default:
        return 'px-6 py-3 text-base';
    }
  };

  const getStateClasses = () => {
    switch (state) {
      case 'loading':
        return 'button-thinking';
      case 'success':
        return 'button-success bg-gradient-to-r from-green-500 to-emerald-600';
      case 'error':
        return 'bg-gradient-to-r from-red-500 to-pink-600';
      default:
        return '';
    }
  };

  const getButtonContent = () => {
    switch (state) {
      case 'loading':
        return (
          <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>{loadingText}</span>
          </div>
        );
      case 'success':
        return (
          <div className="flex items-center space-x-2">
            <Check className="w-4 h-4" />
            <span>{successText}</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center space-x-2">
            <X className="w-4 h-4" />
            <span>{errorText}</span>
          </div>
        );
      default:
        return children;
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || state === 'loading'}
      className={`
        relative
        inline-flex
        items-center
        justify-center
        font-medium
        rounded-lg
        border
        transition-all
        duration-300
        transform
        hover:scale-105
        active:scale-95
        focus:outline-none
        focus:ring-2
        focus:ring-blue-500/50
        disabled:opacity-50
        disabled:cursor-not-allowed
        disabled:transform-none
        ${getVariantClasses()}
        ${getSizeClasses()}
        ${getStateClasses()}
        ${className}
      `}
    >
      {getButtonContent()}
    </button>
  );
};

export default AnimatedButton;