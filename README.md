# Julia Sets Explorer

A modern, high-performance fractal visualization tool built with **Rust** and **Tauri + Svelte**.

This is a complete rewrite of the original Python 2.x wxPython application, now featuring a blazing-fast Rust backend with parallel computation and a sleek, modern web-based UI.

## Features

- **Three Fractal Types:**
  - **Newton Fractal** - Visualizes convergence of Newton's method for z^n - 1 = 0
  - **Julia Set** - Classic z² + c iteration with customizable constant c
  - **Mandelbrot Set** - The famous Mandelbrot set with cardioid/bulb optimization

- **Interactive Zoom:**
  - Click and drag to select a region to zoom into
  - Hold **Shift** while dragging for square selection
  - Zoom slider (1x - 1000x)
  - Reset to Square button for returning to default view

- **Customizable Colors:**
  - Three color pickers: Start color, End color, Inside set color
  - Six built-in presets: Classic, Neon, Grayscale, Matrix, Sunset, Royal

- **High Performance:**
  - Parallel computation using Rayon
  - Smooth coloring using normalized iteration count (eliminates banding)
  - Periodicity detection for faster rendering of interior points
  - Cardioid/bulb check for Mandelbrot optimization
  - Resolution up to 4000x4000 pixels
  - Up to 10,000 iterations

## Tech Stack

- **Backend:** Rust with Tauri 2.0
- **Frontend:** Svelte 5 with TypeScript
- **Computation:** num-complex, Rayon (parallel processing)
- **Build:** Vite, Cargo

## Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://rustup.rs/) (latest stable)
- Platform-specific dependencies for Tauri (see [Tauri Prerequisites](https://tauri.app/v1/guides/getting-started/prerequisites))

## Installation

```bash
# Clone the repository
git clone https://github.com/gcol33/plotjuliasets.git
cd plotjuliasets/julia-sets

# Install dependencies
npm install

# Run in development mode
npm run tauri dev

# Build for production
npm run tauri build
```

## Usage

1. **Select a fractal type** from the dropdown menu
2. **Adjust parameters:**
   - For Newton: set the exponent n
   - For Julia: set the complex constant c (real and imaginary parts)
3. **Set resolution and iterations** using the sliders
4. **Choose colors** using the color pickers or select a preset
5. **Click "Compute"** to generate the fractal
6. **Zoom in** by clicking and dragging on the canvas (hold Shift for square selection)

## Project Structure

```
julia-sets/
├── src/                    # Svelte frontend
│   └── routes/
│       └── +page.svelte    # Main UI component
├── src-tauri/
│   ├── src/
│   │   └── lib.rs          # Rust backend (fractal computation)
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri configuration
└── package.json            # Node dependencies
```

## Legacy Version

The original Python 2.x version using wxPython and matplotlib is preserved in the repository root for reference. The new Rust version offers significantly better performance and a more modern user experience.

## License

MIT
