<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";

  // Fractal types
  type FractalType = "newton" | "julia" | "mandelbrot";

  // State
  let fractalType: FractalType = $state("newton");
  let computing = $state(false);
  let imageData = $state<string | null>(null);
  let canvasRef = $state<HTMLCanvasElement | null>(null);
  let overlayRef = $state<HTMLCanvasElement | null>(null);

  // Parameters
  let resolution = $state(600);
  let maxIter = $state(100);

  // Viewport
  let xMin = $state(-2);
  let xMax = $state(2);
  let yMin = $state(-2);
  let yMax = $state(2);

  // Newton params
  let newtonN = $state(3);

  // Julia params
  let juliaReal = $state(-0.7);
  let juliaImag = $state(0.27015);

  // Color settings
  let color1 = $state("#0000ff"); // Start color (blue)
  let color2 = $state("#ff0000"); // End color (red)
  let insideColor = $state("#000000"); // Color for points inside the set

  // Helper to convert hex to RGB array
  function hexToRgb(hex: string): [number, number, number] {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
      : [0, 0, 0];
  }

  // Zoom level (for display)
  let zoomLevel = $state(1);

  // Selection rectangle state
  let isSelecting = $state(false);
  let selectionStart = $state<{x: number, y: number} | null>(null);
  let selectionEnd = $state<{x: number, y: number} | null>(null);
  let shiftHeld = $state(false);

  // Zoom history for back button
  let zoomHistory: Array<{xMin: number, xMax: number, yMin: number, yMax: number}> = [];

  // Track shift key
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === "Shift") shiftHeld = true;
  }
  function handleKeyUp(e: KeyboardEvent) {
    if (e.key === "Shift") shiftHeld = false;
  }

  // Presets for Julia set
  const juliaPresets = [
    { name: "Classic", real: -0.7, imag: 0.27015 },
    { name: "Dendrite", real: 0, imag: 1 },
    { name: "Spiral", real: -0.8, imag: 0.156 },
    { name: "Dragon", real: -0.74543, imag: 0.11301 },
    { name: "Rabbit", real: -0.123, imag: 0.745 },
    { name: "San Marco", real: -0.75, imag: 0 },
  ];

  async function compute() {
    computing = true;
    try {
      let result: { image_data: string; width: number; height: number };

      const colorParams = {
        color1: hexToRgb(color1),
        color2: hexToRgb(color2),
        inside_color: hexToRgb(insideColor),
      };

      if (fractalType === "newton") {
        result = await invoke("compute_newton", {
          params: {
            n: newtonN,
            width: resolution,
            height: resolution,
            x_min: xMin,
            x_max: xMax,
            y_min: yMin,
            y_max: yMax,
            max_iter: maxIter,
            ...colorParams,
          },
        });
      } else if (fractalType === "julia") {
        result = await invoke("compute_julia", {
          params: {
            c_real: juliaReal,
            c_imag: juliaImag,
            width: resolution,
            height: resolution,
            x_min: xMin,
            x_max: xMax,
            y_min: yMin,
            y_max: yMax,
            max_iter: maxIter,
            ...colorParams,
          },
        });
      } else {
        result = await invoke("compute_mandelbrot", {
          params: {
            c_real: 0,
            c_imag: 0,
            width: resolution,
            height: resolution,
            x_min: xMin,
            x_max: xMax,
            y_min: yMin,
            y_max: yMax,
            max_iter: maxIter,
            ...colorParams,
          },
        });
      }

      // Decode base64 and draw to canvas
      const bytes = Uint8Array.from(atob(result.image_data), (c) => c.charCodeAt(0));
      const canvas = canvasRef;
      if (canvas) {
        canvas.width = result.width;
        canvas.height = result.height;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const imgData = ctx.createImageData(result.width, result.height);
          imgData.data.set(bytes);
          ctx.putImageData(imgData, 0, 0);
        }
      }
      // Sync overlay size
      if (overlayRef && canvasRef) {
        overlayRef.width = canvasRef.width;
        overlayRef.height = canvasRef.height;
      }
    } catch (e) {
      console.error("Computation failed:", e);
    }
    computing = false;
  }

  function getCanvasCoords(event: MouseEvent): {x: number, y: number} | null {
    if (!canvasRef) return null;
    const rect = canvasRef.getBoundingClientRect();
    const scaleX = canvasRef.width / rect.width;
    const scaleY = canvasRef.height / rect.height;
    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY
    };
  }

  function drawSelectionRect() {
    if (!overlayRef || !selectionStart || !selectionEnd) return;
    const ctx = overlayRef.getContext("2d");
    if (!ctx) return;

    // Clear previous
    ctx.clearRect(0, 0, overlayRef.width, overlayRef.height);

    // Calculate rectangle dimensions
    let w = Math.abs(selectionEnd.x - selectionStart.x);
    let h = Math.abs(selectionEnd.y - selectionStart.y);

    // If shift is held, make it square (use the larger dimension)
    if (shiftHeld) {
      const size = Math.max(w, h);
      w = size;
      h = size;
    }

    // Calculate top-left position
    const x = selectionEnd.x >= selectionStart.x ? selectionStart.x : selectionStart.x - w;
    const y = selectionEnd.y >= selectionStart.y ? selectionStart.y : selectionStart.y - h;

    // Semi-transparent fill
    ctx.fillStyle = "rgba(102, 126, 234, 0.2)";
    ctx.fillRect(x, y, w, h);

    // Border
    ctx.strokeStyle = shiftHeld ? "#ffa500" : "#667eea"; // Orange when square mode
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(x, y, w, h);
  }

  function clearSelectionRect() {
    if (!overlayRef) return;
    const ctx = overlayRef.getContext("2d");
    if (ctx) {
      ctx.clearRect(0, 0, overlayRef.width, overlayRef.height);
    }
  }

  function handleMouseDown(event: MouseEvent) {
    if (event.button !== 0) return; // Only left click
    const coords = getCanvasCoords(event);
    if (!coords) return;

    isSelecting = true;
    selectionStart = coords;
    selectionEnd = coords;
  }

  function handleMouseMove(event: MouseEvent) {
    if (!isSelecting) return;
    const coords = getCanvasCoords(event);
    if (!coords) return;

    selectionEnd = coords;
    drawSelectionRect();
  }

  function handleMouseUp(event: MouseEvent) {
    if (!isSelecting || !selectionStart || !selectionEnd || !canvasRef) {
      isSelecting = false;
      return;
    }

    isSelecting = false;
    clearSelectionRect();

    // Calculate selection size
    let dx = Math.abs(selectionEnd.x - selectionStart.x);
    let dy = Math.abs(selectionEnd.y - selectionStart.y);

    // If too small, treat as a click (zoom 2x centered)
    if (dx < 10 && dy < 10) {
      const clickX = xMin + (selectionStart.x / canvasRef.width) * (xMax - xMin);
      const clickY = yMax - (selectionStart.y / canvasRef.height) * (yMax - yMin);

      zoomHistory.push({ xMin, xMax, yMin, yMax });

      const zoomFactor = 0.5;
      const newWidth = (xMax - xMin) * zoomFactor;
      const newHeight = (yMax - yMin) * zoomFactor;

      xMin = clickX - newWidth / 2;
      xMax = clickX + newWidth / 2;
      yMin = clickY - newHeight / 2;
      yMax = clickY + newHeight / 2;

      zoomLevel = 4 / (xMax - xMin);
      compute();
      return;
    }

    // If shift is held, make it square
    if (shiftHeld) {
      const size = Math.max(dx, dy);
      dx = size;
      dy = size;
    }

    // Calculate rectangle bounds accounting for shift/square mode
    let x1, x2, y1, y2;
    if (shiftHeld) {
      const size = Math.max(
        Math.abs(selectionEnd.x - selectionStart.x),
        Math.abs(selectionEnd.y - selectionStart.y)
      );
      x1 = selectionEnd.x >= selectionStart.x ? selectionStart.x : selectionStart.x - size;
      x2 = x1 + size;
      y1 = selectionEnd.y >= selectionStart.y ? selectionStart.y : selectionStart.y - size;
      y2 = y1 + size;
    } else {
      x1 = Math.min(selectionStart.x, selectionEnd.x);
      x2 = Math.max(selectionStart.x, selectionEnd.x);
      y1 = Math.min(selectionStart.y, selectionEnd.y);
      y2 = Math.max(selectionStart.y, selectionEnd.y);
    }

    // Convert to complex plane
    const newXMin = xMin + (x1 / canvasRef.width) * (xMax - xMin);
    const newXMax = xMin + (x2 / canvasRef.width) * (xMax - xMin);
    const newYMax = yMax - (y1 / canvasRef.height) * (yMax - yMin);
    const newYMin = yMax - (y2 / canvasRef.height) * (yMax - yMin);

    zoomHistory.push({ xMin, xMax, yMin, yMax });

    xMin = newXMin;
    xMax = newXMax;
    yMin = newYMin;
    yMax = newYMax;

    zoomLevel = 4 / (xMax - xMin);
    compute();

    selectionStart = null;
    selectionEnd = null;
  }

  function handleRightClick(event: MouseEvent) {
    event.preventDefault();
    if (zoomHistory.length > 0) {
      const prev = zoomHistory.pop()!;
      xMin = prev.xMin;
      xMax = prev.xMax;
      yMin = prev.yMin;
      yMax = prev.yMax;
      zoomLevel = 4 / (xMax - xMin);
      compute();
    }
  }

  function reset() {
    xMin = -2;
    xMax = 2;
    yMin = -2;
    yMax = 2;
    zoomLevel = 1;
    zoomHistory = [];
    compute();
  }

  function resetToSquare() {
    // Make the current view square by using the larger dimension
    const currentWidth = xMax - xMin;
    const currentHeight = yMax - yMin;
    const centerX = (xMin + xMax) / 2;
    const centerY = (yMin + yMax) / 2;
    const size = Math.max(currentWidth, currentHeight);

    zoomHistory.push({ xMin, xMax, yMin, yMax });

    xMin = centerX - size / 2;
    xMax = centerX + size / 2;
    yMin = centerY - size / 2;
    yMax = centerY + size / 2;

    zoomLevel = 4 / size;
    compute();
  }

  function applyPreset(preset: typeof juliaPresets[0]) {
    juliaReal = preset.real;
    juliaImag = preset.imag;
    reset();
  }

  function applyZoomSlider() {
    // Calculate new bounds centered on current view
    const centerX = (xMin + xMax) / 2;
    const centerY = (yMin + yMax) / 2;
    const newWidth = 4 / zoomLevel;
    const newHeight = 4 / zoomLevel;

    zoomHistory.push({ xMin, xMax, yMin, yMax });

    xMin = centerX - newWidth / 2;
    xMax = centerX + newWidth / 2;
    yMin = centerY - newHeight / 2;
    yMax = centerY + newHeight / 2;

    compute();
  }

  function exportImage() {
    if (!canvasRef) return;
    const link = document.createElement("a");
    link.download = `${fractalType}-fractal.png`;
    link.href = canvasRef.toDataURL("image/png");
    link.click();
  }

  // Compute on mount
  $effect(() => {
    compute();
  });
