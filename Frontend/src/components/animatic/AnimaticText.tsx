import React from 'react';
import { useAnimatic } from '@/hooks/useAnimatic';
import { cn } from '@/lib/utils';

interface AnimaticTextProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'div';
  animation?: 'fade' | 'slide' | 'scale' | 'typewriter' | 'reveal';
  delay?: number;
  stagger?: number;
  duration?: number;
  children: React.ReactNode;
}

export function AnimaticText({
  as: Component = 'p',
  animation = 'fade',
  delay = 0,
  stagger = 0,
  duration = 600,
  className,
  children,
  ...props
}: AnimaticTextProps) {
  const { ref, isVisible } = useAnimatic({
    threshold: 0.1,
    triggerOnce: true,
    delay: delay + stagger,
  });

  const animationClasses = {
    fade: 'animate-fade-in-up',
    slide: 'animate-slide-in-left',
    scale: 'animate-scale-in',
    typewriter: 'animate-typewriter',
    reveal: 'animate-reveal',
  };

  return (
    <Component
      ref={ref}
      className={cn(
        'transition-all duration-500 ease-out',
        isVisible && animationClasses[animation],
        className
      )}
      style={{
        animationDelay: `${delay + stagger}ms`,
        animationDuration: `${duration}ms`,
        opacity: isVisible ? 1 : 0,
        transform: isVisible 
          ? 'translateY(0) scale(1)' 
          : 'translateY(20px) scale(0.95)',
      }}
      {...props}
    >
      {children}
    </Component>
  );
}

interface AnimaticHeadingProps extends Omit<AnimaticTextProps, 'as'> {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  gradient?: boolean;
}

export function AnimaticHeading({
  level = 1,
  gradient = false,
  className,
  children,
  ...props
}: AnimaticHeadingProps) {
  const Component = `h${level}` as keyof JSX.IntrinsicElements;
  
  const sizeClasses = {
    1: 'text-4xl sm:text-5xl lg:text-6xl',
    2: 'text-3xl sm:text-4xl lg:text-5xl',
    3: 'text-2xl sm:text-3xl lg:text-4xl',
    4: 'text-xl sm:text-2xl lg:text-3xl',
    5: 'text-lg sm:text-xl lg:text-2xl',
    6: 'text-base sm:text-lg lg:text-xl',
  };

  return (
    <AnimaticText
      as={Component}
      className={cn(
        'font-display font-semibold leading-tight tracking-tight',
        sizeClasses[level],
        gradient && 'bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent',
        className
      )}
      {...props}
    >
      {children}
    </AnimaticText>
  );
}

interface AnimaticParagraphProps extends Omit<AnimaticTextProps, 'as'> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  weight?: 'light' | 'normal' | 'medium' | 'semibold';
}

export function AnimaticParagraph({
  size = 'md',
  weight = 'normal',
  className,
  children,
  ...props
}: AnimaticParagraphProps) {
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };

  const weightClasses = {
    light: 'font-light',
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
  };

  return (
    <AnimaticText
      as="p"
      className={cn(
        'animatic-text leading-relaxed',
        sizeClasses[size],
        weightClasses[weight],
        className
      )}
      {...props}
    >
      {children}
    </AnimaticText>
  );
}

interface AnimaticCodeProps extends Omit<AnimaticTextProps, 'as'> {
  language?: string;
  inline?: boolean;
}

export function AnimaticCode({
  language,
  inline = false,
  className,
  children,
  ...props
}: AnimaticCodeProps) {
  const Component = inline ? 'code' : 'pre';
  
  return (
    <AnimaticText
      as={Component}
      className={cn(
        inline 
          ? 'px-2 py-1 bg-muted rounded text-sm font-mono'
          : 'p-4 bg-muted rounded-lg text-sm font-mono overflow-x-auto',
        className
      )}
      {...props}
    >
      {children}
    </AnimaticText>
  );
}

interface AnimaticQuoteProps extends Omit<AnimaticTextProps, 'as'> {
  author?: string;
  source?: string;
}

export function AnimaticQuote({
  author,
  source,
  className,
  children,
  ...props
}: AnimaticQuoteProps) {
  return (
    <blockquote className={cn('border-l-4 border-primary pl-6 py-4', className)}>
      <AnimaticText
        as="p"
        className="text-lg italic text-muted-foreground mb-4"
        {...props}
      >
        "{children}"
      </AnimaticText>
      {(author || source) && (
        <footer className="text-sm text-muted-foreground">
          {author && <cite className="font-semibold">{author}</cite>}
          {author && source && <span> — </span>}
          {source && <cite>{source}</cite>}
        </footer>
      )}
    </blockquote>
  );
}
