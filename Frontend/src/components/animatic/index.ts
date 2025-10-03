// Animatic Component Library
// A comprehensive collection of animated UI components for the Janus Prop AI platform

export { AnimaticCard, AnimaticCardGrid } from './AnimaticCard';
export { AnimaticButton, AnimaticIconButton, AnimaticButtonGroup } from './AnimaticButton';
export { 
  AnimaticText, 
  AnimaticHeading, 
  AnimaticParagraph, 
  AnimaticCode, 
  AnimaticQuote 
} from './AnimaticText';

// Re-export hooks for convenience
export { 
  useAnimatic,
  useStaggeredAnimatic,
  useLoadingAnimatic,
  useScrollAnimatic,
  useHoverAnimatic,
  useFocusAnimatic,
  useClickAnimatic,
  usePageTransition,
  useResponsiveAnimatic
} from '@/hooks/useAnimatic';
