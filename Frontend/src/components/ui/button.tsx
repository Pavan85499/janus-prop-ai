import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  `inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium 
   ring-offset-background transition-all duration-300 ease-out focus-visible:outline-none 
   focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 
   disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0
   relative overflow-hidden hover:scale-105 active:scale-95 transform-gpu`,
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/25",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-lg shadow-destructive/25",
        outline:
          `border border-input bg-background hover:bg-accent hover:text-accent-foreground 
           hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10`,
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-md",
        ghost: "hover:bg-accent hover:text-accent-foreground hover:scale-105",
        link: "text-primary underline-offset-4 hover:underline hover:text-primary/80",
        animatic: `bg-gradient-primary text-primary-foreground hover:bg-primary/90 
                  shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/40
                  before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent 
                  before:via-white/10 before:to-transparent before:translate-x-[-100%] 
                  hover:before:translate-x-[100%] before:transition-transform before:duration-500`,
        success: "bg-success text-success-foreground hover:bg-success/90 shadow-lg shadow-success/25",
        warning: "bg-warning text-warning-foreground hover:bg-warning/90 shadow-lg shadow-warning/25",
        ice: "bg-ice text-ice-foreground hover:bg-ice/90 shadow-lg shadow-ice/25",
        gold: "bg-gold text-gold-foreground hover:bg-gold/90 shadow-lg shadow-gold/25",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-xs",
        lg: "h-11 rounded-md px-8 text-base",
        xl: "h-12 rounded-lg px-10 text-lg",
        icon: "h-10 w-10",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
