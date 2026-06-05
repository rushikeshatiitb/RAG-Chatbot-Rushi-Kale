---
name: Lumina Finance
colors:
  surface: '#0e1511'
  surface-dim: '#0e1511'
  surface-bright: '#343b36'
  surface-container-lowest: '#09100c'
  surface-container-low: '#161d19'
  surface-container: '#1a211d'
  surface-container-high: '#242c27'
  surface-container-highest: '#2f3632'
  on-surface: '#dde4dd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dde4dd'
  inverse-on-surface: '#2b322d'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#c1c7cf'
  on-secondary: '#2b3137'
  secondary-container: '#41474e'
  on-secondary-container: '#afb6bd'
  tertiary: '#b7c8e1'
  on-tertiary: '#213145'
  tertiary-container: '#94a4bd'
  on-tertiary-container: '#2a3a4f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#dde3eb'
  secondary-fixed-dim: '#c1c7cf'
  on-secondary-fixed: '#161c22'
  on-secondary-fixed-variant: '#41474e'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#0e1511'
  on-background: '#dde4dd'
  surface-variant: '#2f3632'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1200px
  gutter: 24px
---

## Brand & Style
The design system is engineered for a premium wealth-management experience, specifically tailored for the SBI Mutual Fund FAQ Assistant. The brand personality is authoritative yet accessible, evoking a sense of institutional security blended with modern technological agility. 

The aesthetic follows a **Wealth-Tech Modern** direction, utilizing **Glassmorphism** to create depth and sophistication. This style emphasizes clarity through semi-transparent surfaces, subtle backdrop blurs, and soft radial glows that guide the user's focus. The emotional response should be one of "calm confidence"—the user feels their financial queries are being handled by a precise, high-end digital concierge.

## Colors
The palette is rooted in a **Deep Navy Blue** (#0A192F) foundation to establish trust and stability. 

- **Primary (Jade):** Used for CTA buttons, success states, and indicating verified citations. It represents growth and financial health.
- **Secondary (Ice Blue):** The primary text color, providing high legibility against dark backgrounds without the harshness of pure white.
- **Tertiary (Slate):** Reserved for subtle borders, secondary labels, and inactive states.
- **Surface:** Glassmorphic layers use white with 5% - 8% opacity and a 12px-20px backdrop blur to create a sense of physical layering.

## Typography
This design system utilizes a dual-font strategy. **Outfit** is used for headlines to provide a modern, geometric, and premium feel. **Inter** is used for body copy and data labels due to its exceptional legibility at small sizes and neutral, professional tone.

- **Contrast:** Maintain high contrast between headlines (Ice Blue) and secondary metadata (Slate).
- **Scale:** On mobile devices, display and large headlines should scale down by approximately 25% to maintain visual balance within the viewport.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a max-width container for desktop. A 12-column system is used for dashboard views, while the FAQ Assistant interface is centered with generous side margins to mimic a focused, conversational experience.

- **Desktop:** 12 columns, 24px gutters, 64px side margins.
- **Tablet:** 8 columns, 16px gutters, 32px side margins.
- **Mobile:** 4 columns, 16px gutters, 16px side margins.
- **Rhythm:** Use an 8px base grid for all padding and margin increments to ensure vertical harmony.

## Elevation & Depth
Depth is not conveyed through traditional black shadows, but through **Tonal Layering** and **Backdrop Blurs**.

1.  **Level 0 (Base):** Deep Navy Blue (#0A192F).
2.  **Level 1 (Cards/Panels):** Surface color (5% white) with a 1px border (#64748B at 20% opacity) and a 16px backdrop blur.
3.  **Level 2 (Modals/Popovers):** Surface color (10% white) with a soft Jade glow (primary color at 10% opacity, 40px blur) appearing behind the element to suggest "light" emitting from within.

Borders should be used sparingly but crisply to define edges where blur alone is insufficient.

## Shapes
The design system adopts a **Rounded** shape language. 
- **Standard UI Elements:** (Buttons, Inputs, Cards) use a 0.5rem (8px) radius.
- **Large Containers:** Use 1rem (16px) for a softer, more modern tech feel.
- **Search Bars:** Are pill-shaped (full radius) to indicate a primary entry point and distinct interaction zone.

## Components

### Buttons
- **Primary:** Jade background, Navy text, bold weight. On hover, apply a subtle Jade outer glow.
- **Secondary:** Transparent with an Ice Blue border and text.
- **Ghost:** Ice Blue text, no background, used for low-priority actions like "Cancel".

### Cards
Cards are the primary container. They must feature a 1px Slate border at 20% opacity and a subtle top-down linear gradient (White 5% to White 2%). Use internal padding of 24px.

### Inputs (Search & Chat)
The main FAQ input should be pill-shaped with a 1px Slate border. Upon focus, the border transitions to Jade, and a soft 8px Jade outer glow (20% opacity) is applied.

### Data Visualization
- **Progress Bars:** Use a Slate track with a Jade fill. Fill should have a slight "pulse" animation for active states.
- **Citations:** Small, high-contrast chips (Jade background at 10% opacity, Jade text) used to link to fund documents or legal disclaimers.

### Status Rings
Small circular indicators for system health or fund performance. Use Jade for "On Track" and a subtle Slate for "Historical".