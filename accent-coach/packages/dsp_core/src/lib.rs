//! Accent Coach on-device DSP core.
//!
//! Contract: `specs/001-audio-engine/contracts/dsp_core_ffi.md` (frozen v1).
//! All per-frame work is allocation-free after `Analyzer::new`.

pub mod frame;
pub mod pitch;
pub mod resample;
pub mod vad;

pub const SAMPLE_RATE_CAPTURE: u32 = 48_000;
pub const SAMPLE_RATE_SCORING: u32 = 16_000;
/// 20 ms at 48 kHz.
pub const FRAME_LEN: usize = 960;
pub const F0_MIN_HZ: f32 = 60.0;
pub const F0_MAX_HZ: f32 = 400.0;
/// Used when calibration finds no voiced speech.
pub const DEFAULT_MEDIAN_F0_HZ: f32 = 150.0;

pub use resample::downsample_48k_to_16k;

/// Per-frame output streamed to the UI.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FrameFeatures {
    /// dBFS, floored at -120.
    pub rms_db: f32,
    pub is_speech: bool,
    /// `None` = unvoiced or silent. Never 0.0 (E001-05).
    pub f0_hz: Option<f32>,
    /// Relative to `Profile::median_f0_hz` (E001-08).
    pub semitones: Option<f32>,
}

/// Speaker/room calibration (E001-07).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Profile {
    pub noise_floor_db: f32,
    pub median_f0_hz: f32,
}

/// Stateful streaming analyser. Feed consecutive `FRAME_LEN` frames.
pub struct Analyzer {
    profile: Option<Profile>,
    vad: vad::Vad,
    yin: pitch::Yin,
    /// Last two frames as f32 (40 ms) so YIN has a window longer than the 60 Hz period.
    history: Vec<f32>,
}

impl Analyzer {
    pub fn new(profile: Option<Profile>) -> Self {
        let floor = profile.map(|p| p.noise_floor_db);
        Self {
            profile,
            vad: vad::Vad::new(floor),
            yin: pitch::Yin::new(SAMPLE_RATE_CAPTURE, 2 * FRAME_LEN),
            history: vec![0.0; 2 * FRAME_LEN],
        }
    }

    /// Process exactly one 20 ms frame of 48 kHz mono i16 PCM.
    ///
    /// # Panics
    /// If `pcm.len() != FRAME_LEN`.
    pub fn process_frame(&mut self, pcm: &[i16]) -> FrameFeatures {
        assert_eq!(pcm.len(), FRAME_LEN, "frame must be {FRAME_LEN} samples");

        // Shift history left by one frame, append new frame (no allocation).
        self.history.copy_within(FRAME_LEN.., 0);
        for (dst, &s) in self.history[FRAME_LEN..].iter_mut().zip(pcm) {
            *dst = s as f32 / 32768.0;
        }

        let rms_db = frame::rms_db_f32(&self.history[FRAME_LEN..]);
        let is_speech = self.vad.update(rms_db);

        let f0_hz = if is_speech {
            self.yin.estimate(&self.history)
        } else {
            None
        };
        let median = self
            .profile
            .map(|p| p.median_f0_hz)
            .unwrap_or(DEFAULT_MEDIAN_F0_HZ);
        let semitones = f0_hz.map(|f| hz_to_semitones(f, median));

        FrameFeatures {
            rms_db,
            is_speech,
            f0_hz,
            semitones,
        }
    }
}

/// E001-08: semitones relative to the speaker's median F0.
pub fn hz_to_semitones(f0_hz: f32, median_hz: f32) -> f32 {
    12.0 * (f0_hz / median_hz).log2()
}

/// E001-07: derive noise floor (median room-tone frame RMS) and median voiced F0.
pub fn calibrate(room_tone: &[i16], speech: &[i16]) -> Profile {
    let mut floors: Vec<f32> = room_tone
        .chunks_exact(FRAME_LEN)
        .map(frame::rms_db)
        .collect();
    let noise_floor_db = median(&mut floors).unwrap_or(-60.0);

    let mut analyzer = Analyzer::new(Some(Profile {
        noise_floor_db,
        median_f0_hz: DEFAULT_MEDIAN_F0_HZ,
    }));
    let mut f0s: Vec<f32> = speech
        .chunks_exact(FRAME_LEN)
        .filter_map(|f| analyzer.process_frame(f).f0_hz)
        .collect();
    let median_f0_hz = median(&mut f0s).unwrap_or(DEFAULT_MEDIAN_F0_HZ);

    Profile {
        noise_floor_db,
        median_f0_hz,
    }
}

fn median(v: &mut [f32]) -> Option<f32> {
    if v.is_empty() {
        return None;
    }
    v.sort_by(|a, b| a.total_cmp(b));
    let n = v.len();
    Some(if n % 2 == 1 {
        v[n / 2]
    } else {
        0.5 * (v[n / 2 - 1] + v[n / 2])
    })
}

#[cfg(test)]
pub(crate) mod testsig {
    use super::*;
    use std::f32::consts::TAU;

    /// Harmonic-rich voiced-like signal (5 harmonics, 1/k amplitude), i16.
    pub fn voiced(f0: f32, n: usize, amp: f32, phase0: usize) -> Vec<i16> {
        (0..n)
            .map(|i| {
                let t = (i + phase0) as f32 / SAMPLE_RATE_CAPTURE as f32;
                let s: f32 = (1..=5)
                    .map(|k| (TAU * f0 * k as f32 * t).sin() / k as f32)
                    .sum();
                (s * amp * 32767.0 / 2.3).clamp(-32768.0, 32767.0) as i16
            })
            .collect()
    }

