/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		maxWidth: {
  			'7xl': '1200px'
  		},
  		fontFamily: {
  			sans: [
  				'Helvetica Neue',
  				'Helvetica',
  				'Arial',
  				'sans-serif'
  			]
  		},
  		colors: {
  			'brand-orange': {
  				'50': '#FFF5ED',
  				'100': '#FFE8D4',
  				'200': '#FFCDA8',
  				'300': '#FFAA72',
  				'400': '#FE7C39',
  				'500': '#FD5108',
  				'600': '#E8460A',
  				'700': '#D13D09'
  			},
  			'brand-gray': {
  				'50': '#F5F7F8',
  				'100': '#EEEFF1',
  				'200': '#DFE3E6',
  				'300': '#CBD1D6',
  				'400': '#B5BCC4',
  				'500': '#A1A8B3'
  			},
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		animation: {
  			spin: 'spin 1s linear infinite',
  			fadeIn: 'fadeIn 0.3s ease-in',
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		},
  		keyframes: {
  			fadeIn: {
  				from: {
  					opacity: '0',
  					transform: 'translateY(-10px)'
  				},
  				to: {
  					opacity: '1',
  					transform: 'translateY(0)'
  				}
  			},
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		typography: {
  			DEFAULT: {
  				css: {
  					maxWidth: 'none',
  					color: '#374151',
  					a: {
  						color: '#2563eb',
  						'&:hover': {
  							color: '#1e40af'
  						}
  					},
  					code: {
  						color: '#dc2626',
  						backgroundColor: '#f3f4f6',
  						padding: '0.25rem 0.375rem',
  						borderRadius: '0.25rem',
  						fontWeight: '400'
  					},
  					'code::before': {
  						content: '""'
  					},
  					'code::after': {
  						content: '""'
  					},
  					pre: {
  						backgroundColor: '#1e1e1e',
  						color: '#d4d4d4'
  					}
  				}
  			},
  			sm: {
  				css: {
  					fontSize: '0.875rem',
  					lineHeight: '1.5rem',
  					h1: {
  						fontSize: '1.5rem',
  						lineHeight: '2rem'
  					},
  					h2: {
  						fontSize: '1.25rem',
  						lineHeight: '1.75rem'
  					},
  					h3: {
  						fontSize: '1.125rem',
  						lineHeight: '1.5rem'
  					}
  				}
  			}
  		}
  	}
  },
  plugins: [require("tailwindcss-animate"), require("@tailwindcss/typography")],
};