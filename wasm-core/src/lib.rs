use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fast_happiness_calculation(
    gdp_per_capita: f64,
    social_support: f64,
    life_expectancy: f64,
) -> f64 {
    // Simulate a highly CPU-intensive mathematical calculation
    // done in WebAssembly at native speeds instead of JS
    let mut score = (gdp_per_capita.ln() * 0.4) + (social_support * 2.0) + (life_expectancy * 3.0);
    
    // Add some artificial complexity
    for i in 1..1000 {
        score += (i as f64).sin() * 0.0001;
    }
    
    score
}
