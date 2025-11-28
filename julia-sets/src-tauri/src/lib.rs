use num_complex::Complex64;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};

/// Result of Julia set computation - returns image as base64 PNG
#[derive(Serialize, Deserialize)]
pub struct JuliaResult {
    pub image_data: String, // base64 encoded raw RGBA pixels
    pub width: u32,
    pub height: u32,
    pub iterations_used: u32,
}

/// Parameters for Newton iteration (z^n - 1 = 0)
#[derive(Deserialize)]
pub struct NewtonParams {
    pub n: u32,           // exponent
    pub width: u32,       // image width
    pub height: u32,      // image height
    pub x_min: f64,
    pub x_max: f64,
    pub y_min: f64,
    pub y_max: f64,
    pub max_iter: u32,
    // Color parameters
    pub color1: [u8; 3],      // Start color (RGB)
    pub color2: [u8; 3],      // End color (RGB)
    pub inside_color: [u8; 3], // Inside set color (RGB)
}

/// Parameters for custom iteration f(z)
#[derive(Deserialize)]
pub struct CustomIterParams {
    pub c_real: f64,      // constant c (real part)
    pub c_imag: f64,      // constant c (imaginary part)
    pub width: u32,
    pub height: u32,
    pub x_min: f64,
    pub x_max: f64,
    pub y_min: f64,
    pub y_max: f64,
    pub max_iter: u32,
    // Color parameters
    pub color1: [u8; 3],      // Start color (RGB)
    pub color2: [u8; 3],      // End color (RGB)
    pub inside_color: [u8; 3], // Inside set color (RGB)
}

/// Color palette for roots with custom gradient
fn root_color_custom(angle: f64, color1: [u8; 3], color2: [u8; 3]) -> [u8; 4] {
    // Normalize angle to [0, 1]
    let t = (angle + std::f64::consts::PI) / (2.0 * std::f64::consts::PI);

    // Linear interpolation between color1 and color2 based on angle
    let r = (color1[0] as f64 * (1.0 - t) + color2[0] as f64 * t) as u8;
    let g = (color1[1] as f64 * (1.0 - t) + color2[1] as f64 * t) as u8;
    let b = (color1[2] as f64 * (1.0 - t) + color2[2] as f64 * t) as u8;

    [r, g, b, 255]
}

/// Smooth coloring using normalized iteration count with custom colors
/// This eliminates banding artifacts by using the fractional escape value
fn smooth_escape_color_custom(
    iterations: u32,
    max_iter: u32,
    z_final_norm_sq: f64,
    color1: [u8; 3],
    color2: [u8; 3],
    inside_color: [u8; 3],
) -> [u8; 4] {
    if iterations >= max_iter {
        // Inside the set - use custom inside color
        [inside_color[0], inside_color[1], inside_color[2], 255]
    } else {
        // Smooth coloring using normalized iteration count
        // Formula: n + 1 - log2(log2(|z|)) = n + 1 - log(ln(|z|))/log(2)
        let log_zn = z_final_norm_sq.ln() / 2.0; // ln(|z|) = ln(|z|^2)/2
        let nu = (log_zn / 2.0_f64.ln()).ln() / 2.0_f64.ln();
        let smooth_iter = iterations as f64 + 1.0 - nu;

        // Interpolation factor (0 to 1)
        let t = (smooth_iter / max_iter as f64).clamp(0.0, 1.0);

        // Linear interpolation between color1 and color2
        let r = (color1[0] as f64 * (1.0 - t) + color2[0] as f64 * t) as u8;
        let g = (color1[1] as f64 * (1.0 - t) + color2[1] as f64 * t) as u8;
        let b = (color1[2] as f64 * (1.0 - t) + color2[2] as f64 * t) as u8;

        [r, g, b, 255]
    }
}

/// Newton iteration for z^n - 1 = 0
/// f(z) = z^n - 1
/// f'(z) = n * z^(n-1)
/// Newton step: z_new = z - f(z)/f'(z) = z - (z^n - 1)/(n * z^(n-1))
///            = z - z/n + 1/(n * z^(n-1))
///            = z * (1 - 1/n) + 1/(n * z^(n-1))
fn newton_iterate(z: Complex64, n: u32, max_iter: u32, tol: f64) -> (Complex64, u32) {
    let mut z = z;
    let n_f = n as f64;

    for i in 0..max_iter {
        let z_n_minus_1 = z.powi(n as i32 - 1);
        let z_n = z_n_minus_1 * z;
        let f = z_n - Complex64::new(1.0, 0.0);
        let f_prime = Complex64::new(n_f, 0.0) * z_n_minus_1;

        if f_prime.norm() < 1e-10 {
            return (z, i);
        }

        let z_new = z - f / f_prime;

        if (z_new - z).norm() < tol {
            return (z_new, i);
        }

        z = z_new;
    }

    (z, max_iter)
}

/// Compute Newton fractal for z^n - 1 = 0
#[tauri::command]
fn compute_newton(params: NewtonParams) -> JuliaResult {
    let width = params.width as usize;
    let height = params.height as usize;
    let tol = 1e-6;
    let color1 = params.color1;
    let color2 = params.color2;

    // Create pixel buffer (RGBA)
    let pixels: Vec<[u8; 4]> = (0..height)
        .into_par_iter()
        .flat_map(|py| {
            let y = params.y_max - (py as f64) * (params.y_max - params.y_min) / (height as f64);

            (0..width)
                .map(|px| {
                    let x = params.x_min + (px as f64) * (params.x_max - params.x_min) / (width as f64);
                    let z0 = Complex64::new(x, y);

                    let (z_final, _iters) = newton_iterate(z0, params.n, params.max_iter, tol);

                    // Color based on which root we converged to (determined by angle)
                    let angle = z_final.arg();
                    root_color_custom(angle, color1, color2)
                })
                .collect::<Vec<_>>()
        })
        .collect();

    // Flatten to bytes
    let bytes: Vec<u8> = pixels.into_iter().flatten().collect();

    JuliaResult {
        image_data: BASE64.encode(&bytes),
        width: params.width,
        height: params.height,
        iterations_used: params.max_iter,
    }
}

