//! E001-02: exact 3:1 decimation 48 kHz → 16 kHz, used only at the scoring boundary.
//!
//! Linear-phase windowed-sinc (Blackman) low-pass, cutoff 7.2 kHz, 95 taps.

use std::f64::consts::PI;

const TAPS: usize = 95;
const FACTOR: usize = 3;
const CUTOFF_HZ: f64 = 7_200.0;
const FS: f64 = 48_000.0;

fn kernel() -> [f32; TAPS] {
    let mut h = [0f32; TAPS];
    let m = (TAPS - 1) as f64;
    let fc = CUTOFF_HZ / FS;
    let mut sum = 0.0;
    for (n, tap) in h.iter_mut().enumerate() {
        let k = n as f64 - m / 2.0;
        let sinc = if k == 0.0 {
            2.0 * fc
        } else {
            (2.0 * PI * fc * k).sin() / (PI * k)
        };
        let w =
            0.42 - 0.5 * (2.0 * PI * n as f64 / m).cos() + 0.08 * (4.0 * PI * n as f64 / m).cos();
        let v = sinc * w;
        *tap = v as f32;
        sum += v;
    }
    for tap in h.iter_mut() {
        *tap /= sum as f32; // unity DC gain
    }
    h
}

/// Output length is `pcm.len() / 3`. Zero-padded edges; group delay is compensated.
pub fn downsample_48k_to_16k(pcm: &[i16]) -> Vec<i16> {
    let h = kernel();
    let half = (TAPS / 2) as isize;
    let n_out = pcm.len() / FACTOR;
    let mut out = Vec::with_capacity(n_out);
    for o in 0..n_out {
        let centre = (o * FACTOR) as isize;
        let mut acc = 0.0f32;
        for (j, &c) in h.iter().enumerate() {
            let idx = centre + j as isize - half;
            if idx >= 0 && (idx as usize) < pcm.len() {
                acc += c * pcm[idx as usize] as f32;
            }
        }
        out.push(acc.round().clamp(-32768.0, 32767.0) as i16);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::frame::rms_db;
    use crate::testsig::sine;

    #[test]
    fn test_e001_02_length_is_one_third() {
        assert_eq!(downsample_48k_to_16k(&[0; 960]).len(), 320);
        assert_eq!(downsample_48k_to_16k(&[0; 961]).len(), 320);
        assert!(downsample_48k_to_16k(&[]).is_empty());
    }

    #[test]
    fn test_e001_02_passband_preserved() {
        for &f in &[200.0, 1000.0, 4000.0, 6000.0] {
            let x = sine(f, 48_000, 0.5);
            let y = downsample_48k_to_16k(&x);
            // Ignore filter edges.
            let gain = rms_db(&y[200..y.len() - 200]) - rms_db(&x[600..x.len() - 600]);
            assert!(gain.abs() < 0.5, "f={f} gain={gain}");
        }
    }

    #[test]
    fn test_e001_02_aliasing_band_rejected() {
        // 10 kHz and 12 kHz would alias into 6 kHz / 4 kHz at 16 kHz without filtering.
        for &f in &[10_000.0, 12_000.0, 15_000.0] {
            let x = sine(f, 48_000, 0.5);
            let y = downsample_48k_to_16k(&x);
            let att = rms_db(&x[600..x.len() - 600]) - rms_db(&y[200..y.len() - 200]);
            assert!(att > 50.0, "f={f} attenuation={att}");
        }
    }
}
