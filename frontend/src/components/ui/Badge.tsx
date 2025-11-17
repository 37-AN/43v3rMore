import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default';
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className = '', variant = 'default', children, ...props }, ref) => {
    const variantClasses = {
      success: 'badge-success',
      warning: 'badge-warning',
      error: 'badge-error',
      info: 'badge-info',
      default: 'badge bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
    };

    return (
      <span
        ref={ref}
        className={`${variantClasses[variant]} ${className}`}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export default Badge;
