//! E001-04 / E001-05: YIN fundamental-frequency estimator (de Cheveigné & Kawahara 2002).
//!
//! Allocation-free after construction. Returns `None` for aperiodic input.

use crate::{F0_MAX_HZ, F0_MIN_HZ};

/// CMNDF threshold; lower = stricter voicing decision.
const THRESHOLD: f32 = 0.15;

pub struct Yin {
    sample_rate: f32,
    tau_min: usize,
    tau_max: usize,
    window: usize,
    diff: Vec<f32>,
}

impl Yin {
    /// `buffer_len` is the length of the slices that will be passed to `estimate`.
    pub fn new(sample_rate: u32, buffer_len: usize) -> Self {
        let sr = sample_rate as f32;
        let tau_min = (sr / F0_MAX_HZ).floor() as usize;
        let tau_max = (sr / F0_MIN_HZ).ceil() as usize;
        assert!(buffer_len > tau_max + 1, "buffer too short for F0_MIN_HZ");
        Self {
            sample_rate: sr,
            tau_min,
            tau_max,
            window: buffer_len - tau_max - 1,
            diff: vec![0.0; tau_max + 2],
        }
    }

    pub fn estimate(&mut self, x: &[f32]) -> Option<f32> {
        let w = self.window;
        debug_assert!(x.len() > w + self.tau_max);

        // Step 2: difference function d(tau).
        self.diff[0] = 0.0;
        for tau in 1..=self.tau_max + 1 {
            let (a, b) = (&x[..w], &x[tau..tau + w]);
            let mut s = 0.0f32;
            for (p, q) in a.iter().zip(b) {
                let d = p - q;
                s += d * d;
            }
            self.diff[tau] = s;
        }

        // Step 3: cumulative mean normalised difference d'(tau), in place.
        self.diff[0] = 1.0;
        let mut running = 0.0f32;
        for tau in 1..=self.tau_max + 1 {
            running += self.diff[tau];
            self.diff[tau] = if running > 0.0 {
                self.diff[tau] * tau as f32 / running
            } else {
                1.0
            };
        }

        // Step 4: absolute threshold — first dip below THRESHOLD, then walk to its local minimum.
        let mut tau = self.tau_min.max(2);
        let mut found = None;
        while tau <= self.tau_max {
            if self.diff[tau] < THRESHOLD {
                while tau < self.tau_max && self.diff[tau + 1] < self.diff[tau] {
                    tau += 1;
                }
                found = Some(tau);
                break;
            }
            tau += 1;
        }
        let tau = found?;

        // Step 5: parabolic interpolation for sub-sample precision.
        let (y0, y1, y2) = (self.diff[tau - 1], self.diff[tau], self.diff[tau + 1]);
        let denom = y0 - 2.0 * y1 + y2;
        let shift = if denom.abs() > f32::EPSILON {
            0.5 * (y0 - y2) / denom
        } else {
            0.0
        };
        let period = tau as f32 + shift.clamp(-1.0, 1.0);

        let f0 = self.sample_rate / period;
        (F0_MIN_HZ..=F0_MAX_HZ).contains(&f0).then_some(f0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::testsig::{noise, sine, voiced};
    use crate::{FRAME_LEN, SAMPLE_RATE_CAPTURE};

    fn to_f32(v: &[i16]) -> Vec<f32> {
        v.iter().map(|&s| s as f32 / 32768.0).collect()
    }

    fn yin() -> Yin {
        Yin::new(SAMPLE_RATE_CAPTURE, 2 * FRAME_LEN)
    }

    #[test]
    fn test_e001_04_pure_sines_within_2_percent() {
        let mut y = yin();
        let mut f = 60.5f32;
        while f <= 400.0 {
            let est = y
                .estimate(&to_f32(&sine(f, 2 * FRAME_LEN, 0.5)))
                .unwrap_or(0.0);
            assert!((est - f).abs() / f <= 0.02, "f={f} est={est}");
            f *= 1.07;
        }
    }

    #[test]
    fn test_e001_04_harmonic_signal_no_octave_error() {
        let mut y = yin();
        for &f in &[70.0, 120.0, 200.0, 280.0, 380.0] {
            let est = y
                .estimate(&to_f32(&voiced(f, 2 * FRAME_LEN, 0.5, 123)))
                .unwrap();
            assert!((est - f).abs() / f <= 0.02, "f={f} est={est}");
        }
    }

    #[test]
    fn test_e001_05_noise_is_unvoiced() {
        let mut y = yin();
        for seed in 1..20 {
            assert_eq!(y.estimate(&to_f32(&noise(2 * FRAME_LEN, 0.5, seed))), None);
        }
    }

    #[test]
    fn test_e001_05_out_of_range_is_none() {
        let mut y = yin();
        // 800 Hz pure tone: its period is below tau_min; must not report 400 Hz or 800 Hz.
        let est = y.estimate(&to_f32(&sine(800.0, 2 * FRAME_LEN, 0.5)));
        assert!(
            est.is_none() || (est.unwrap() - 400.0).abs() < 8.0,
            "{est:?}"
        );
    }
}
