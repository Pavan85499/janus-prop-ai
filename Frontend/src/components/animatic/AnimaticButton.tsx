import React from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { useClickAnimatic, useHoverAnimatic } from '@/hooks/useAnimatic';
import { cn } from '@/lib/utils';

interface AnimaticButtonProps extends ButtonProps {
  animation?: 'bounce' | 'pulse' | 'wiggle' | 'glow' | 'shimmer';
  loading?: boolean;
  success?: boolean;
  error?: boolean;
  ripple?: boolean;
}

export function AnimaticButton({
  animation = 'bounce',
  loading = false,
  success = false,
  error = false,
  ripple = true,
  className,
  children,
  onClick,
  ...props
}: AnimaticButtonProps) {
  const { isClicked, clickCount, handleClick } = useClickAnimatic();
  const { isHovered, handleMouseEnter, handleMouseLeave } = useHoverAnimatic();

  const animationClasses = {
    bounce: 'hover:animate-bounce',
    pulse: 'hover:animate-pulse',
    wiggle: 'hover:animate-wiggle',
    glow: 'hover:animate-glow',
    shimmer: 'hover:animate-shimmer',
  };

  const stateClasses = {
    loading: 'opacity-75 cursor-not-allowed',
    success: 'bg-success text-success-foreground hover:bg-success/90',
    error: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
  };

  const handleClickWithAnimation = (e: React.MouseEvent<HTMLButtonElement>) => {
    handleClick();
    onClick?.(e);
  };

  return (
    <Button
      className={cn(
        'relative overflow-hidden transition-all duration-300 ease-out',
        animationClasses[animation],
        loading && stateClasses.loading,
        success && stateClasses.success,
        error && stateClasses.error,
        isClicked && 'scale-95',
        isHovered && 'scale-105',
        className
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClickWithAnimation}
      disabled={loading}
      {...props}
    >
      {ripple && isClicked && (
        <div className="absolute inset-0 bg-white/20 rounded-full animate-ping" />
      )}
      
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      <span className={cn(
        'transition-opacity duration-200',
        loading && 'opacity-0'
      )}>
        {children}
      </span>
    </Button>
  );
}

interface AnimaticIconButtonProps extends Omit<AnimaticButtonProps, 'children'> {
  icon: React.ReactNode;
  label?: string;
}

export function AnimaticIconButton({
  icon,
  label,
  ...props
}: AnimaticIconButtonProps) {
  return (
    <AnimaticButton
      size="icon"
      aria-label={label}
      {...props}
    >
      {icon}
    </AnimaticButton>
  );
}

interface AnimaticButtonGroupProps {
  children: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outlined' | 'ghost';
}

export function AnimaticButtonGroup({
  children,
  orientation = 'horizontal',
  spacing = 'md',
  variant = 'default',
}: AnimaticButtonGroupProps) {
  const orientationClasses = {
    horizontal: 'flex-row',
    vertical: 'flex-col',
  };

  const spacingClasses = {
    sm: 'gap-1',
    md: 'gap-2',
    lg: 'gap-4',
  };

  const variantClasses = {
    default: 'p-1 bg-card rounded-lg border',
    outlined: 'p-1 bg-transparent rounded-lg border-2 border-border',
    ghost: 'p-1 bg-transparent rounded-lg',
  };

  return (
    <div className={cn(
      'flex',
      orientationClasses[orientation],
      spacingClasses[spacing],
      variantClasses[variant],
      'transition-all duration-300'
    )}>
      {children}
    </div>
  );
}
