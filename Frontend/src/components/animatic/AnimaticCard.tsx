import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAnimatic } from '@/hooks/useAnimatic';
import { cn } from '@/lib/utils';

interface AnimaticCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  children?: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined' | 'glass';
  animation?: 'fade' | 'slide' | 'scale' | 'bounce';
  delay?: number;
  stagger?: number;
  hover?: boolean;
  clickable?: boolean;
}

export function AnimaticCard({
  title,
  description,
  children,
  variant = 'default',
  animation = 'fade',
  delay = 0,
  stagger = 0,
  hover = true,
  clickable = false,
  className,
  ...props
}: AnimaticCardProps) {
  const { ref, isVisible } = useAnimatic({
    threshold: 0.1,
    triggerOnce: true,
    delay: delay + stagger,
  });

  const animationClasses = {
    fade: 'animate-fade-in-up',
    slide: 'animate-slide-in-left',
    scale: 'animate-scale-in',
    bounce: 'animate-bounce',
  };

  const variantClasses = {
    default: 'bg-card border-border',
    elevated: 'bg-card border-border shadow-lg shadow-primary/5',
    outlined: 'bg-transparent border-2 border-primary/20',
    glass: 'bg-card/50 backdrop-blur-sm border-border/50',
  };

  return (
    <Card
      ref={ref}
      className={cn(
        'transition-all duration-500 ease-out',
        isVisible && animationClasses[animation],
        variantClasses[variant],
        hover && 'hover:shadow-xl hover:shadow-primary/10 hover:scale-105',
        clickable && 'cursor-pointer hover:border-primary/40',
        className
      )}
      style={{
        animationDelay: `${delay + stagger}ms`,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.95)',
      }}
      {...props}
    >
      {(title || description) && (
        <CardHeader>
          {title && (
            <CardTitle className="animatic-heading group-hover:text-primary transition-colors duration-300">
              {title}
            </CardTitle>
          )}
          {description && (
            <CardDescription className="animatic-text">
              {description}
            </CardDescription>
          )}
        </CardHeader>
      )}
      {children && (
        <CardContent className="animatic-text">
          {children}
        </CardContent>
      )}
    </Card>
  );
}

interface AnimaticCardGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  stagger?: number;
}

export function AnimaticCardGrid({
  children,
  columns = 3,
  gap = 'md',
  stagger = 100,
}: AnimaticCardGridProps) {
  const gapClasses = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5',
    6: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6',
  };

  return (
    <div className={cn(
      'grid',
      columnClasses[columns],
      gapClasses[gap],
      'w-full'
    )}>
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            stagger: index * stagger,
            ...child.props,
          });
        }
        return child;
      })}
    </div>
  );
}
