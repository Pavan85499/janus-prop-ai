import { useEffect, useRef, useState } from 'react';

interface UseAnimaticOptions {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
  delay?: number;
}

interface UseAnimaticReturn {
  ref: React.RefObject<HTMLElement>;
  isVisible: boolean;
  hasAnimated: boolean;
}

/**
 * Custom hook for managing animatic entrance animations
 * Uses Intersection Observer API for performance-optimized animations
 */
export function useAnimatic(options: UseAnimaticOptions = {}): UseAnimaticReturn {
  const {
    threshold = 0.1,
    rootMargin = '0px 0px -50px 0px',
    triggerOnce = true,
    delay = 0
  } = options;

  const ref = useRef<HTMLElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (triggerOnce) {
            setHasAnimated(true);
          }
        } else if (!triggerOnce) {
          setIsVisible(false);
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [threshold, rootMargin, triggerOnce]);

  useEffect(() => {
    if (isVisible && delay > 0) {
      const timer = setTimeout(() => {
        setHasAnimated(true);
      }, delay);
      return () => clearTimeout(timer);
    } else if (isVisible) {
      setHasAnimated(true);
    }
  }, [isVisible, delay]);

  return { ref, isVisible, hasAnimated };
}

/**
 * Hook for staggered animations in lists
 */
export function useStaggeredAnimatic(
  itemCount: number,
  staggerDelay: number = 100,
  options: UseAnimaticOptions = {}
) {
  const { ref, isVisible } = useAnimatic(options);
  const [animatedItems, setAnimatedItems] = useState<boolean[]>(
    new Array(itemCount).fill(false)
  );

  useEffect(() => {
    if (isVisible) {
      animatedItems.forEach((_, index) => {
        setTimeout(() => {
          setAnimatedItems(prev => {
            const newState = [...prev];
            newState[index] = true;
            return newState;
          });
        }, index * staggerDelay);
      });
    }
  }, [isVisible, itemCount, staggerDelay]);

  return { ref, isVisible, animatedItems };
}

/**
 * Hook for managing loading states with animations
 */
export function useLoadingAnimatic(loading: boolean, duration: number = 1000) {
  const [showLoading, setShowLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (loading) {
      setShowLoading(true);
      setShowContent(false);
    } else {
      setShowLoading(false);
      setTimeout(() => {
        setShowContent(true);
      }, 200);
    }
  }, [loading]);

  return { showLoading, showContent };
}

/**
 * Hook for managing scroll-based animations
 */
export function useScrollAnimatic(threshold: number = 0.5) {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = Math.min(scrollTop / docHeight, 1);
      
      setScrollProgress(progress);
      setIsScrolled(scrollTop > threshold * window.innerHeight);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [threshold]);

  return { scrollProgress, isScrolled };
}

/**
 * Hook for managing hover animations
 */
export function useHoverAnimatic() {
  const [isHovered, setIsHovered] = useState(false);
  const [hoverCount, setHoverCount] = useState(0);

  const handleMouseEnter = () => {
    setIsHovered(true);
    setHoverCount(prev => prev + 1);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return {
    isHovered,
    hoverCount,
    handleMouseEnter,
    handleMouseLeave,
  };
}

/**
 * Hook for managing focus animations
 */
export function useFocusAnimatic() {
  const [isFocused, setIsFocused] = useState(false);

  const handleFocus = () => setIsFocused(true);
  const handleBlur = () => setIsFocused(false);

  return {
    isFocused,
    handleFocus,
    handleBlur,
  };
}

/**
 * Hook for managing click animations
 */
export function useClickAnimatic() {
  const [isClicked, setIsClicked] = useState(false);
  const [clickCount, setClickCount] = useState(0);

  const handleClick = () => {
    setIsClicked(true);
    setClickCount(prev => prev + 1);
    
    setTimeout(() => {
      setIsClicked(false);
    }, 150);
  };

  return {
    isClicked,
    clickCount,
    handleClick,
  };
}

/**
 * Hook for managing page transitions
 */
export function usePageTransition() {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState<'in' | 'out'>('in');

  const startTransition = (direction: 'in' | 'out' = 'out') => {
    setTransitionDirection(direction);
    setIsTransitioning(true);
    
    setTimeout(() => {
      setIsTransitioning(false);
    }, 300);
  };

  return {
    isTransitioning,
    transitionDirection,
    startTransition,
  };
}

/**
 * Hook for managing responsive animations
 */
export function useResponsiveAnimatic() {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      const width = window.innerWidth;
      setIsMobile(width < 640);
      setIsTablet(width >= 640 && width < 1024);
      setIsDesktop(width >= 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  return {
    isMobile,
    isTablet,
    isDesktop,
  };
}
