//! E001-06: energy VAD with an adaptive noise floor and short hangover.

/// Speech must exceed the floor by this margin.
const MARGIN_DB: f32 = 10.0;
/// Floor never drops below this (digital silence would otherwise collapse it).
const MIN_FLOOR_DB: f32 = -90.0;
/// Floor adaptation while non-speech.
const ALPHA_QUIET: f32 = 0.05;
/// Slow creep during "speech" so sustained loud noise is eventually absorbed (~4–5 s).
const ALPHA_SPEECH: f32 = 0.003;
/// Frames of hangover after energy drops (4 × 20 ms = 80 ms).
const HANGOVER: u8 = 4;

pub struct Vad {
    floor_db: f32,
    hang: u8,
}

impl Vad {
    pub fn new(initial_floor_db: Option<f32>) -> Self {
        Self {
            floor_db: initial_floor_db.unwrap_or(-60.0).max(MIN_FLOOR_DB),
            hang: 0,
        }
    }

    pub fn floor_db(&self) -> f32 {
        self.floor_db
    }

    pub fn update(&mut self, rms_db: f32) -> bool {
        let level = rms_db.max(MIN_FLOOR_DB);
        let loud = level > self.floor_db + MARGIN_DB;

        if level < self.floor_db {
            self.floor_db = level; // fast attack downwards
        } else {
            let a = if loud { ALPHA_SPEECH } else { ALPHA_QUIET };
            self.floor_db += a * (level - self.floor_db);
        }

        if loud {
            self.hang = HANGOVER;
            true
        } else if self.hang > 0 {
            self.hang -= 1;
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_e001_06_speech_above_floor_detected() {
        let mut v = Vad::new(Some(-60.0));
        assert!(!v.update(-58.0));
        assert!(v.update(-30.0));
    }

    #[test]
    fn test_e001_06_hangover_then_release() {
        let mut v = Vad::new(Some(-60.0));
        assert!(v.update(-25.0));
        for _ in 0..HANGOVER {
            assert!(v.update(-60.0));
        }
        assert!(!v.update(-60.0));
    }

    #[test]
    fn test_e001_06_digital_silence_does_not_collapse_floor() {
        let mut v = Vad::new(None);
        for _ in 0..100 {
            v.update(-120.0);
        }
        assert_eq!(v.floor_db(), MIN_FLOOR_DB);
        assert!(!v.update(-85.0), "barely-above-silence must not be speech");
    }

    #[test]
    fn test_e001_06_sustained_noise_rise_is_absorbed() {
        let mut v = Vad::new(Some(-60.0));
        // Fan switches on: -40 dB constant for 8 s (400 frames).
        let decisions: Vec<bool> = (0..400).map(|_| v.update(-40.0)).collect();
        assert!(decisions[0], "sudden rise initially looks like speech");
        assert!(!decisions[399], "after 8 s the fan is the new floor");
        // Speech over the fan still detected.
        assert!(v.update(-20.0));
    }
}