/// Optimized Julia set iteration: z = z^2 + c
/// Returns (iterations, final_z_norm_squared) for smooth coloring
/// Uses:
/// - Precomputed x^2 and y^2 to avoid redundant calculations
/// - Higher bailout radius (256) for smoother color gradients
/// - Periodicity detection to speed up points inside the set
fn julia_iterate_smooth(z0: Complex64, c: Complex64, max_iter: u32) -> (u32, f64) {
    let mut zx = z0.re;
    let mut zy = z0.im;
    let cx = c.re;
    let cy = c.im;

    // Periodicity detection: store old value every N iterations
    let mut old_zx = zx;
    let mut old_zy = zy;
    let mut period = 0u32;
    const PERIOD_CHECK: u32 = 20;

    for i in 0..max_iter {
        // Precompute squares (optimization)
        let zx2 = zx * zx;
        let zy2 = zy * zy;
        let norm_sq = zx2 + zy2;

        // Bailout check (use 256 for smoother coloring with log formula)
        if norm_sq > 256.0 {
            return (i, norm_sq);
        }

        // Periodicity detection: if we return to a previous point, we're in the set
        if (zx - old_zx).abs() < 1e-10 && (zy - old_zy).abs() < 1e-10 && i > 0 {
            return (max_iter, norm_sq);
        }

        period += 1;
        if period >= PERIOD_CHECK {
            old_zx = zx;
            old_zy = zy;
            period = 0;
        }

        // z = z^2 + c (optimized: zy = 2*zx*zy + cy before zx changes)
        zy = 2.0 * zx * zy + cy;
        zx = zx2 - zy2 + cx;
    }

    (max_iter, zx * zx + zy * zy)
}

/// Compute Julia set for z^2 + c with smooth coloring
#[tauri::command]
fn compute_julia(params: CustomIterParams) -> JuliaResult {
    let width = params.width as usize;
    let height = params.height as usize;
    let c = Complex64::new(params.c_real, params.c_imag);
    let color1 = params.color1;
    let color2 = params.color2;
    let inside_color = params.inside_color;

    let pixels: Vec<[u8; 4]> = (0..height)
        .into_par_iter()
        .flat_map(|py| {
            let y = params.y_max - (py as f64) * (params.y_max - params.y_min) / (height as f64);

            (0..width)
                .map(|px| {
                    let x = params.x_min + (px as f64) * (params.x_max - params.x_min) / (width as f64);
                    let z0 = Complex64::new(x, y);

                    let (iterations, final_norm_sq) = julia_iterate_smooth(z0, c, params.max_iter);
                    smooth_escape_color_custom(iterations, params.max_iter, final_norm_sq, color1, color2, inside_color)
                })
                .collect::<Vec<_>>()
        })
        .collect();

    let bytes: Vec<u8> = pixels.into_iter().flatten().collect();

    JuliaResult {
        image_data: BASE64.encode(&bytes),
        width: params.width,
        height: params.height,
        iterations_used: params.max_iter,
    }
}

/// Mandelbrot set: z = z^2 + c where c varies and z0 = 0
/// Uses optimized iteration with cardioid/bulb checking
#[tauri::command]
fn compute_mandelbrot(params: CustomIterParams) -> JuliaResult {
    let width = params.width as usize;
    let height = params.height as usize;
    let color1 = params.color1;
    let color2 = params.color2;
    let inside_color = params.inside_color;

    let pixels: Vec<[u8; 4]> = (0..height)
        .into_par_iter()
        .flat_map(|py| {
            let y = params.y_max - (py as f64) * (params.y_max - params.y_min) / (height as f64);

            (0..width)
                .map(|px| {
                    let x = params.x_min + (px as f64) * (params.x_max - params.x_min) / (width as f64);

                    // Quick cardioid/bulb check for Mandelbrot optimization
                    let y2 = y * y;
                    let q = (x - 0.25) * (x - 0.25) + y2;
                    if q * (q + (x - 0.25)) <= 0.25 * y2 {
                        // Inside main cardioid
                        return [inside_color[0], inside_color[1], inside_color[2], 255];
                    }
                    if (x + 1.0) * (x + 1.0) + y2 <= 0.0625 {
                        // Inside period-2 bulb
                        return [inside_color[0], inside_color[1], inside_color[2], 255];
                    }

                    let c = Complex64::new(x, y);
                    let (iterations, final_norm_sq) = julia_iterate_smooth(Complex64::new(0.0, 0.0), c, params.max_iter);
                    smooth_escape_color_custom(iterations, params.max_iter, final_norm_sq, color1, color2, inside_color)
                })
                .collect::<Vec<_>>()
        })
        .collect();

    let bytes: Vec<u8> = pixels.into_iter().flatten().collect();

    JuliaResult {
        image_data: BASE64.encode(&bytes),
        width: params.width,
        height: params.height,
        iterations_used: params.max_iter,
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            compute_newton,
            compute_julia,
            compute_mandelbrot
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