</script>

<svelte:window onkeydown={handleKeyDown} onkeyup={handleKeyUp} />

<main>
  <aside class="controls">
    <h1>Julia Sets</h1>

    <section>
      <h2>Fractal Type</h2>
      <div class="button-group">
        <button
          class:active={fractalType === "newton"}
          onclick={() => { fractalType = "newton"; reset(); }}
        >
          Newton z^n-1
        </button>
        <button
          class:active={fractalType === "julia"}
          onclick={() => { fractalType = "julia"; reset(); }}
        >
          Julia Set
        </button>
        <button
          class:active={fractalType === "mandelbrot"}
          onclick={() => { fractalType = "mandelbrot"; reset(); }}
        >
          Mandelbrot
        </button>
      </div>
    </section>

    {#if fractalType === "newton"}
      <section>
        <h2>Newton Parameters</h2>
        <label>
          Exponent (n): <strong>{newtonN}</strong>
          <input type="range" min="2" max="12" bind:value={newtonN} onchange={compute} />
        </label>
      </section>
    {/if}

    {#if fractalType === "julia"}
      <section>
        <h2>Julia Constant (c)</h2>
        <label>
          Real: <strong>{juliaReal.toFixed(4)}</strong>
          <input type="range" min="-2" max="2" step="0.001" bind:value={juliaReal} onchange={compute} />
        </label>
        <label>
          Imaginary: <strong>{juliaImag.toFixed(4)}</strong>
          <input type="range" min="-2" max="2" step="0.001" bind:value={juliaImag} onchange={compute} />
        </label>
        <h3>Presets</h3>
        <div class="presets">
          {#each juliaPresets as preset}
            <button onclick={() => applyPreset(preset)}>{preset.name}</button>
          {/each}
        </div>
      </section>
    {/if}

    <section>
      <h2>Zoom</h2>
      <label>
        Level: <strong>{zoomLevel.toFixed(1)}x</strong>
        <input
          type="range"
          min="1"
          max="1000"
          step="1"
          bind:value={zoomLevel}
          onchange={applyZoomSlider}
        />
      </label>
      <div class="zoom-info">
        <span>X: [{xMin.toFixed(4)}, {xMax.toFixed(4)}]</span>
        <span>Y: [{yMin.toFixed(4)}, {yMax.toFixed(4)}]</span>
      </div>
    </section>

    <section>
      <h2>Colors</h2>
      <div class="color-row">
        <label class="color-label">
          Start
          <input type="color" bind:value={color1} onchange={compute} />
        </label>
        <label class="color-label">
          End
          <input type="color" bind:value={color2} onchange={compute} />
        </label>
        <label class="color-label">
          Inside
          <input type="color" bind:value={insideColor} onchange={compute} />
        </label>
      </div>
      <div class="color-presets">
        <button onclick={() => { color1 = "#0000ff"; color2 = "#ff0000"; insideColor = "#000000"; compute(); }}>Classic</button>
        <button onclick={() => { color1 = "#00ffff"; color2 = "#ff00ff"; insideColor = "#000000"; compute(); }}>Neon</button>
        <button onclick={() => { color1 = "#ffffff"; color2 = "#000000"; insideColor = "#808080"; compute(); }}>Grayscale</button>
        <button onclick={() => { color1 = "#00ff00"; color2 = "#ffff00"; insideColor = "#001100"; compute(); }}>Matrix</button>
        <button onclick={() => { color1 = "#ff6600"; color2 = "#3300ff"; insideColor = "#000022"; compute(); }}>Sunset</button>
        <button onclick={() => { color1 = "#ffd700"; color2 = "#4b0082"; insideColor = "#1a0a2e"; compute(); }}>Royal</button>
      </div>
    </section>

    <section>
      <h2>Quality</h2>
      <label>
        Resolution: <strong>{resolution}px</strong>
        <input type="range" min="200" max="4000" step="100" bind:value={resolution} onchange={compute} />
      </label>
      <label>
        Max Iterations: <strong>{maxIter}</strong>
        <input type="range" min="20" max="10000" step="10" bind:value={maxIter} onchange={compute} />
      </label>
    </section>

    <section>
      <h2>Actions</h2>
      <div class="button-group vertical">
        <button onclick={reset}>Reset View</button>
        <button onclick={resetToSquare}>Reset to Square</button>
        <button onclick={exportImage}>Export PNG</button>
      </div>
    </section>

    <p class="hint">
      Drag to select area. Hold <strong>Shift</strong> for square selection.<br />
      Right-click to zoom out.
    </p>
  </aside>

  <div class="canvas-container">
    {#if computing}
      <div class="loading">
        <div class="spinner"></div>
        <span>Computing...</span>
      </div>
    {/if}
    <div class="canvas-wrapper">
      <canvas
        bind:this={canvasRef}
        class:computing
      ></canvas>
      <canvas
        bind:this={overlayRef}
        class="overlay"
        onmousedown={handleMouseDown}
        onmousemove={handleMouseMove}
        onmouseup={handleMouseUp}
        onmouseleave={() => { if (isSelecting) { isSelecting = false; clearSelectionRect(); } }}
        oncontextmenu={handleRightClick}
      ></canvas>
    </div>
  </div>
</main>

<style>
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(body) {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0a0a0f;
    color: #e0e0e0;
    overflow: hidden;
  }

  main {
    display: flex;
    height: 100vh;
    width: 100vw;
  }

  .controls {
    width: 320px;
    background: linear-gradient(180deg, #12121a 0%, #0d0d12 100%);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    overflow-y: auto;
    border-right: 1px solid #2a2a3a;
  }

  h1 {
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  h2 {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #888;
    margin-bottom: 12px;
  }

  h3 {
    font-size: 0.75rem;
    font-weight: 500;
    color: #666;
    margin: 12px 0 8px;
  }

  section {
    padding-bottom: 16px;
    border-bottom: 1px solid #1a1a24;
  }

  label {
    display: block;
    margin-bottom: 12px;
    font-size: 0.9rem;
    color: #aaa;
  }

  label strong {
    color: #fff;
    margin-left: 8px;
  }

  input[type="range"] {
    width: 100%;
    height: 6px;
    margin-top: 8px;
    border-radius: 3px;
    background: #2a2a3a;
    appearance: none;
    cursor: pointer;
  }

  input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.4);
  }

  .button-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .button-group.vertical {
    flex-direction: column;
  }

  button {
    padding: 10px 16px;
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    background: #1a1a24;
    color: #ccc;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  button:hover {
    background: #252532;
    border-color: #3a3a4a;
    color: #fff;
  }

  button.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
    color: #fff;
  }

  .presets {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }

  .presets button {
    padding: 8px 12px;
    font-size: 0.8rem;
  }

  .zoom-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.75rem;
    color: #666;
    font-family: monospace;
    margin-top: 8px;
  }

  .color-row {
    display: flex;
    gap: 12px;
    justify-content: space-between;
  }

  .color-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: #888;
  }

  input[type="color"] {
    width: 48px;
    height: 32px;
    border: 2px solid #2a2a3a;
    border-radius: 6px;
    background: transparent;
    cursor: pointer;
    padding: 0;
  }

  input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 2px;
  }

  input[type="color"]::-webkit-color-swatch {
    border-radius: 4px;
    border: none;
  }

  .color-presets {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-top: 12px;
  }

  .color-presets button {
    padding: 6px 8px;
    font-size: 0.7rem;
  }

  .hint {
    font-size: 0.8rem;
    color: #666;
    text-align: center;
    margin-top: auto;
  }

  .canvas-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: #08080c;
  }

  .canvas-wrapper {
    position: relative;
    max-width: calc(100vh - 48px);
    max-height: calc(100vh - 48px);
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
    border-radius: 12px;
    box-shadow: 0 0 60px rgba(102, 126, 234, 0.15);
  }

  canvas.computing {
    opacity: 0.5;
  }

  canvas.overlay {
    position: absolute;
    top: 0;
    left: 0;
    cursor: crosshair;
    box-shadow: none;
  }

  .loading {
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    color: #888;
    font-size: 0.9rem;
    z-index: 10;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #2a2a3a;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
