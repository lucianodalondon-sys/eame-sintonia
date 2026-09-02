/* @ds-bundle: {"format":4,"namespace":"ADAMADesignSystem","components":[{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"ProductIcon","sourcePath":"components/core/ProductIcon.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"}],"sourceHashes":{"components/core/Badge.jsx":"cd5c55b2d577","components/core/Button.jsx":"a9198a47c423","components/core/Card.jsx":"c793431e71bf","components/core/ProductIcon.jsx":"75ffb109557b","components/core/Tag.jsx":"b2d7b85a5308"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.ADAMADesignSystem = window.ADAMADesignSystem || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const PRODUCT_CONFIG = {
  'crop-enhancement': {
    label: 'Crop Enhancement',
    bg: '#f89e18',
    text: '#fff',
    dot: '#f89e18'
  },
  'weed-control': {
    label: 'Weed Control',
    bg: '#7db41e',
    text: '#fff',
    dot: '#7db41e'
  },
  'disease-control': {
    label: 'Disease Control',
    bg: '#00a0df',
    text: '#fff',
    dot: '#00a0df'
  },
  'pest-control': {
    label: 'Pest Control',
    bg: '#9d1d96',
    text: '#fff',
    dot: '#9d1d96'
  },
  'corporate-green': {
    label: 'Corporate',
    bg: '#009845',
    text: '#fff',
    dot: '#009845'
  },
  earth: {
    label: 'Earth',
    bg: '#978b87',
    text: '#fff',
    dot: '#978b87'
  },
  success: {
    label: 'Success',
    bg: '#e8f7ee',
    text: '#00783f',
    dot: '#009845'
  },
  warning: {
    label: 'Warning',
    bg: '#fef6e4',
    text: '#b37512',
    dot: '#f89e18'
  },
  info: {
    label: 'Info',
    bg: '#e3f5fc',
    text: '#00698f',
    dot: '#00a0df'
  },
  error: {
    label: 'Error',
    bg: '#fde8fd',
    text: '#831880',
    dot: '#9d1d96'
  },
  neutral: {
    label: 'Neutral',
    bg: '#f4f2f2',
    text: '#5f504d',
    dot: '#978b87'
  }
};
function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  outline = false,
  style: extraStyle,
  ...props
}) {
  const c = PRODUCT_CONFIG[variant] || PRODUCT_CONFIG.neutral;
  const sizes = {
    sm: {
      fontSize: '11px',
      padding: '2px 8px',
      height: '20px',
      dotSize: '6px'
    },
    md: {
      fontSize: '12px',
      padding: '3px 10px',
      height: '24px',
      dotSize: '7px'
    },
    lg: {
      fontSize: '13px',
      padding: '4px 12px',
      height: '28px',
      dotSize: '8px'
    }
  };
  const s = sizes[size] || sizes.md;
  const style = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '5px',
    fontFamily: 'var(--font-primary)',
    fontWeight: 600,
    fontSize: s.fontSize,
    letterSpacing: '0.02em',
    lineHeight: 1,
    height: s.height,
    padding: s.padding,
    borderRadius: 'var(--radius-badge)',
    background: outline ? 'transparent' : c.bg,
    color: outline ? c.dot : c.text,
    border: outline ? `1.5px solid ${c.dot}` : 'none',
    whiteSpace: 'nowrap',
    ...extraStyle
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: style
  }, props), dot && /*#__PURE__*/React.createElement("span", {
    style: {
      width: s.dotSize,
      height: s.dotSize,
      borderRadius: '50%',
      background: outline ? c.dot : c.text,
      flexShrink: 0
    }
  }), children || c.label);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const COLORS = {
  corporate: {
    bg: '#009845',
    dark: '#00783f',
    text: '#fff',
    border: '#009845'
  },
  'crop-enhancement': {
    bg: '#f89e18',
    dark: '#d9890e',
    text: '#fff',
    border: '#f89e18'
  },
  'weed-control': {
    bg: '#7db41e',
    dark: '#699918',
    text: '#fff',
    border: '#7db41e'
  },
  'disease-control': {
    bg: '#00a0df',
    dark: '#0087be',
    text: '#fff',
    border: '#00a0df'
  },
  'pest-control': {
    bg: '#9d1d96',
    text: '#fff',
    dark: '#831880',
    border: '#9d1d96'
  },
  earth: {
    bg: '#978b87',
    dark: '#7a706c',
    text: '#fff',
    border: '#978b87'
  },
  white: {
    bg: '#ffffff',
    dark: '#f4f2f2',
    text: '#009845',
    border: '#009845'
  }
};
const SIZES = {
  sm: {
    padding: '6px 16px',
    fontSize: '13px',
    height: '32px',
    iconSize: '14px',
    gap: '6px'
  },
  md: {
    padding: '9px 22px',
    fontSize: '15px',
    height: '40px',
    iconSize: '16px',
    gap: '8px'
  },
  lg: {
    padding: '12px 28px',
    fontSize: '17px',
    height: '48px',
    iconSize: '18px',
    gap: '10px'
  }
};
function Button({
  children,
  variant = 'primary',
  size = 'md',
  color = 'corporate',
  disabled = false,
  fullWidth = false,
  iconLeft,
  iconRight,
  onClick,
  type = 'button',
  style: extraStyle,
  ...props
}) {
  const c = COLORS[color] || COLORS.corporate;
  const s = SIZES[size] || SIZES.md;
  const [hovered, setHovered] = React.useState(false);
  const base = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: s.gap,
    fontFamily: 'var(--font-primary)',
    fontWeight: 600,
    fontSize: s.fontSize,
    letterSpacing: '0.01em',
    lineHeight: 1,
    height: s.height,
    padding: s.padding,
    borderRadius: 'var(--radius-button)',
    border: '2px solid transparent',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast)',
    opacity: disabled ? 0.5 : 1,
    width: fullWidth ? '100%' : undefined,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    ...extraStyle
  };
  let variantStyle = {};
  if (variant === 'primary') {
    variantStyle = {
      background: hovered && !disabled ? c.dark : c.bg,
      color: c.text,
      borderColor: hovered && !disabled ? c.dark : c.bg,
      boxShadow: hovered && !disabled ? 'var(--shadow-md)' : 'none'
    };
  } else if (variant === 'outline') {
    variantStyle = {
      background: hovered && !disabled ? c.bg + '12' : 'transparent',
      color: c.bg,
      borderColor: c.bg
    };
  } else if (variant === 'ghost') {
    variantStyle = {
      background: hovered && !disabled ? c.bg + '12' : 'transparent',
      color: c.bg,
      borderColor: 'transparent'
    };
  } else if (variant === 'secondary') {
    variantStyle = {
      background: hovered && !disabled ? '#e5e1e0' : '#f4f2f2',
      color: '#5f504d',
      borderColor: hovered && !disabled ? '#cbc5c3' : 'transparent'
    };
  }
  return /*#__PURE__*/React.createElement("button", _extends({
    type: type,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHovered(true),
    onMouseLeave: () => setHovered(false),
    style: {
      ...base,
      ...variantStyle
    }
  }, props), iconLeft && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: s.iconSize,
      display: 'flex',
      alignItems: 'center'
    }
  }, iconLeft), children, iconRight && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: s.iconSize,
      display: 'flex',
      alignItems: 'center'
    }
  }, iconRight));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Card({
  children,
  variant = 'default',
  padding = 'md',
  color,
  hoverable = false,
  style: extraStyle,
  ...props
}) {
  const [hovered, setHovered] = React.useState(false);
  const paddings = {
    none: '0',
    sm: 'var(--space-4)',
    md: 'var(--space-6)',
    lg: 'var(--space-8)',
    xl: 'var(--space-12)'
  };

  // Color-tinted card backgrounds (Earth tints or product colors)
  const colorMap = {
    'crop-enhancement': {
      bg: '#fff8ed',
      border: '#f89e1820'
    },
    'weed-control': {
      bg: '#f5faed',
      border: '#7db41e20'
    },
    'disease-control': {
      bg: '#e8f7fd',
      border: '#00a0df20'
    },
    'pest-control': {
      bg: '#f8edf8',
      border: '#9d1d9620'
    },
    'corporate-green': {
      bg: '#e8f5ee',
      border: '#00984520'
    },
    earth: {
      bg: '#f4f2f2',
      border: '#978b8720'
    }
  };
  const variantStyles = {
    default: {
      background: '#fff',
      border: '1px solid var(--color-border-subtle)',
      boxShadow: hovered && hoverable ? 'var(--shadow-lg)' : 'var(--shadow-sm)'
    },
    elevated: {
      background: '#fff',
      border: 'none',
      boxShadow: hovered && hoverable ? 'var(--shadow-xl)' : 'var(--shadow-md)'
    },
    outline: {
      background: '#fff',
      border: '2px solid var(--color-border)',
      boxShadow: 'none'
    },
    filled: {
      background: 'var(--color-surface-muted)',
      border: 'none',
      boxShadow: 'none'
    }
  };
  const colorStyle = color && colorMap[color] ? {
    background: colorMap[color].bg,
    border: `1px solid ${colorMap[color].border}`
  } : {};
  return /*#__PURE__*/React.createElement("div", _extends({
    onMouseEnter: () => hoverable && setHovered(true),
    onMouseLeave: () => hoverable && setHovered(false),
    style: {
      borderRadius: 'var(--radius-card)',
      padding: paddings[padding] || paddings.md,
      transition: 'box-shadow var(--transition-base), transform var(--transition-base)',
      transform: hovered && hoverable ? 'translateY(-2px)' : 'none',
      ...(variantStyles[variant] || variantStyles.default),
      ...colorStyle,
      ...extraStyle
    }
  }, props), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/ProductIcon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * ProductIcon — displays the circular product-category icon with colored background
 * Used for visually communicating which ADAMA product category a piece of content belongs to.
 */
const CATEGORIES = {
  'crop-enhancement': {
    bg: '#f89e18',
    label: 'Crop Enhancement',
    symbol: '◎'
  },
  'weed-control': {
    bg: '#7db41e',
    label: 'Weed Control',
    symbol: '⟁'
  },
  'disease-control': {
    bg: '#00a0df',
    label: 'Disease Control',
    symbol: '◉'
  },
  'pest-control': {
    bg: '#9d1d96',
    label: 'Pest Control',
    symbol: '✳'
  },
  corporate: {
    bg: '#009845',
    label: 'ADAMA',
    symbol: 'A'
  }
};
function ProductIcon({
  category = 'corporate',
  size = 48,
  showLabel = false,
  style: extraStyle,
  ...props
}) {
  const c = CATEGORIES[category] || CATEGORIES.corporate;
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'inline-flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '6px',
      ...extraStyle
    }
  }, props), /*#__PURE__*/React.createElement("div", {
    style: {
      width: size,
      height: size,
      borderRadius: '50%',
      background: c.bg,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#fff',
      fontSize: size * 0.4,
      fontFamily: 'var(--font-primary)',
      fontWeight: 700,
      flexShrink: 0
    }
  }, c.symbol), showLabel && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-primary)',
      fontSize: '11px',
      fontWeight: 600,
      color: 'var(--color-text-body)',
      textAlign: 'center',
      maxWidth: size + 16,
      lineHeight: 1.3
    }
  }, c.label));
}
Object.assign(__ds_scope, { ProductIcon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/ProductIcon.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const PRODUCT_COLORS = {
  'crop-enhancement': {
    bg: '#f89e18',
    text: '#fff',
    label: 'Crop Enhancement'
  },
  'weed-control': {
    bg: '#7db41e',
    text: '#fff',
    label: 'Weed Control'
  },
  'disease-control': {
    bg: '#00a0df',
    text: '#fff',
    label: 'Disease Control'
  },
  'pest-control': {
    bg: '#9d1d96',
    text: '#fff',
    label: 'Pest Control'
  },
  corporate: {
    bg: '#009845',
    text: '#fff',
    label: 'Corporate'
  },
  earth: {
    bg: '#978b87',
    text: '#fff',
    label: 'ADAMA Earth'
  }
};

/** A tag/chip for labelling product category context */
function Tag({
  children,
  category,
  onRemove,
  size = 'md',
  style: extraStyle,
  ...props
}) {
  const c = category && PRODUCT_COLORS[category] || {
    bg: '#e5e1e0',
    text: '#5f504d',
    label: ''
  };
  const sizes = {
    sm: {
      fontSize: '11px',
      padding: '3px 9px',
      gap: '4px',
      height: '22px',
      removeSize: '14px'
    },
    md: {
      fontSize: '13px',
      padding: '4px 12px',
      gap: '5px',
      height: '26px',
      removeSize: '16px'
    },
    lg: {
      fontSize: '14px',
      padding: '5px 14px',
      gap: '6px',
      height: '30px',
      removeSize: '18px'
    }
  };
  const s = sizes[size] || sizes.md;
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: s.gap,
      fontFamily: 'var(--font-primary)',
      fontWeight: 600,
      fontSize: s.fontSize,
      height: s.height,
      padding: s.padding,
      borderRadius: 'var(--radius-full)',
      background: c.bg,
      color: c.text,
      whiteSpace: 'nowrap',
      letterSpacing: '0.01em',
      ...extraStyle
    }
  }, props), children || c.label, onRemove && /*#__PURE__*/React.createElement("button", {
    onClick: onRemove,
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      color: 'inherit',
      opacity: 0.75,
      padding: 0,
      fontSize: s.removeSize,
      lineHeight: 1
    },
    "aria-label": "Remove"
  }, "\xD7"));
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.ProductIcon = __ds_scope.ProductIcon;

__ds_ns.Tag = __ds_scope.Tag;

})();
