// src/components/Button.jsx
// Örnek 6.2: Kurumsal Buton Bileşeni — Varyantlı Yapı — Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR (ADR-001)

import PropTypes from 'prop-types';
import { cn } from '../utils/styleUtils';

/**
 * @param {object} props
 * @param {'primary'|'secondary'|'outline'|'ghost'} [props.variant='primary']
 * @param {'sm'|'md'|'lg'} [props.size='md']
 * @param {boolean} [props.isLoading=false]
 * @param {string} [props.className]
 * @param {React.ReactNode} props.children
 */
export const Button = ({
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-0 outline-none disabled:pointer-events-none disabled:opacity-50';

  const variants = {
    primary: 'bg-black text-white hover:bg-black/90 shadow-sm dark:bg-white dark:text-black dark:hover:bg-white/90',
    secondary: 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm',
    outline: 'border border-black/10 bg-transparent hover:bg-black/5 text-black dark:border-white/10 dark:hover:bg-white/5 dark:text-white',
    ghost: 'bg-transparent hover:bg-black/5 text-black dark:hover:bg-white/5 dark:text-white',
  };

  const sizes = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 py-2 text-sm',
    lg: 'h-12 px-8 text-base',
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
};

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'ghost']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  isLoading: PropTypes.bool,
  className: PropTypes.string,
  children: PropTypes.node,
  disabled: PropTypes.bool,
};
