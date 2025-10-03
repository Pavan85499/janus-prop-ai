/**
 * Animatic Design System Utilities
 * Performance-optimized animation utilities for the Janus Prop AI platform
 */

import { useEffect, useRef, useCallback } from 'react';

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return function (this: unknown, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return function (this: unknown, ...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get optimal animation duration based on user preferences
 */
export function getOptimalDuration(baseDuration: number): number {
  return prefersReducedMotion() ? 0 : baseDuration;
}

/**
 * Check if element is in viewport
 */
export function isInViewport(element: HTMLElement, threshold: number = 0.1): boolean {
  const rect = element.getBoundingClientRect();
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;
  const windowWidth = window.innerWidth || document.documentElement.clientWidth;
  
  return (
    rect.top <= windowHeight * (1 - threshold) &&
    rect.bottom >= windowHeight * threshold &&
    rect.left <= windowWidth &&
    rect.right >= 0
  );
}

/**
 * Generate CSS custom properties for animations
 */
export function generateAnimationProperties(
  duration: number = 300,
  easing: string = 'cubic-bezier(0.4, 0, 0.2, 1)',
  delay: number = 0
): React.CSSProperties {
  return {
    '--animation-duration': `${duration}ms`,
    '--animation-easing': easing,
    '--animation-delay': `${delay}ms`,
  } as React.CSSProperties;
}

/**
 * Create intersection observer for performance-optimized animations
 */
export function createIntersectionObserver(
  callback: IntersectionObserverCallback,
  options: IntersectionObserverInit = {}
): IntersectionObserver {
  const defaultOptions: IntersectionObserverInit = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
    ...options,
  };

  return new IntersectionObserver(callback, defaultOptions);
}

/**
 * Animation frame scheduler for smooth animations
 */
export class AnimationScheduler {
  private rafId: number | null = null;
  private callbacks: Set<() => void> = new Set();

  add(callback: () => void): void {
    this.callbacks.add(callback);
    this.schedule();
  }

  remove(callback: () => void): void {
    this.callbacks.delete(callback);
  }

  private schedule(): void {
    if (this.rafId) return;
    
    this.rafId = requestAnimationFrame(() => {
      this.callbacks.forEach(callback => callback());
      this.rafId = null;
      
      if (this.callbacks.size > 0) {
        this.schedule();
      }
    });
  }

  cancel(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
}

/**
 * Global animation scheduler instance
 */
export const animationScheduler = new AnimationScheduler();

/**
 * Hook for managing animation performance
 */
export function useAnimationPerformance() {
  const schedulerRef = useRef(animationScheduler);
  
  const addAnimation = useCallback((callback: () => void) => {
    schedulerRef.current.add(callback);
  }, []);
  
  const removeAnimation = useCallback((callback: () => void) => {
    schedulerRef.current.remove(callback);
  }, []);
  
  useEffect(() => {
    return () => {
      schedulerRef.current.cancel();
    };
  }, []);
  
  return { addAnimation, removeAnimation };
}

/**
 * Generate staggered animation delays
 */
export function generateStaggerDelays(
  count: number,
  baseDelay: number = 0,
  staggerDelay: number = 100
): number[] {
  return Array.from({ length: count }, (_, index) => 
    baseDelay + (index * staggerDelay)
  );
}

/**
 * Calculate optimal stagger delay based on element count
 */
export function calculateOptimalStagger(count: number, maxDelay: number = 500): number {
  return Math.min(maxDelay / count, 100);
}

/**
 * Create CSS animation keyframes dynamically
 */
export function createKeyframes(name: string, keyframes: Record<string, React.CSSProperties>): string {
  const keyframeString = Object.entries(keyframes)
    .map(([percentage, styles]) => {
      const styleString = Object.entries(styles)
        .map(([property, value]) => `${property}: ${value}`)
        .join('; ');
      return `${percentage} { ${styleString} }`;
    })
    .join(' ');

  return `@keyframes ${name} { ${keyframeString} }`;
}

/**
 * Performance-optimized scroll handler
 */
export function createScrollHandler(
  callback: (scrollY: number, scrollProgress: number) => void,
  throttleMs: number = 16
) {
  let ticking = false;
  
  const throttledCallback = throttle(() => {
    const scrollY = window.scrollY;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollProgress = Math.min(scrollY / scrollHeight, 1);
    
    callback(scrollY, scrollProgress);
    ticking = false;
  }, throttleMs);
  
  return () => {
    if (!ticking) {
      requestAnimationFrame(throttledCallback);
      ticking = true;
    }
  };
}

/**
 * Check if device supports hardware acceleration
 */
export function supportsHardwareAcceleration(): boolean {
  if (typeof window === 'undefined') return false;
  
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  
  return !!gl;
}

/**
 * Get optimal transform properties for hardware acceleration
 */
export function getHardwareAcceleratedTransform(
  x: number = 0,
  y: number = 0,
  scale: number = 1,
  rotate: number = 0
): React.CSSProperties {
  return {
    transform: `translate3d(${x}px, ${y}px, 0) scale(${scale}) rotate(${rotate}deg)`,
    willChange: 'transform',
    backfaceVisibility: 'hidden',
    perspective: '1000px',
  };
}

/**
 * Memory-efficient animation cleanup
 */
export function createAnimationCleanup() {
  const cleanupFunctions: (() => void)[] = [];
  
  return {
    add: (cleanup: () => void) => cleanupFunctions.push(cleanup),
    cleanup: () => {
      cleanupFunctions.forEach(cleanup => cleanup());
      cleanupFunctions.length = 0;
    },
  };
}

/**
 * Responsive animation breakpoints
 */
export const ANIMATION_BREAKPOINTS = {
  mobile: 640,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
} as const;

/**
 * Get animation settings based on screen size
 */
export function getResponsiveAnimationSettings(screenWidth: number) {
  if (screenWidth < ANIMATION_BREAKPOINTS.mobile) {
    return {
      duration: 200,
      stagger: 50,
      threshold: 0.2,
    };
  } else if (screenWidth < ANIMATION_BREAKPOINTS.tablet) {
    return {
      duration: 300,
      stagger: 75,
      threshold: 0.15,
    };
  } else if (screenWidth < ANIMATION_BREAKPOINTS.desktop) {
    return {
      duration: 400,
      stagger: 100,
      threshold: 0.1,
    };
  } else {
    return {
      duration: 500,
      stagger: 150,
      threshold: 0.05,
    };
  }
}