    pub fn sine(f: f32, n: usize, amp: f32) -> Vec<i16> {
        (0..n)
            .map(|i| {
                ((TAU * f * i as f32 / SAMPLE_RATE_CAPTURE as f32).sin() * amp * 32767.0) as i16
            })
            .collect()
    }

    /// Deterministic white noise (xorshift), i16.
    pub fn noise(n: usize, amp: f32, seed: u32) -> Vec<i16> {
        let mut x = seed.max(1);
        (0..n)
            .map(|_| {
                x ^= x << 13;
                x ^= x >> 17;
                x ^= x << 5;
                let u = (x as f32 / u32::MAX as f32) * 2.0 - 1.0;
                (u * amp * 32767.0) as i16
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::testsig::*;
    use super::*;

    fn run(an: &mut Analyzer, sig: &[i16]) -> Vec<FrameFeatures> {
        sig.chunks_exact(FRAME_LEN)
            .map(|f| an.process_frame(f))
            .collect()
    }

    #[test]
    fn test_e001_04_f0_within_2_percent_end_to_end() {
        for &f0 in &[65.0f32, 98.0, 147.0, 220.0, 310.0, 392.0] {
            let floor = Profile {
                noise_floor_db: -70.0,
                median_f0_hz: 150.0,
            };
            let mut an = Analyzer::new(Some(floor));
            let out = run(&mut an, &voiced(f0, FRAME_LEN * 10, 0.5, 0));
            for ff in &out[2..] {
                let est = ff.f0_hz.expect("voiced frame must have f0");
                let err = (est - f0).abs() / f0;
                assert!(err <= 0.02, "f0={f0} est={est} err={err}");
            }
        }
    }

    #[test]
    fn test_e001_05_silence_and_noise_have_no_f0() {
        let mut an = Analyzer::new(None);
        for ff in run(&mut an, &vec![0i16; FRAME_LEN * 10]) {
            assert_eq!(ff.f0_hz, None);
            assert_eq!(ff.semitones, None);
        }
        let mut an = Analyzer::new(Some(Profile {
            noise_floor_db: -80.0,
            median_f0_hz: 150.0,
        }));
        let out = run(&mut an, &noise(FRAME_LEN * 10, 0.3, 7));
        // Loud white noise is "speech" to an energy VAD but must not yield a pitch.
        assert!(out.iter().all(|f| f.f0_hz.is_none()), "{out:?}");
    }

    #[test]
    fn test_e001_07_calibration_profile() {
        // Uniform noise, peak 0.003 → RMS 0.003/√3 ≈ -55.2 dBFS.
        let room = noise(FRAME_LEN * 150, 0.003, 3);
        let speech = voiced(180.0, FRAME_LEN * 250, 0.4, 0);
        let p = calibrate(&room, &speech);
        assert!((-56.5..=-54.0).contains(&p.noise_floor_db), "{p:?}");
        assert!((p.median_f0_hz - 180.0).abs() / 180.0 < 0.01, "{p:?}");
    }

    #[test]
    fn test_e001_07_calibration_without_voice_falls_back() {
        let p = calibrate(&vec![0; FRAME_LEN * 10], &vec![0; FRAME_LEN * 10]);
        assert_eq!(p.median_f0_hz, DEFAULT_MEDIAN_F0_HZ);
    }

    #[test]
    fn test_e001_08_semitones_relative_to_median() {
        assert!((hz_to_semitones(300.0, 150.0) - 12.0).abs() < 1e-4);
        assert!((hz_to_semitones(150.0, 150.0)).abs() < 1e-6);
        assert!((hz_to_semitones(75.0, 150.0) + 12.0).abs() < 1e-4);

        let mut an = Analyzer::new(Some(Profile {
            noise_floor_db: -70.0,
            median_f0_hz: 110.0,
        }));
        let out = run(&mut an, &voiced(220.0, FRAME_LEN * 5, 0.5, 0));
        let st = out[4].semitones.unwrap();
        assert!((st - 12.0).abs() < 0.35, "st={st}");
    }

    #[test]
    #[should_panic(expected = "frame must be")]
    fn wrong_frame_len_panics() {
        Analyzer::new(None).process_frame(&[0; 100]);
    }

    #[test]
    #[cfg_attr(
        debug_assertions,
        ignore = "perf budget only meaningful with --release"
    )]
    fn test_e001_12_frame_under_1ms_release() {
        let sig = voiced(140.0, FRAME_LEN * 500, 0.5, 0);
        let mut an = Analyzer::new(Some(Profile {
            noise_floor_db: -70.0,
            median_f0_hz: 140.0,
        }));
        let start = std::time::Instant::now();
        let mut voiced_frames = 0;
        for f in sig.chunks_exact(FRAME_LEN) {
            if an.process_frame(f).f0_hz.is_some() {
                voiced_frames += 1;
            }
        }
        let per_frame = start.elapsed().as_secs_f64() * 1000.0 / 500.0;
        assert!(voiced_frames > 490);
        assert!(per_frame < 1.0, "per-frame {per_frame:.3} ms");
    }
}
