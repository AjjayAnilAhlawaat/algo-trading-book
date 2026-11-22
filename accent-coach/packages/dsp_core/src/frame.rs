//! E001-03: frame RMS envelope in dBFS.

pub const DB_FLOOR: f32 = -120.0;

/// RMS level of i16 PCM in dBFS (full-scale sine ≈ -3 dB), floored at -120.
pub fn rms_db(pcm: &[i16]) -> f32 {
    if pcm.is_empty() {
        return DB_FLOOR;
    }
    let sum: f64 = pcm
        .iter()
        .map(|&s| {
            let x = s as f64 / 32768.0;
            x * x
        })
        .sum();
    to_db((sum / pcm.len() as f64).sqrt() as f32)
}

/// RMS level of normalised f32 samples in dBFS.
pub fn rms_db_f32(x: &[f32]) -> f32 {
    if x.is_empty() {
        return DB_FLOOR;
    }
    let sum: f32 = x.iter().map(|v| v * v).sum();
    to_db((sum / x.len() as f32).sqrt())
}

fn to_db(rms: f32) -> f32 {
    if rms <= 0.0 {
        DB_FLOOR
    } else {
        (20.0 * rms.log10()).max(DB_FLOOR)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::testsig::sine;
    use crate::FRAME_LEN;

    #[test]
    fn test_e001_03_silence_is_floor() {
        assert_eq!(rms_db(&[0; FRAME_LEN]), DB_FLOOR);
        assert_eq!(rms_db(&[]), DB_FLOOR);
    }

    #[test]
    fn test_e001_03_full_scale_sine_is_minus_3db() {
        let db = rms_db(&sine(1000.0, FRAME_LEN, 1.0));
        assert!((db + 3.01).abs() < 0.1, "db={db}");
    }

    #[test]
    fn test_e001_03_halving_amplitude_is_minus_6db() {
        let a = rms_db(&sine(500.0, FRAME_LEN, 0.5));
        let b = rms_db(&sine(500.0, FRAME_LEN, 0.25));
        assert!(((a - b) - 6.02).abs() < 0.1);
    }

    #[test]
    fn test_e001_03_i16_and_f32_agree() {
        let s = sine(300.0, FRAME_LEN, 0.3);
        let f: Vec<f32> = s.iter().map(|&v| v as f32 / 32768.0).collect();
        assert!((rms_db(&s) - rms_db_f32(&f)).abs() < 0.01);
    }
}
